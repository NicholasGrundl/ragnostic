"""Two-tier query pipeline: summary search -> filtered chunk search -> rerank."""
import logging
from functools import lru_cache
from typing import Callable, List, Optional

from ragnostic.db.client import DatabaseClient
from ragnostic.embeddings.base import EmbeddingProvider
from ragnostic.vectorstore.store import VectorStore

from .rerank import DEFAULT_COVERAGE_WEIGHT, rerank_by_section_coverage
from .schema import ChunkMatch, DocumentMatch, QueryResult

logger = logging.getLogger(__name__)


class QueryPipeline:
    """Runs the two-tier retrieval flow from the project plan.

    1. Embed the query.
    2. Search the summary collection for the top-N candidate documents.
    3. Search the chunk collection filtered to those documents.
    4. Rerank chunks by section coverage.
    5. Assemble a context block (and optionally an LLM answer).
    """

    def __init__(
        self,
        db_client: DatabaseClient,
        vector_store: VectorStore,
        embedder: EmbeddingProvider,
        answer_fn: Optional[Callable[[str, str], str]] = None,
    ):
        """
        Args:
            answer_fn: Optional LLM generation hook with signature
                (query, context) -> answer. Retrieval works without it.
        """
        self.db_client = db_client
        self.vector_store = vector_store
        self.embedder = embedder
        self.answer_fn = answer_fn

    def query(
        self,
        text: str,
        top_docs: int = 5,
        top_chunks: int = 20,
        final_chunks: int = 8,
        coverage_weight: float = DEFAULT_COVERAGE_WEIGHT,
        generate_answer: bool = False,
    ) -> QueryResult:
        """Run a query through the two-tier pipeline."""
        query_embedding = self.embedder.embed_query(text)

        # Tier 1: document search over summaries
        summary_hits = self.vector_store.search_summaries(query_embedding, n_results=top_docs)
        documents = []
        for hit in summary_hits:
            metadata = self.db_client.get_metadata(hit.id)
            documents.append(
                DocumentMatch(
                    doc_id=hit.id,
                    score=hit.score,
                    title=metadata.title if metadata else None,
                    summary=hit.document,
                )
            )
        doc_ids = [d.doc_id for d in documents]
        if not doc_ids:
            logger.warning("No documents matched query; is the index empty?")
            return QueryResult(query=text)

        # Tier 2: chunk search filtered to candidate documents
        chunk_hits = self.vector_store.search_chunks(
            query_embedding, n_results=top_chunks, doc_ids=doc_ids
        )
        chunks = [
            ChunkMatch(
                chunk_id=hit.id,
                doc_id=hit.metadata.get("doc_id", ""),
                section_id=hit.metadata.get("section_id") or None,
                score=hit.score,
                text=hit.document or "",
            )
            for hit in chunk_hits
        ]

        # Rerank by section coverage
        @lru_cache(maxsize=256)
        def section_total(section_id: str) -> int:
            return self.db_client.count_section_chunks(section_id)

        chunks = rerank_by_section_coverage(chunks, section_total, coverage_weight)
        chunks = chunks[:final_chunks]
        chunks = self._attach_section_titles(chunks)

        context = self._assemble_context(documents, chunks)

        answer = None
        if generate_answer:
            if self.answer_fn is None:
                logger.warning("generate_answer=True but no answer_fn configured; skipping")
            else:
                answer = self.answer_fn(text, context)

        return QueryResult(
            query=text,
            documents=documents,
            chunks=chunks,
            context=context,
            answer=answer,
        )

    def _attach_section_titles(self, chunks: List[ChunkMatch]) -> List[ChunkMatch]:
        sections_by_doc: dict = {}
        updated = []
        for chunk in chunks:
            if not chunk.section_id:
                updated.append(chunk)
                continue
            if chunk.doc_id not in sections_by_doc:
                sections_by_doc[chunk.doc_id] = {
                    s.section_id: (s.content.title if s.content else None)
                    for s in self.db_client.get_document_sections(chunk.doc_id)
                }
            title = sections_by_doc[chunk.doc_id].get(chunk.section_id)
            updated.append(chunk.model_copy(update={"section_title": title}))
        return updated

    @staticmethod
    def _assemble_context(documents: List[DocumentMatch], chunks: List[ChunkMatch]) -> str:
        """Build an LLM-ready context block from ranked chunks."""
        titles = {d.doc_id: d.title or d.doc_id for d in documents}
        parts = []
        for i, chunk in enumerate(chunks, start=1):
            source = titles.get(chunk.doc_id, chunk.doc_id)
            section = f" / {chunk.section_title}" if chunk.section_title else ""
            parts.append(f"[{i}] ({source}{section})\n{chunk.text}")
        return "\n\n---\n\n".join(parts)
