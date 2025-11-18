# Issue 14: Implement Query Pipeline (Phase 4)

**Priority:** Low (Future)
**Estimated Effort:** 3-4 weeks
**Labels:** `feature`, `rag`, `phase-4`, `ml`
**Phase:** 4 - Query and Retrieval

## Problem Statement

From project plan (docs/2_Ragnostic_Project_Plan.md):
- Vector storage exists but no query interface
- Two-tier retrieval strategy documented but not implemented
- No query processing or reranking
- No context assembly for LLM consumption

This is the core RAG functionality.

## Scope

Implement complete query pipeline:
1. **Query Processing** - Parse and embed user queries
2. **Two-Tier Retrieval** - Summary search → chunk search
3. **Reranking** - Score chunks by section coverage
4. **Context Assembly** - Format retrieved context for LLM
5. **Query Interface** - User-facing API for questions

## Proposed Solution

### Two-Tier Retrieval Architecture

```
User Query
    ↓
1. Embed Query
    ↓
2. Search Document Summaries (Tier 1)
    ↓
3. Filter to Top-K Documents
    ↓
4. Search Chunks in Filtered Docs (Tier 2)
    ↓
5. Rerank by Section Coverage
    ↓
6. Assemble Context
    ↓
7. Return to LLM
```

### Implementation Outline

```python
# src/ragnostic/query/query_pipeline.py
from dataclasses import dataclass
from typing import List, Optional
from ragnostic.vector import VectorStoreClient, EmbeddingService
from ragnostic.db import DatabaseClient

@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    document_id: str
    document_title: str
    chunks: List[str]
    chunk_ids: List[str]
    scores: List[float]
    section_coverage: float
    total_score: float

class QueryPipeline:
    """Two-tier retrieval pipeline for RAG."""

    def __init__(
        self,
        vector_client: VectorStoreClient,
        embedding_service: EmbeddingService,
        db_client: DatabaseClient,
    ):
        self.vector_client = vector_client
        self.embedding_service = embedding_service
        self.db_client = db_client

    def query(
        self,
        question: str,
        top_k_docs: int = 5,
        chunks_per_doc: int = 10,
    ) -> List[RetrievalResult]:
        """Execute two-tier retrieval.

        Args:
            question: User's question
            top_k_docs: Number of documents to retrieve
            chunks_per_doc: Chunks to retrieve per document

        Returns:
            List of retrieval results with ranked chunks
        """
        # 1. Embed query
        query_embedding = self.embedding_service.embed_text(question)

        # 2. Tier 1: Search document summaries
        summary_results = self.vector_client.search_summaries(
            query_embedding=query_embedding,
            n_results=top_k_docs
        )

        # Extract document IDs
        doc_ids = summary_results['ids'][0]

        # 3. Tier 2: Search chunks within filtered documents
        chunk_results = self.vector_client.search_chunks(
            query_embedding=query_embedding,
            n_results=chunks_per_doc * top_k_docs,
            where={"doc_id": {"$in": doc_ids}}  # Filter to selected docs
        )

        # 4. Group chunks by document
        results_by_doc = self._group_chunks_by_document(chunk_results)

        # 5. Rerank by section coverage
        results = self._rerank_by_section_coverage(results_by_doc)

        # 6. Assemble retrieval results
        return results

    def _group_chunks_by_document(self, chunk_results) -> dict:
        """Group retrieved chunks by document ID."""
        groups = {}
        chunk_ids = chunk_results['ids'][0]
        documents = chunk_results['documents'][0]
        metadatas = chunk_results['metadatas'][0]
        distances = chunk_results['distances'][0]

        for chunk_id, text, metadata, distance in zip(
            chunk_ids, documents, metadatas, distances
        ):
            doc_id = metadata['doc_id']
            if doc_id not in groups:
                groups[doc_id] = {
                    'chunk_ids': [],
                    'chunks': [],
                    'scores': [],
                    'sections': set(),
                    'metadata': metadata
                }

            groups[doc_id]['chunk_ids'].append(chunk_id)
            groups[doc_id]['chunks'].append(text)
            groups[doc_id]['scores'].append(1 - distance)  # Convert distance to score
            if 'section_id' in metadata:
                groups[doc_id]['sections'].add(metadata['section_id'])

        return groups

    def _rerank_by_section_coverage(self, results_by_doc: dict) -> List[RetrievalResult]:
        """Rerank chunks considering section coverage.

        Documents with chunks from more sections get higher scores.
        """
        results = []

        for doc_id, data in results_by_doc.items():
            # Get document metadata
            doc = self.db_client.get_document(doc_id)

            # Calculate section coverage score
            num_sections = len(data['sections'])
            avg_chunk_score = sum(data['scores']) / len(data['scores'])

            # Combined score: chunk relevance + section diversity
            section_coverage = num_sections / 10.0  # Normalize (assume ~10 sections max)
            total_score = (0.7 * avg_chunk_score) + (0.3 * section_coverage)

            results.append(RetrievalResult(
                document_id=doc_id,
                document_title=doc.title,
                chunks=data['chunks'],
                chunk_ids=data['chunk_ids'],
                scores=data['scores'],
                section_coverage=section_coverage,
                total_score=total_score
            ))

        # Sort by total score
        results.sort(key=lambda x: x.total_score, reverse=True)
        return results

    def format_context(
        self,
        results: List[RetrievalResult],
        max_chunks: int = 10
    ) -> str:
        """Format retrieval results as context for LLM.

        Args:
            results: Retrieval results
            max_chunks: Maximum chunks to include

        Returns:
            Formatted context string
        """
        context_parts = []
        chunk_count = 0

        for result in results:
            context_parts.append(f"\n## Document: {result.document_title}\n")

            for chunk, score in zip(result.chunks, result.scores):
                if chunk_count >= max_chunks:
                    break

                context_parts.append(f"(Relevance: {score:.2f})\n{chunk}\n")
                chunk_count += 1

            if chunk_count >= max_chunks:
                break

        return "\n".join(context_parts)
```

