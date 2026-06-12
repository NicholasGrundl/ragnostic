"""Query package: two-tier retrieval and optional answer generation."""
from .answer import make_anthropic_answer_fn, make_gemini_answer_fn
from .pipeline import QueryPipeline
from .rerank import rerank_by_section_coverage
from .schema import ChunkMatch, DocumentMatch, QueryResult

__all__ = [
    "QueryPipeline",
    "QueryResult",
    "DocumentMatch",
    "ChunkMatch",
    "rerank_by_section_coverage",
    "make_gemini_answer_fn",
    "make_anthropic_answer_fn",
]
