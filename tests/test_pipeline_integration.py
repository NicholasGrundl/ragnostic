"""End-to-end integration test for the RAG MVP using synthetic documents.

Exercises the full document + query flow without any PDF parsing or network:
sections -> chunks -> summary -> TF-IDF embeddings -> ChromaDB -> two-tier
query -> section-coverage rerank.
"""
import datetime

import pytest

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import DocumentCreate, DocumentMetadataCreate
from ragnostic.embeddings.tfidf import TfidfEmbedder
from ragnostic.extraction.persist import persist_parsed_document
from ragnostic.extraction.schema import ParsedDocument, ParsedSection
from ragnostic.pipeline import RagIndexer, build_query_pipeline
from ragnostic.vectorstore.store import VectorStore

DOCS = {
    "DOC_AERATION": {
        "title": "Aeration Costs in Stirred Tank Bioreactors",
        "sections": [
            ("Introduction", "Aeration drives oxygen transfer in aerobic fermentation. "
                             "Oxygen transfer rate depends on the volumetric mass transfer coefficient kLa."),
            ("Power Consumption", "Stirred tank bioreactors consume significant power for agitation "
                                  "and compressed air sparging. Energy costs scale with reactor volume "
                                  "and required oxygen uptake rate of the culture."),
        ],
    },
    "DOC_CRYSTAL": {
        "title": "Industrial Crystallization Fundamentals",
        "sections": [
            ("Nucleation", "Crystallization begins with nucleation governed by supersaturation. "
                           "Primary and secondary nucleation mechanisms control crystal number."),
            ("Crystal Growth", "Crystal growth rate depends on supersaturation and temperature. "
                               "Particle size distribution is controlled by residence time and cooling profile."),
        ],
    },
}


@pytest.fixture
def db_client():
    return DatabaseClient("sqlite:///:memory:")


def _seed_document(db_client, doc_id, spec):
    db_client.create_document(
        DocumentCreate(
            id=doc_id,
            raw_file_path=f"/tmp/{doc_id}.pdf",
            file_hash=doc_id,  # unique per doc
            file_size_bytes=1000,
            mime_type="application/pdf",
        )
    )
    db_client.create_metadata(
        DocumentMetadataCreate(doc_id=doc_id, title=spec["title"], page_count=2)
    )
    parsed = ParsedDocument(
        doc_id=doc_id,
        sections=[ParsedSection(title=t, text=c, level=1) for t, c in spec["sections"]],
    )
    persist_parsed_document(db_client, parsed)


@pytest.fixture
def indexed(db_client, tmp_path):
    for doc_id, spec in DOCS.items():
        _seed_document(db_client, doc_id, spec)

    persist_dir = tmp_path / "chroma"
    vector_store = VectorStore(persist_dir)
    indexer = RagIndexer(
        db_client=db_client,
        vector_store=vector_store,
        embedder=TfidfEmbedder(max_features=256),
        chunk_words=40,
        overlap_words=10,
    )
    indexer.process_all()
    stats = indexer.build_vector_index()
    return persist_dir, stats


@pytest.mark.integration
def test_full_index_builds(db_client, indexed):
    _, stats = indexed
    assert stats.n_documents == 2
    assert stats.n_chunks > 0
    assert stats.embedder == "tfidf"
    # chunks and summaries persisted in the relational DB too
    assert db_client.get_summary("DOC_AERATION") is not None
    assert len(db_client.get_document_chunks("DOC_CRYSTAL")) > 0


@pytest.mark.integration
def test_query_retrieves_relevant_document(db_client, indexed):
    persist_dir, _ = indexed
    pipeline = build_query_pipeline(db_client, persist_dir)

    result = pipeline.query("oxygen transfer and aeration power costs", top_docs=2, final_chunks=4)
    assert result.documents
    assert result.documents[0].doc_id == "DOC_AERATION"
    assert result.chunks
    # top chunk should come from the aeration document
    assert result.chunks[0].doc_id == "DOC_AERATION"
    assert result.context


@pytest.mark.integration
def test_query_other_topic(db_client, indexed):
    persist_dir, _ = indexed
    pipeline = build_query_pipeline(db_client, persist_dir)
    result = pipeline.query("supersaturation and crystal nucleation", top_docs=2)
    assert result.documents[0].doc_id == "DOC_CRYSTAL"


@pytest.mark.integration
def test_answer_fn_invoked_when_enabled(db_client, indexed):
    persist_dir, _ = indexed
    captured = {}

    def fake_answer(query, context):
        captured["query"] = query
        captured["context"] = context
        return "stub answer"

    pipeline = build_query_pipeline(db_client, persist_dir, answer_fn=fake_answer)
    result = pipeline.query("aeration", generate_answer=True)
    assert result.answer == "stub answer"
    assert captured["query"] == "aeration"
    assert captured["context"]
