"""Tests for the TF-IDF embedding provider."""
import pytest

from ragnostic.embeddings.tfidf import TfidfEmbedder

CORPUS = [
    "bioreactor aeration and oxygen transfer in stirred tanks",
    "crystallization kinetics and supersaturation control",
    "heavy oil hydrocracking catalyst performance",
]


@pytest.mark.unit
def test_requires_fit_before_embed():
    embedder = TfidfEmbedder(max_features=64)
    with pytest.raises(RuntimeError):
        embedder.embed_query("anything")


@pytest.mark.unit
def test_fixed_dimension_output():
    embedder = TfidfEmbedder(max_features=64).fit(CORPUS)
    vectors = embedder.embed_documents(CORPUS)
    assert all(len(v) == 64 for v in vectors)
    assert len(embedder.embed_query("oxygen transfer")) == 64


@pytest.mark.unit
def test_query_matches_related_document():
    embedder = TfidfEmbedder(max_features=128).fit(CORPUS)
    docs = embedder.embed_documents(CORPUS)
    q = embedder.embed_query("oxygen transfer aeration")

    def cosine(a, b):
        import numpy as np

        a, b = np.array(a), np.array(b)
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
        return float(a @ b / denom)

    scores = [cosine(q, d) for d in docs]
    assert scores.index(max(scores)) == 0  # bioreactor/aeration doc


@pytest.mark.unit
def test_save_and_load_roundtrip(tmp_path):
    embedder = TfidfEmbedder(max_features=64).fit(CORPUS)
    embedder.save(tmp_path)
    loaded = TfidfEmbedder.load(tmp_path)
    assert loaded.embed_query("crystallization") == pytest.approx(
        embedder.embed_query("crystallization")
    )
