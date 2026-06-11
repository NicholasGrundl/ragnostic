"""Tests for the ChromaDB two-tier vector store."""
import pytest

from ragnostic.vectorstore.store import VectorStore


@pytest.fixture
def store(tmp_path):
    return VectorStore(tmp_path / "chroma")


@pytest.mark.integration
def test_summary_search_returns_nearest(store):
    store.upsert_summaries(
        doc_ids=["DOC_A", "DOC_B"],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        summaries=["about aeration", "about crystals"],
    )
    hits = store.search_summaries([0.9, 0.1], n_results=2)
    assert hits[0].id == "DOC_A"
    assert hits[0].score > hits[1].score


@pytest.mark.integration
def test_chunk_search_filters_by_doc_ids(store):
    store.upsert_chunks(
        chunk_ids=["c1", "c2", "c3"],
        embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]],
        texts=["t1", "t2", "t3"],
        doc_ids=["DOC_A", "DOC_B", "DOC_A"],
        section_ids=["S1", "S2", "S3"],
    )
    hits = store.search_chunks([1.0, 0.0], n_results=10, doc_ids=["DOC_B"])
    assert {h.id for h in hits} == {"c2"}


@pytest.mark.integration
def test_empty_collections_return_empty(store):
    assert store.search_summaries([1.0, 0.0]) == []
    assert store.search_chunks([1.0, 0.0]) == []


@pytest.mark.integration
def test_delete_document_removes_chunks(store):
    store.upsert_chunks(
        chunk_ids=["c1", "c2"],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        texts=["t1", "t2"],
        doc_ids=["DOC_A", "DOC_B"],
        section_ids=["S1", "S2"],
    )
    store.delete_document("DOC_A")
    hits = store.search_chunks([1.0, 0.0], n_results=10)
    assert {h.id for h in hits} == {"c2"}
