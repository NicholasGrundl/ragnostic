# Issue 10: Implement Document Search Functionality

**Priority:** Medium
**Estimated Effort:** 2-3 days
**Labels:** `feature`, `search`, `enhancement`
**Phase:** 1 - Complete Ingestion

## Problem Statement

From ACTIONITEMS.md:
- "Basic query client for keyword search"
- "Search by document titles (original title)"
- "Human-friendly library interface"

Current state:
- Documents can be ingested and indexed
- No way to search indexed documents
- No query interface for users
- Cannot find documents by title, keywords, or metadata
- Database has the data but no search API

## Current State

**What exists:**
- Database with indexed documents
- Document metadata (title, authors, page count, etc.)
- Document storage with organized files
- No search functionality

**What's missing:**
- Search API/interface
- Keyword search capability
- Title search
- Metadata filtering
- Human-friendly query interface

## Proposed Solution

Implement a multi-tier search system:

### 1. Search Service (Business Logic)

```python
# src/ragnostic/search/search_service.py
from typing import List, Optional
from dataclasses import dataclass
from ragnostic.db import DatabaseClient
from ragnostic.db.models import Document

@dataclass
class SearchResult:
    """Result from document search."""
    document: Document
    score: float  # Relevance score (0-1)
    matched_fields: List[str]  # Which fields matched

@dataclass
class SearchQuery:
    """Search query parameters."""
    text: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    doc_type: Optional[str] = None
    min_pages: Optional[int] = None
    max_pages: Optional[int] = None
    limit: int = 10
    offset: int = 0

class DocumentSearchService:
    """Service for searching indexed documents."""

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search documents with flexible query parameters.

        Args:
            query: Search query with filters

        Returns:
            List of search results ordered by relevance
        """
        with self.db_client.session() as session:
            # Start with base query
            q = session.query(Document)

            # Apply filters
            if query.title:
                q = q.filter(Document.title.ilike(f"%{query.title}%"))

            if query.doc_type:
                q = q.filter(Document.document_type == query.doc_type)

            if query.min_pages:
                q = q.filter(Document.page_count >= query.min_pages)

            if query.max_pages:
                q = q.filter(Document.page_count <= query.max_pages)

            if query.authors:
                # Search in authors JSON field
                for author in query.authors:
                    q = q.filter(Document.authors.contains(author))

            # Full-text search across multiple fields
            if query.text:
                q = self._apply_fulltext_search(q, query.text)

            # Apply pagination
            q = q.limit(query.limit).offset(query.offset)

            # Execute and convert to results
            documents = q.all()
            return [
                SearchResult(
                    document=doc,
                    score=self._calculate_relevance(doc, query),
                    matched_fields=self._get_matched_fields(doc, query)
                )
                for doc in documents
            ]

    def _apply_fulltext_search(self, query, search_text: str):
        """Apply full-text search across document fields."""
        # Simple implementation: search title, preview, metadata
        search_pattern = f"%{search_text}%"
        return query.filter(
            (Document.title.ilike(search_pattern)) |
            (Document.text_preview.ilike(search_pattern))
        )

    def _calculate_relevance(self, doc: Document, query: SearchQuery) -> float:
        """Calculate relevance score for a document."""
        score = 0.0

        # Title match: highest weight
        if query.title and query.title.lower() in doc.title.lower():
            score += 0.5

        # Text match: medium weight
        if query.text:
            if doc.text_preview and query.text.lower() in doc.text_preview.lower():
                score += 0.3

        # Exact type match: low weight
        if query.doc_type and doc.document_type == query.doc_type:
            score += 0.2

        return min(score, 1.0)

    def _get_matched_fields(self, doc: Document, query: SearchQuery) -> List[str]:
        """Identify which fields matched the query."""
        matched = []

        if query.title and query.title.lower() in doc.title.lower():
            matched.append("title")

        if query.text and doc.text_preview and query.text.lower() in doc.text_preview.lower():
            matched.append("content")

        if query.doc_type and doc.document_type == query.doc_type:
            matched.append("type")

        return matched

    def search_by_title(self, title: str, limit: int = 10) -> List[Document]:
        """Convenience method for title search."""
        query = SearchQuery(title=title, limit=limit)
        results = self.search(query)
        return [r.document for r in results]

    def get_recent_documents(self, limit: int = 10) -> List[Document]:
        """Get most recently indexed documents."""
        with self.db_client.session() as session:
            return session.query(Document)\
                .order_by(Document.created_at.desc())\
                .limit(limit)\
                .all()
```

### 2. Command-Line Interface (Human-Friendly)

```python
# src/ragnostic/cli/search.py
import click
from rich.console import Console
from rich.table import Table
from ragnostic.search import DocumentSearchService, SearchQuery
from ragnostic.db import DatabaseClient

console = Console()

@click.command()
@click.option('--title', help='Search by title')
@click.option('--text', help='Full-text search')
@click.option('--type', 'doc_type', help='Filter by document type')
@click.option('--author', help='Filter by author')
@click.option('--limit', default=10, help='Number of results')
def search(title, text, doc_type, author, limit):
    """Search indexed documents."""

    db_client = DatabaseClient("sqlite:///ragnostic.db")
    search_service = DocumentSearchService(db_client)

    query = SearchQuery(
        title=title,
        text=text,
        doc_type=doc_type,
        authors=[author] if author else None,
        limit=limit
    )

    results = search_service.search(query)

    if not results:
        console.print("[yellow]No documents found.[/yellow]")
        return

    # Display results in table
    table = Table(title=f"Search Results ({len(results)} found)")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Pages", justify="right")
    table.add_column("Score", justify="right", style="yellow")

    for result in results:
        doc = result.document
        table.add_row(
            doc.id[:8],
            doc.title[:50],
            doc.document_type or "unknown",
            str(doc.page_count),
            f"{result.score:.2f}"
        )

    console.print(table)

if __name__ == "__main__":
    search()
```