### User-Facing API

```python
# src/ragnostic/rag.py
class RAGnostic:
    """Main interface for RAG question-answering."""

    def __init__(self, database_path: str, chroma_path: str):
        self.db_client = DatabaseClient(database_path)
        self.vector_client = VectorStoreClient(chroma_path)
        self.embedding_service = EmbeddingService()
        self.query_pipeline = QueryPipeline(
            self.vector_client,
            self.embedding_service,
            self.db_client
        )

    def ask(
        self,
        question: str,
        llm_provider: str = "openai",
        model: str = "gpt-4",
        top_k: int = 5
    ) -> str:
        """Ask a question and get an answer.

        Args:
            question: User's question
            llm_provider: LLM provider (openai, anthropic, gemini)
            model: Model name
            top_k: Number of documents to retrieve

        Returns:
            Answer generated by LLM
        """
        # Retrieve relevant context
        results = self.query_pipeline.query(question, top_k_docs=top_k)

        # Format context
        context = self.query_pipeline.format_context(results)

        # Build prompt
        prompt = f"""Answer the following question based on the provided context.

Context:
{context}

Question: {question}

Answer:"""

        # Call LLM
        answer = self._call_llm(prompt, llm_provider, model)

        return answer

    def _call_llm(self, prompt: str, provider: str, model: str) -> str:
        """Call LLM provider."""
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        elif provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        # Add other providers...
```

## Acceptance Criteria

- [ ] Query pipeline implemented with two-tier retrieval
- [ ] Query embedding and search working
- [ ] Reranking by section coverage implemented
- [ ] Context assembly formatted for LLMs
- [ ] User-facing API (`RAGnostic.ask()`)
- [ ] Support for multiple LLM providers
- [ ] CLI interface for asking questions
- [ ] Tests for all components
- [ ] Performance benchmarks

## Implementation Steps

1. Create query module
2. Implement `QueryPipeline` class
3. Implement tier 1 (summary search)
4. Implement tier 2 (chunk search with filtering)
5. Implement reranking logic
6. Implement context formatting
7. Create user-facing API
8. Add LLM provider integrations
9. Create CLI interface
10. Add comprehensive tests

## Dependencies

**Required before:**
- Issue #13 (Vector storage must be implemented)
- Phase 3 complete (embeddings exist)

## Testing Strategy

- Unit tests for each pipeline component
- Integration tests for full query flow
- Test with various question types
- Evaluate retrieval quality
- Test with different LLM providers
- Performance testing (query latency)

## Parallel Work Opportunities

**Can work in parallel with:**
- Issue #15 (Evaluation framework)

**Must work after:**
- Issue #13 (vector storage)

## Performance Targets

- Query embedding: <100ms
- Summary search: <200ms
- Chunk search: <500ms
- Total retrieval: <1s
- End-to-end (with LLM): <5s

## CLI Usage Example

```bash
# Ask a question
ragnostic ask "What are the main findings about neural networks?"

# Specify model
ragnostic ask "Explain transformers" --provider anthropic --model claude-3-opus

# Debug mode (show retrieved context)
ragnostic ask "What is RAG?" --debug
```

## API Usage Example

```python
from ragnostic import RAGnostic

# Initialize
rag = RAGnostic(
    database_path="ragnostic.db",
    chroma_path="./chroma_db"
)

# Ask questions
answer = rag.ask("What are the key contributions of this paper?")
print(answer)

# Get retrieval results without LLM
results = rag.query_pipeline.query("neural networks", top_k_docs=5)
for result in results:
    print(f"{result.document_title}: {result.total_score:.2f}")
```

## Notes

- Consider adding query history/caching
- May want to add streaming responses
- Could add citation/source attribution
- Consider adding confidence scores
- May want conversation history for follow-up questions
- Could add query rewriting/expansion
