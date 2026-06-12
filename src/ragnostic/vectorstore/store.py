"""Two-tier ChromaDB vector store: document summaries and chunks.

Embeddings are always precomputed by an EmbeddingProvider and passed in —
Chroma's built-in embedding functions are never used, so the store works
offline and stays backend-agnostic.
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

SUMMARY_COLLECTION = "doc_summaries"
CHUNK_COLLECTION = "doc_chunks"


class VectorHit(BaseModel):
    """A single search hit from a vector collection."""
    id: str
    score: float = Field(description="Cosine similarity in [0, 1], higher is better")
    document: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class VectorStore:
    """Persistent ChromaDB store with summary and chunk collections."""

    def __init__(self, persist_dir: str | Path):
        import chromadb

        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.summaries = self.client.get_or_create_collection(
            SUMMARY_COLLECTION, metadata={"hnsw:space": "cosine"}
        )
        self.chunks = self.client.get_or_create_collection(
            CHUNK_COLLECTION, metadata={"hnsw:space": "cosine"}
        )

    def upsert_summaries(
        self,
        doc_ids: List[str],
        embeddings: List[List[float]],
        summaries: List[str],
    ) -> None:
        """Store document summary vectors keyed by doc_id."""
        self.summaries.upsert(
            ids=doc_ids,
            embeddings=embeddings,
            documents=summaries,
            metadatas=[{"doc_id": d} for d in doc_ids],
        )

    def upsert_chunks(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        texts: List[str],
        doc_ids: List[str],
        section_ids: List[Optional[str]],
    ) -> None:
        """Store chunk vectors with doc/section metadata for filtering."""
        metadatas = [
            {"doc_id": d, "section_id": s or ""}
            for d, s in zip(doc_ids, section_ids)
        ]
        self.chunks.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

    @staticmethod
    def _to_hits(result) -> List[VectorHit]:
        hits = []
        ids = result["ids"][0]
        distances = result["distances"][0]
        documents = (result.get("documents") or [[None] * len(ids)])[0]
        metadatas = (result.get("metadatas") or [[{}] * len(ids)])[0]
        for id_, dist, doc, meta in zip(ids, distances, documents, metadatas):
            hits.append(
                VectorHit(
                    id=id_,
                    score=1.0 - dist,  # cosine distance -> similarity
                    document=doc,
                    metadata=meta or {},
                )
            )
        return hits

    def search_summaries(self, query_embedding: List[float], n_results: int = 5) -> List[VectorHit]:
        """Tier-1 search: find relevant documents by summary."""
        count = self.summaries.count()
        if count == 0:
            return []
        result = self.summaries.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count),
        )
        return self._to_hits(result)

    def search_chunks(
        self,
        query_embedding: List[float],
        n_results: int = 20,
        doc_ids: Optional[List[str]] = None,
    ) -> List[VectorHit]:
        """Tier-2 search: find relevant chunks, optionally filtered to doc_ids."""
        count = self.chunks.count()
        if count == 0:
            return []
        where = None
        if doc_ids:
            where = {"doc_id": {"$in": doc_ids}} if len(doc_ids) > 1 else {"doc_id": doc_ids[0]}
        result = self.chunks.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count),
            where=where,
        )
        return self._to_hits(result)

    def delete_document(self, doc_id: str) -> None:
        """Remove a document's summary and chunks from both collections."""
        self.summaries.delete(ids=[doc_id])
        self.chunks.delete(where={"doc_id": doc_id})