### 3. Programmatic API

```python
# Example usage in Python
from ragnostic import RAGnostic

# Initialize
rag = RAGnostic(database="ragnostic.db")

# Search by title
results = rag.search_by_title("machine learning")

# Advanced search
results = rag.search(
    text="neural networks",
    doc_type="journal",
    min_pages=10,
    limit=5
)

# Get recent documents
recent = rag.get_recent_documents(limit=10)

# Iterate results
for doc in results:
    print(f"{doc.title} ({doc.page_count} pages)")
```

## Acceptance Criteria

- [ ] `DocumentSearchService` implemented with search methods
- [ ] Support for title search
- [ ] Support for full-text search
- [ ] Support for metadata filtering (type, authors, pages)
- [ ] CLI interface for searching documents
- [ ] Programmatic Python API
- [ ] Search results ranked by relevance
- [ ] Pagination support
- [ ] Tests for all search functionality
- [ ] Documentation with usage examples

## Implementation Steps

1. **Create search module:**
   ```bash
   mkdir -p src/ragnostic/search
   touch src/ragnostic/search/__init__.py
   touch src/ragnostic/search/search_service.py
   ```

2. **Implement `DocumentSearchService`** (see solution above)

3. **Create CLI command:**
   ```bash
   mkdir -p src/ragnostic/cli
   touch src/ragnostic/cli/__init__.py
   touch src/ragnostic/cli/search.py
   ```

4. **Add entry point to pyproject.toml:**
   ```toml
   [project.scripts]
   ragnostic-search = "ragnostic.cli.search:search"
   ```

5. **Implement programmatic API:**
   ```python
   # src/ragnostic/__init__.py
   from ragnostic.search import DocumentSearchService
   from ragnostic.db import DatabaseClient

   class RAGnostic:
       def __init__(self, database: str):
           self.db_client = DatabaseClient(f"sqlite:///{database}")
           self.search_service = DocumentSearchService(self.db_client)

       def search(self, **kwargs):
           return self.search_service.search(SearchQuery(**kwargs))

       def search_by_title(self, title: str, limit: int = 10):
           return self.search_service.search_by_title(title, limit)
   ```

6. **Add tests:**
   ```python
   # tests/search/test_search_service.py
   import pytest
   from ragnostic.search import DocumentSearchService, SearchQuery

   @pytest.mark.integration
   @pytest.mark.database
   def test_search_by_title(db_client, sample_documents):
       """Test title search."""
       service = DocumentSearchService(db_client)
       results = service.search(SearchQuery(title="machine learning"))
       assert len(results) > 0
       assert "machine learning" in results[0].document.title.lower()

   @pytest.mark.integration
   @pytest.mark.database
   def test_fulltext_search(db_client, sample_documents):
       """Test full-text search."""
       service = DocumentSearchService(db_client)
       results = service.search(SearchQuery(text="neural networks"))
       assert len(results) > 0
   ```

7. **Add documentation:**
   - Update README with search examples
   - Document CLI usage
   - Add API reference

## Dependencies

**Required before:**
- Issue #03 (package installation)
- Documents must be indexed (Phase 1 ingestion complete)

**Enhanced by:**
- Issue #07 (repository pattern makes search implementation cleaner)
- Issue #05 (logging for search operations)

## Testing Strategy

### Unit Tests
- Search query building
- Relevance scoring algorithm
- Filter application logic

### Integration Tests
- Search with real database
- Title search accuracy
- Full-text search results
- Metadata filtering
- Pagination

### Test Data
Use existing sample documents in `data/`:
- Create test database with indexed samples
- Verify search finds known documents
- Test edge cases (empty results, special characters)

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #09 (cleanup)
- Issue #11 (original filename)
- Issue #12 (semantic extraction planning)

Should be worked **after**:
- Issue #03 (package installation)
- Documents indexed from Phase 1

## Future Enhancements

### SQLite FTS (Full-Text Search)
For better performance, consider SQLite FTS5:
```sql
CREATE VIRTUAL TABLE documents_fts USING fts5(
    document_id,
    title,
    text_preview,
    content='documents'
);
```

### Advanced Ranking
- TF-IDF scoring
- BM25 algorithm
- Field boost weights

### Query Features
- Boolean operators (AND, OR, NOT)
- Phrase search ("exact phrase")
- Wildcard search (machine*)
- Fuzzy matching (tolerates typos)

### Performance
- Caching frequent queries
- Query optimization
- Index tuning

## CLI Usage Examples

```bash
# Search by title
ragnostic-search --title "machine learning"

# Full-text search
ragnostic-search --text "neural networks"

# Combined search
ragnostic-search --title "deep learning" --type "journal" --limit 5

# Filter by author
ragnostic-search --author "Hinton"

# Recent documents
ragnostic-search --limit 10
```

## API Usage Examples

```python
from ragnostic import RAGnostic

rag = RAGnostic(database="ragnostic.db")

# Simple title search
docs = rag.search_by_title("reinforcement learning")

# Advanced search
results = rag.search(
    text="transformer architecture",
    doc_type="article",
    min_pages=5,
    max_pages=50,
    limit=10
)

# Access results
for result in results:
    print(f"Score: {result.score:.2f}")
    print(f"Title: {result.document.title}")
    print(f"Matched: {', '.join(result.matched_fields)}")
    print()
```

## Notes

- Keep search simple initially, enhance with FTS later
- Consider search analytics (track popular queries)
- May want to add search history/suggestions
- Could add export functionality (search results to CSV/JSON)
- Consider adding faceted search (group by type, author, etc.)
