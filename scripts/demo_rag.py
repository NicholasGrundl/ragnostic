"""End-to-end RAG demo on the sample PDFs in data/.

Runs the full document flow (parse -> section -> chunk -> summarize -> embed ->
store) and then the query flow (two-tier retrieval -> section-coverage rerank),
all offline with the TF-IDF prototype embedder.

Usage:
    python scripts/demo_rag.py
    python scripts/demo_rag.py --data-dir data --limit 6 \
        --query "oxygen transfer in stirred tank bioreactors"

Switching to production backends (on a machine with network/keys):
    --embedder gemini   (needs GEMINI_API_KEY, pip install ragnostic[gemini])
    --embedder cohere   (needs CO_API_KEY,     pip install ragnostic[cohere])
    --parser docling    (pip install ragnostic[docling])
    --answer gemini     (LLM answer generation)
"""
import argparse
import logging
import tempfile
from pathlib import Path

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import DocumentCreate
from ragnostic.embeddings.tfidf import TfidfEmbedder
from ragnostic.ingestion.validation.checks import compute_file_hash
from ragnostic.pipeline import RagIndexer, build_query_pipeline
from ragnostic.utils import create_doc_id
from ragnostic.vectorstore.store import VectorStore

DEFAULT_QUERIES = [
    "oxygen transfer and aeration costs in stirred tank bioreactors",
    "supersaturation and crystal nucleation in industrial crystallization",
    "economics and cost estimation for process scale up",
]


def discover_pdfs(data_dir: Path, limit: int):
    pdfs = sorted(data_dir.rglob("*.pdf"))[:limit]
    if not pdfs:
        raise SystemExit(f"No PDFs found under {data_dir}")
    return pdfs


def register_documents(db_client: DatabaseClient, pdfs):
    """Insert minimal Document rows so the indexer can find the files.

    The real ingestion workflow does this with validation + blob storage; here
    we register the files in place to keep the demo self-contained.
    """
    doc_ids = []
    for pdf in pdfs:
        file_hash = compute_file_hash(pdf)
        existing = db_client.get_document_by_hash(file_hash)
        if existing:
            doc_ids.append(existing.id)
            continue
        doc_id = create_doc_id(prefix="DOC")
        db_client.create_document(
            DocumentCreate(
                id=doc_id,
                raw_file_path=str(pdf.resolve()),
                file_hash=file_hash,
                file_size_bytes=pdf.stat().st_size,
                mime_type="application/pdf",
            )
        )
        # Use the filename as a human-readable title for tier-1 search.
        from ragnostic.db.schema import DocumentMetadataCreate

        db_client.create_metadata(
            DocumentMetadataCreate(doc_id=doc_id, title=pdf.stem)
        )
        doc_ids.append(doc_id)
    return doc_ids


def build_embedder(name: str):
    if name == "tfidf":
        return TfidfEmbedder()
    if name == "gemini":
        from ragnostic.embeddings.api import GeminiEmbedder

        return GeminiEmbedder()
    if name == "cohere":
        from ragnostic.embeddings.api import CohereEmbedder

        return CohereEmbedder()
    if name == "fastembed":
        from ragnostic.embeddings.api import FastEmbedEmbedder

        return FastEmbedEmbedder()
    raise SystemExit(f"Unknown embedder: {name}")


def build_parser(name: str):
    if name == "pymupdf":
        from ragnostic.extraction.pymupdf_parser import PyMuPDFParser

        return PyMuPDFParser()
    if name == "docling":
        from ragnostic.extraction.docling_parser import DoclingParser

        return DoclingParser()
    raise SystemExit(f"Unknown parser: {name}")


def build_answer_fn(name: str):
    if name == "none":
        return None
    if name == "gemini":
        from ragnostic.query.answer import make_gemini_answer_fn

        return make_gemini_answer_fn()
    if name == "anthropic":
        from ragnostic.query.answer import make_anthropic_answer_fn

        return make_anthropic_answer_fn()
    raise SystemExit(f"Unknown answer backend: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--limit", type=int, default=6, help="Max PDFs to index")
    parser.add_argument("--embedder", default="tfidf",
                        choices=["tfidf", "gemini", "cohere", "fastembed"])
    parser.add_argument("--parser", default="pymupdf", choices=["pymupdf", "docling"])
    parser.add_argument("--answer", default="none", choices=["none", "gemini", "anthropic"])
    parser.add_argument("--query", action="append", help="Query (repeatable)")
    parser.add_argument("--workdir", default=None,
                        help="Persist dir for the DB + vector store (default: temp dir)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    workdir = Path(args.workdir) if args.workdir else Path(tempfile.mkdtemp(prefix="ragnostic_demo_"))
    workdir.mkdir(parents=True, exist_ok=True)
    db_path = workdir / "ragnostic.db"
    persist_dir = workdir / "chroma"

    db_client = DatabaseClient(f"sqlite:///{db_path}")
    vector_store = VectorStore(persist_dir)

    pdfs = discover_pdfs(Path(args.data_dir), args.limit)
    print(f"\n=== Document flow: indexing {len(pdfs)} PDFs from {args.data_dir} ===")
    for pdf in pdfs:
        print(f"  - {pdf.name}")

    register_documents(db_client, pdfs)

    embedder = build_embedder(args.embedder)
    indexer = RagIndexer(
        db_client=db_client,
        vector_store=vector_store,
        embedder=embedder,
        parser=build_parser(args.parser),
    )

    print("\nParsing, chunking, summarizing...")
    for stats in indexer.process_all():
        flag = "ok" if stats.error is None else f"ERROR: {stats.error}"
        print(f"  {stats.doc_id}: {stats.n_sections} sections, {stats.n_chunks} chunks [{flag}]")

    index_stats = indexer.build_vector_index()
    print(f"\nVector index built: {index_stats.n_documents} summaries, "
          f"{index_stats.n_chunks} chunks (embedder={index_stats.embedder})")

    # Query flow: reuse the indexed embedder (TF-IDF is loaded from disk).
    query_embedder = None if args.embedder == "tfidf" else embedder
    pipeline = build_query_pipeline(
        db_client, persist_dir, embedder=query_embedder, answer_fn=build_answer_fn(args.answer)
    )

    queries = args.query or DEFAULT_QUERIES
    for query in queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)
        result = pipeline.query(query, top_docs=3, final_chunks=4,
                                generate_answer=(args.answer != "none"))

        print("\nTier-1 documents (by summary):")
        for doc in result.documents:
            print(f"  [{doc.score:.3f}] {doc.title or doc.doc_id}")

        print("\nTier-2 chunks (after section-coverage rerank):")
        for i, chunk in enumerate(result.chunks, start=1):
            preview = " ".join(chunk.text.split())[:160]
            print(f"  {i}. [rerank={chunk.rerank_score:.3f} sim={chunk.score:.3f} "
                  f"cov={chunk.section_coverage:.2f}] "
                  f"{chunk.section_title or chunk.section_id}")
            print(f"     {preview}...")

        if result.answer:
            print("\nAnswer:")
            print("  " + result.answer.replace("\n", "\n  "))

    print(f"\nArtifacts kept in: {workdir}")


if __name__ == "__main__":
    main()
