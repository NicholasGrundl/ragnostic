# Action Items

## MVP RAG pipeline — DONE

The end-to-end two-tier RAG pipeline is implemented and demoable
(`make demo`, see `docs/3_MVP_RAG_Pipeline.md`):
- [x] Packaging fixed: `pyproject.toml` declares runtime deps + optional extras; `pip install -e .` works
- [x] DB schema: added `document_chunks` + `document_summaries`, client CRUD, and `search_documents_by_title` keyword search
- [x] Full-document parsing into sections (`ragnostic.extraction`, pymupdf4llm default / docling pluggable)
- [x] Section-aware chunking + document summarization (`ragnostic.semantic`)
- [x] Pluggable embeddings (`ragnostic.embeddings`: TF-IDF offline default, Gemini/Cohere/fastembed)
- [x] ChromaDB two-tier vector store (`ragnostic.vectorstore`)
- [x] Two-tier query pipeline with section-coverage reranking + optional LLM answers (`ragnostic.query`)
- [x] Orchestration (`RagIndexer`, `build_query_pipeline`) + demo script
- [x] Tests (112 passing) with unit/integration markers; lint/format/test Make targets

### Follow-ups (still open)
- Image/table captioning (schema exists, extraction not wired)
- Entity extraction / knowledge-graph links
- LLM-quality semantic embeddings demoed end-to-end (needs keys/network)
- Wikipedia ingestion
- CI workflow on GitHub Actions (roadmap issue #01)

## Ingestion flow

Completed the basic ingestion flow and it runs in jupyter.  Whats missing is the following:
- cleanup of ingestion upon success
- possible adding the original filename as a file field on indexing (i.e. change name when indexed with doc_id) and a suffic to the docis for human use
  - can rename files later when we summarize...
- add some logging across the module and custom log setup
- integration test for ingestion flow

Database client
- the client needs some improvement and is tied to business logic currently
- id like the base cvlient to be a CRUD (get, set, update, delete) API caller to the database, we can use this in the API as well
- id like a indexing specific set of functions or database wrapper that have the dusiness logic

Document search and retrieval client
- id like a basic query client or call that runs on a simple keyword search or allows interfacing with the database in code
- basically search the document titles (original title) so humans can use it lightly as a library

## Semantic extraction flow

- just make functions without tests for demo
- run docling and update the database with text, images, tables
- combine all images with descriptions and insert in text at docling location
- assume document level sections and chunk using basic params (overlap and length)

## Query flow
- run standard query using vectors and chunks


# Action Items DevOps:

## CI/CD

- setup linting and formatting make commands
- setup a build command on merge to main (check github actions?)

## Testing

- setup test commands with parameterize.mark tags
- unittest or fast tests tag
- slow tests/ integration tests
- setup make commands for testing