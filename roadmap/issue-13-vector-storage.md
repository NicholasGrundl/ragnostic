# Issue 13: Implement Vector Storage with ChromaDB (Phase 3)

**Priority:** Low (Future)
**Estimated Effort:** 3-4 weeks
**Labels:** `feature`, `vector-db`, `phase-3`, `ml`
**Phase:** 3 - Vector Storage and Indexing

## Problem Statement

From project plan (docs/2_Ragnostic_Project_Plan.md):
- Documents semantically extracted but not vectorized
- No vector search capability
- ChromaDB specified in requirements but not integrated
- Two-tier retrieval system (summaries + chunks) not implemented

## Scope

Implement hierarchical vector storage:
1. **Document summary embeddings** - For first-tier filtering
2. **Chunk embeddings** - For fine-grained retrieval
3. **ChromaDB integration** - Vector database setup
4. **Embedding pipeline** - Generate and store embeddings
5. **Metadata filtering** - Support for hybrid search

## Current State

**Exists:**
- ChromaDB in requirements.txt
- sentence-transformers in requirements.txt
- Database schema designed (docs/2b_Semantic_Extraction.md)

**Not Implemented:**
- ChromaDB client/connection
- Embedding generation
- Vector collections
- Embedding storage and retrieval

## Proposed Solution

### Two-Tier Collection Architecture

```
ChromaDB
├── summaries_collection
│   ├── Document-level embeddings
│   ├── Metadata: {doc_id, title, type, page_count}
│   └── Use for: Initial document filtering
│
└── chunks_collection
    ├── Chunk-level embeddings
    ├── Metadata: {doc_id, section_id, chunk_id, page_num}
    └── Use for: Fine-grained retrieval
```

### Implementation Outline

```python
# src/ragnostic/vector/chroma_client.py
from chromadb import Client, Settings
from chromadb.config import Settings
import chromadb

class VectorStoreClient:
    """Client for ChromaDB vector storage."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create collections with metadata
        self.summaries = self.client.get_or_create_collection(
            name="document_summaries",
            metadata={"hnsw:space": "cosine"}
        )

        self.chunks = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    def add_document_summary(
        self,
        doc_id: str,
        summary_text: str,
        embedding: list[float],
        metadata: dict
    ):
        """Add document summary embedding."""
        self.summaries.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[summary_text],
            metadatas=[metadata]
        )

    def add_chunks(
        self,
        chunk_ids: list[str],
        chunk_texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict]
    ):
        """Add chunk embeddings in batch."""
        self.chunks.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunk_texts,
            metadatas=metadatas
        )

    def search_summaries(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict = None
    ):
        """Search document summaries."""
        return self.summaries.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

    def search_chunks(
        self,
        query_embedding: list[float],
        n_results: int = 20,
        where: dict = None
    ):
        """Search document chunks."""
        return self.chunks.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
```

```python
# src/ragnostic/vector/embedding_service.py
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """Service for generating embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        return self.model.encode(texts).tolist()
```

## Acceptance Criteria

- [ ] ChromaDB client implemented
- [ ] Two collections created (summaries, chunks)
- [ ] Embedding service implemented
- [ ] Summary embeddings stored
- [ ] Chunk embeddings stored
- [ ] Search functionality works
- [ ] Metadata filtering supported
- [ ] Batch operations efficient
- [ ] Tests for all operations
- [ ] Configuration for embedding model selection

## Implementation Steps

1. **Create vector module:**
   ```bash
   mkdir -p src/ragnostic/vector
   touch src/ragnostic/vector/__init__.py
   touch src/ragnostic/vector/chroma_client.py
   touch src/ragnostic/vector/embedding_service.py
   ```

2. **Implement ChromaDB client** (see solution above)

3. **Implement embedding service**

4. **Create indexing workflow:**
   - Generate summary embeddings
   - Generate chunk embeddings
   - Store in ChromaDB
   - Link to SQL database via IDs

5. **Add configuration:**
   ```bash
   # .env
   EMBEDDING_MODEL=all-MiniLM-L6-v2  # Or sentence-transformers/all-mpnet-base-v2
   CHROMA_PERSIST_DIR=./chroma_db
   ```

6. **Integration with Phase 2:**
   - After semantic extraction, trigger embedding
   - Store embeddings alongside chunks

7. **Add tests:**
   - Test collection creation
   - Test embedding generation
   - Test similarity search
   - Test metadata filtering
   - Test batch operations

## Dependencies

**Required before:**
- Issue #12 (Semantic extraction must produce summaries and chunks)
- Phase 2 complete

**Enhanced by:**
- Issue #05 (logging)

## Testing Strategy

- Unit tests for embedding generation
- Integration tests for ChromaDB operations
- Test with real document data
- Benchmark embedding speed
- Test search quality and relevance

## Parallel Work Opportunities

**Can work in parallel with:**
- Issue #14 (Query pipeline planning)

**Must work after:**
- Issue #12 (needs summaries and chunks)

**Required before:**
- Issue #14 (query pipeline needs vector search)

## Embedding Model Selection

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | Development, general |
| all-mpnet-base-v2 | 768 | Medium | Better | Production |
| instructor-large | 768 | Slow | Best | High quality needed |

## Performance Considerations

**Embedding Generation:**
- Batch processing: ~100 texts/second (GPU)
- ~10 texts/second (CPU)
- Cache embeddings to avoid regeneration

**Vector Search:**
- ChromaDB uses HNSW index (fast)
- Sub-second search for <1M vectors
- Consider sharding for >10M vectors

**Storage:**
- 384-dim embeddings: ~1.5KB per embedding
- 10K documents × 100 chunks = 1M embeddings ≈ 1.5GB

## Configuration Options

```python
# Different embedding models for different needs
MODELS = {
    "fast": "all-MiniLM-L6-v2",        # 384-dim, fastest
    "balanced": "all-mpnet-base-v2",   # 768-dim, good quality
    "quality": "instructor-large",      # 768-dim, best quality
    "multilingual": "paraphrase-multilingual-MiniLM-L12-v2",  # 384-dim
}
```

## Future Enhancements

- **Multimodal embeddings:** CLIP for images
- **Reranking:** Use cross-encoder for reranking top results
- **Fine-tuning:** Fine-tune embeddings on domain data
- **Hybrid search:** Combine vector + keyword search
- **Query expansion:** Expand queries for better recall

## Notes

- ChromaDB persists to disk automatically
- Consider separate embedding model for queries vs documents
- May want to experiment with different distance metrics (cosine, L2, IP)
- Metadata filtering crucial for two-tier retrieval
- Consider adding embedding versioning for model updates
