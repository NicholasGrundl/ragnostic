"""Schemas for query results."""
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentMatch(BaseModel):
    """Tier-1 result: a document matched by summary similarity."""
    doc_id: str
    score: float
    title: Optional[str] = None
    summary: Optional[str] = None


class ChunkMatch(BaseModel):
    """Tier-2 result: a chunk matched within candidate documents."""
    chunk_id: str
    doc_id: str
    section_id: Optional[str] = None
    score: float = Field(description="Cosine similarity from vector search")
    rerank_score: float = Field(default=0.0, description="Score after section-coverage reranking")
    section_title: Optional[str] = None
    section_coverage: float = Field(
        default=0.0,
        description="Fraction of the chunk's section retrieved: hits_in_section / chunks_in_section",
    )
    text: str


class QueryResult(BaseModel):
    """Full two-tier query result."""
    query: str
    documents: List[DocumentMatch] = Field(default_factory=list)
    chunks: List[ChunkMatch] = Field(default_factory=list, description="Reranked, best first")
    context: str = Field(default="", description="Assembled context for LLM consumption")
    answer: Optional[str] = Field(default=None, description="LLM answer when generation is enabled")
