# MVP RAG Pipeline

This document describes the end-to-end RAG MVP that connects every stage of the
hierarchical retrieval system into a single demoable pipeline, as outlined in
`docs/2_Ragnostic_Project_Plan.md`.

## What the MVP delivers

A two-tier hierarchical RAG system:

```
Document flow:  PDF -> parse -> sections -> chunks -> summary -> embeddings -> ChromaDB
Query flow:     query -> embed -> summary search (tier 1) -> filtered chunk search (tier 2)
                      -> section-coverage rerank -> assembled context -> (optional) LLM answer
```

The pipeline runs fully offline with no API keys via prototype backends, and
every external-model touchpoint is swappable for a production backend.

## Pluggable backends

Because model weights cannot always be downloaded (e.g. restricted networks),
each model touchpoint has a keyless/offline default plus production options:

| Concern    | Default (offline)                  | Production options                          |
|------------|------------------------------------|---------------------------------------------|
| PDF parse  | `PyMuPDFParser` (pymupdf4llm)      | `DoclingParser` (`pip install ragnostic[docling]`) |
| Embeddings | `TfidfEmbedder` (scikit-learn)     | `GeminiEmbedder`, `CohereEmbedder`, `FastEmbedEmbedder` |
| Summaries  | `ExtractiveSummarizer`             | `LLMSummarizer` (Gemini/Anthropic/OpenAI)   |
| Answers    | none (retrieval-first)             | `make_gemini_answer_fn`, `make_anthropic_answer_fn` |

The vector store, reranker, and query pipeline are backend-agnostic: they only
see vectors and text, so swapping a backend changes retrieval quality without
touching the pipeline.

> **Note on TF-IDF:** the default embedder is *lexical*, not semantic. It is a
> zero-dependency prototype to validate the wiring and run in CI. For real
> semantic retrieval, switch to Gemini/Cohere (API) or fastembed (local, needs
> a one-time model download).

## Module map

| Module                      | Responsibility                                            |
|-----------------------------|-----------------------------------------------------------|
| `ragnostic.extraction`      | Full-document parse into sections (parser interface)      |
| `ragnostic.semantic`        | Section-aware chunking + document summarization           |
| `ragnostic.embeddings`      | `EmbeddingProvider` backends (TF-IDF, Gemini, Cohere, ...) |
| `ragnostic.vectorstore`     | ChromaDB two-tier store (summaries + chunks)              |
| `ragnostic.query`           | Two-tier retrieval, section-coverage rerank, answer hooks |
| `ragnostic.pipeline`        | `RagIndexer` (document flow) + `build_query_pipeline`     |

The database schema (`ragnostic.db`) gained two tables: `document_chunks` and
`document_summaries`, plus CRUD and a `search_documents_by_title` keyword helper.

## Section-coverage reranking

Per the project plan, chunks are rescored to favour sections with multiple
retrieved chunks:

```
section_coverage = chunks_retrieved_from_section / total_chunks_in_section
rerank_score     = (1 - w) * cosine_similarity + w * section_coverage   # w = 0.3 default
```

Chunks are built per section so every chunk maps to exactly one section, which
the rerank step relies on.

## Usage

### Programmatic

```python
from ragnostic.db.client import DatabaseClient
from ragnostic.vectorstore.store import VectorStore
from ragnostic.pipeline import RagIndexer, build_query_pipeline

db = DatabaseClient("sqlite:///ragnostic.db")
store = VectorStore("./vector_store")

# Document flow (documents must already be ingested / registered in the DB)
indexer = RagIndexer(db_client=db, vector_store=store)
indexer.process_all()          # parse -> sections -> chunks -> summaries
indexer.build_vector_index()   # embed everything into ChromaDB

# Query flow
pipeline = build_query_pipeline(db, "./vector_store")
result = pipeline.query("oxygen transfer in stirred tank bioreactors")
for chunk in result.chunks:
    print(chunk.rerank_score, chunk.section_title, chunk.text[:120])
```

### Demo script

```bash
make demo
# or with options:
python scripts/demo_rag.py --limit 5
python scripts/demo_rag.py --embedder gemini --answer gemini \
    --query "economics of process scale up"
```

The demo registers the sample PDFs from `data/`, runs both flows, and prints
tier-1 documents and reranked tier-2 chunks for each query.

## Switching to production backends

```python
from ragnostic.embeddings.api import GeminiEmbedder
from ragnostic.extraction.docling_parser import DoclingParser
from ragnostic.semantic.summarize import LLMSummarizer
from ragnostic.query.answer import make_gemini_answer_fn

indexer = RagIndexer(
    db_client=db,
    vector_store=store,
    embedder=GeminiEmbedder(),       # GEMINI_API_KEY
    parser=DoclingParser(),          # pip install ragnostic[docling]
    summarizer=LLMSummarizer(),      # GEMINI_API_KEY
)
pipeline = build_query_pipeline(
    db, "./vector_store",
    embedder=GeminiEmbedder(),
    answer_fn=make_gemini_answer_fn(),
)
```

## Not in this MVP

- Image/table captioning (schema exists; extraction not wired).
- Entity extraction and knowledge-graph links.
- Full DevOps (CI pipeline, pre-commit) beyond lint/test Make targets.
- Wikipedia ingestion (PDF-only for now).
