"""Tests for section-coverage reranking."""
import pytest

from ragnostic.query.rerank import rerank_by_section_coverage
from ragnostic.query.schema import ChunkMatch


def _chunk(chunk_id, section_id, score):
    return ChunkMatch(
        chunk_id=chunk_id, doc_id="DOC_1", section_id=section_id, score=score, text="x"
    )


@pytest.mark.unit
def test_coverage_boosts_well_covered_section():
    # Section A: 2 of 2 chunks retrieved (coverage 1.0)
    # Section B: 1 of 10 chunks retrieved (coverage 0.1)
    chunks = [
        _chunk("c1", "A", 0.50),
        _chunk("c2", "A", 0.48),
        _chunk("c3", "B", 0.60),
    ]
    totals = {"A": 2, "B": 10}
    reranked = rerank_by_section_coverage(chunks, lambda s: totals[s], coverage_weight=0.5)

    by_id = {c.chunk_id: c for c in reranked}
    assert by_id["c1"].section_coverage == pytest.approx(1.0)
    assert by_id["c3"].section_coverage == pytest.approx(0.1)
    # c1: 0.5*0.5 + 0.5*1.0 = 0.75 beats c3: 0.5*0.6 + 0.5*0.1 = 0.35
    assert reranked[0].chunk_id == "c1"


@pytest.mark.unit
def test_sorted_descending_by_rerank_score():
    chunks = [_chunk("c1", "A", 0.2), _chunk("c2", "A", 0.9)]
    reranked = rerank_by_section_coverage(chunks, lambda s: 2, coverage_weight=0.3)
    scores = [c.rerank_score for c in reranked]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.unit
def test_chunks_without_section_get_zero_coverage():
    chunks = [_chunk("c1", None, 0.5)]
    reranked = rerank_by_section_coverage(chunks, lambda s: 0, coverage_weight=0.3)
    assert reranked[0].section_coverage == 0.0
    assert reranked[0].rerank_score == pytest.approx(0.7 * 0.5)
