"""End-to-end orchestration for the RAG MVP.

Two halves, mirroring the project plan:

- RagIndexer: ingested document -> sections -> chunks -> summary -> embeddings
  -> vector store (document flow).
- build_query_pipeline: load the persisted embedder + vector store into a
  QueryPipeline (query flow).

Corpus-fitted embedders like TfidfEmbedder must see the whole corpus before
embedding, so vector indexing is a separate batch step (build_vector_index)
after documents are processed. API embedders don't need the fit, but the
batch step keeps both paths identical.
"""
import logging
from pathlib import Path
from typing import Callable, List, Optional

from pydantic import BaseModel, Field

from ragnostic.db.client import DatabaseClient
from ragnostic.embeddings.base import EmbeddingProvider
from ragnostic.embeddings.tfidf import TfidfEmbedder
from ragnostic.extraction.base import DocumentParser
from ragnostic.extraction.persist import persist_parsed_document
from ragnostic.extraction.pymupdf_parser import PyMuPDFParser
from ragnostic.query.pipeline import QueryPipeline
from ragnostic.semantic.chunking import (
    DEFAULT_CHUNK_WORDS,
    DEFAULT_OVERLAP_WORDS,
    chunk_document,
)
from ragnostic.semantic.summarize import Summarizer, summarize_document
from ragnostic.vectorstore.store import VectorStore

logger = logging.getLogger(__name__)


class DocumentIndexStats(BaseModel):
    """Per-document semantic processing outcome."""
    doc_id: str
    n_sections: int = 0
    n_chunks: int = 0
    summarized: bool = False
    error: Optional[str] = None


class VectorIndexStats(BaseModel):
    """Vector index build outcome."""
    n_documents: int = 0
    n_chunks: int = 0
    embedder: str = Field(default="unknown")


class RagIndexer:
    """Processes ingested documents into the searchable two-tier index."""

    def __init__(
        self,
        db_client: DatabaseClient,
        vector_store: VectorStore,
        embedder: Optional[EmbeddingProvider] = None,
        parser: Optional[DocumentParser] = None,
        summarizer: Optional[Summarizer] = None,
        chunk_words: int = DEFAULT_CHUNK_WORDS,
        overlap_words: int = DEFAULT_OVERLAP_WORDS,
    ):
        self.db_client = db_client
        self.vector_store = vector_store
        self.embedder = embedder if embedder is not None else TfidfEmbedder()
        self.parser = parser if parser is not None else PyMuPDFParser()
        self.summarizer = summarizer
        self.chunk_words = chunk_words
        self.overlap_words = overlap_words

    def process_document(self, doc_id: str) -> DocumentIndexStats:
        """Parse, section, chunk, and summarize one ingested document."""
        stats = DocumentIndexStats(doc_id=doc_id)
        try:
            document = self.db_client.get_document_by_id(doc_id)
            if document is None:
                stats.error = f"Document {doc_id} not found in database"
                return stats

            sections = self.db_client.get_document_sections(doc_id)
            if not sections:
                parsed = self.parser.parse(Path(document.raw_file_path), doc_id)
                sections = persist_parsed_document(self.db_client, parsed)
            stats.n_sections = len(sections)

            chunks = self.db_client.get_document_chunks(doc_id)
            if not chunks:
                chunks = chunk_document(
                    self.db_client,
                    doc_id,
                    chunk_words=self.chunk_words,
                    overlap_words=self.overlap_words,
                    sections=sections,
                )
            stats.n_chunks = len(chunks)

            summarize_document(self.db_client, doc_id, summarizer=self.summarizer)
            stats.summarized = True
        except Exception as e:
            logger.exception("Semantic processing failed for %s", doc_id)
            stats.error = str(e)
        return stats

    def process_all(self, limit: int = 1000) -> List[DocumentIndexStats]:
        """Process every document in the library (idempotent per document)."""
        documents = self.db_client.get_documents(limit=limit)
        return [self.process_document(d.id) for d in documents]

    def build_vector_index(self, limit: int = 1000) -> VectorIndexStats:
        """Embed all summaries and chunks and upsert them into the vector store.

        Fits corpus-based embedders (TF-IDF) on the full corpus first and
        persists the fitted state next to the vector store so queries can
        load it.
        """
        documents = self.db_client.get_documents(limit=limit)

        summary_ids: List[str] = []
        summary_texts: List[str] = []
        chunk_records = []
        for document in documents:
            summary = self.db_client.get_summary(document.id)
            if summary is None:
                logger.warning("Skipping %s: no summary (run process_document first)", document.id)
                continue
            summary_ids.append(document.id)
            summary_texts.append(summary.summary)
            chunk_records.extend(self.db_client.get_document_chunks(document.id))

        if not summary_ids:
            logger.warning("Nothing to index: no processed documents found")
            return VectorIndexStats(embedder=getattr(self.embedder, "name", "unknown"))

        chunk_texts = [c.text for c in chunk_records]

        if hasattr(self.embedder, "fit"):
            self.embedder.fit(summary_texts + chunk_texts)
        if hasattr(self.embedder, "save"):
            self.embedder.save(self.vector_store.persist_dir)

        self.vector_store.upsert_summaries(
            doc_ids=summary_ids,
            embeddings=self.embedder.embed_documents(summary_texts),
            summaries=summary_texts,
        )
        if chunk_records:
            self.vector_store.upsert_chunks(
                chunk_ids=[c.chunk_id for c in chunk_records],
                embeddings=self.embedder.embed_documents(chunk_texts),
                texts=chunk_texts,
                doc_ids=[c.doc_id for c in chunk_records],
                section_ids=[c.section_id for c in chunk_records],
            )

        return VectorIndexStats(
            n_documents=len(summary_ids),
            n_chunks=len(chunk_records),
            embedder=getattr(self.embedder, "name", "unknown"),
        )


def build_query_pipeline(
    db_client: DatabaseClient,
    persist_dir: str | Path,
    embedder: Optional[EmbeddingProvider] = None,
    answer_fn: Optional[Callable[[str, str], str]] = None,
) -> QueryPipeline:
    """Construct a QueryPipeline against an existing vector index.

    When no embedder is given, loads the fitted TfidfEmbedder persisted by
    build_vector_index. Pass the same API embedder used at indexing time
    otherwise.
    """
    vector_store = VectorStore(persist_dir)
    if embedder is None:
        embedder = TfidfEmbedder.load(Path(persist_dir))
    return QueryPipeline(
        db_client=db_client,
        vector_store=vector_store,
        embedder=embedder,
        answer_fn=answer_fn,
    )
