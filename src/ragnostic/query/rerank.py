"""Section-coverage reranking.

Per the project plan: sections with several retrieved chunks are likely the
truly relevant passages, so chunks are rescored by combining their own
similarity with their section's "chunk coverage"
(chunks retrieved from section / total chunks in section).
"""
import logging
from collections import defaultdict
from typing import Callable, List

from .schema import ChunkMatch

logger = logging.getLogger(__name__)

DEFAULT_COVERAGE_WEIGHT = 0.3


def rerank_by_section_coverage(
    chunks: List[ChunkMatch],
    section_chunk_counts: Callable[[str], int],
    coverage_weight: float = DEFAULT_COVERAGE_WEIGHT,
) -> List[ChunkMatch]:
    """Rescore and reorder chunk matches using section coverage.

    rerank_score = (1 - w) * similarity + w * section_coverage

    Args:
        chunks: Chunk matches from vector search.
        section_chunk_counts: Callable returning total chunk count for a section_id.
        coverage_weight: Weight w in [0, 1] for the coverage term.

    Returns:
        New list sorted by rerank_score descending.
    """
    hits_per_section: dict = defaultdict(int)
    for chunk in chunks:
        if chunk.section_id:
            hits_per_section[chunk.section_id] += 1

    reranked = []
    for chunk in chunks:
        coverage = 0.0
        if chunk.section_id:
            total = section_chunk_counts(chunk.section_id)
            if total > 0:
                coverage = hits_per_section[chunk.section_id] / total
        updated = chunk.model_copy(
            update={
                "section_coverage": coverage,
                "rerank_score": (1 - coverage_weight) * chunk.score + coverage_weight * coverage,
            }
        )
        reranked.append(updated)

    reranked.sort(key=lambda c: c.rerank_score, reverse=True)
    return reranked
