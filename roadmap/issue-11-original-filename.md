# Issue 11: Add Original Filename to Document Indexing

**Priority:** Low
**Estimated Effort:** 0.5 days
**Labels:** `enhancement`, `database`, `feature`
**Phase:** 1 - Complete Ingestion

## Problem Statement

From ACTIONITEMS.md: "Add original filename as field in indexing"

Currently:
- Documents stored with generated IDs (e.g., `abc123.pdf`)
- Original filename lost or only in file path
- Cannot search/filter by original filename
- Difficult to trace documents back to source
- User-friendly identification requires original name

## Current State

**Database Schema** (src/ragnostic/db/models.py:20-40):
```python
class Document:
    id: str  # Generated ID
    file_path: str  # Path to stored file
    file_hash: str  # SHA-256 hash
    title: str  # Extracted title
    # No original_filename field
```

**Storage:**
- Original: `/input/research_paper_2023.pdf`
- Stored as: `/storage/nK8xPqR2hN4wLmT6vJ3z.pdf`
- Original name lost

## Proposed Solution

Add `original_filename` field to database schema and track it through ingestion:

### 1. Update Database Model

```python
# src/ragnostic/db/models.py
class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    original_filename = Column(String, nullable=False, index=True)  # NEW
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True, index=True)
    # ... other fields
```

### 2. Update Pydantic Schema

```python
# src/ragnostic/db/schemas.py
class DocumentCreate(BaseModel):
    file_path: str
    original_filename: str  # NEW
    file_hash: str
    # ... other fields

class DocumentRead(BaseModel):
    id: str
    original_filename: str  # NEW
    # ... other fields
```

### 3. Update Indexer

```python
# src/ragnostic/ingestion/indexing/indexer.py
def index_document(self, file_path: Path, document_id: str) -> Document:
    """Index document with original filename."""

    # Extract original filename
    original_filename = file_path.name

    # Create document record
    doc_data = DocumentCreate(
        file_path=str(stored_path),
        original_filename=original_filename,  # NEW
        file_hash=file_hash,
        # ... other fields
    )

    return self.db_client.create_document(doc_data)
```

### 4. Database Migration

```python
# migrations/add_original_filename.py
from sqlalchemy import text

def upgrade(connection):
    """Add original_filename column."""
    connection.execute(text(
        "ALTER TABLE documents ADD COLUMN original_filename TEXT"
    ))
    connection.execute(text(
        "CREATE INDEX ix_documents_original_filename ON documents (original_filename)"
    ))

def downgrade(connection):
    """Remove original_filename column."""
    connection.execute(text(
        "DROP INDEX ix_documents_original_filename"
    ))
    connection.execute(text(
        "ALTER TABLE documents DROP COLUMN original_filename"
    ))
```

## Acceptance Criteria

- [ ] `original_filename` field added to `Document` model
- [ ] Database migration created and tested
- [ ] Pydantic schemas updated
- [ ] Indexer captures original filename
- [ ] Field indexed for search performance
- [ ] Search by original filename works
- [ ] Tests updated
- [ ] Existing data migrated (if any)
- [ ] Documentation updated

## Implementation Steps

1. **Update database model** (models.py)
2. **Update Pydantic schemas** (schemas.py)
3. **Create migration script** (or use Alembic)
4. **Update indexer** to capture original filename
5. **Update search** to search by original filename
6. **Add tests:**
   ```python
   def test_original_filename_stored(db_client, tmp_path):
       file_path = tmp_path / "my_document.pdf"
       file_path.write_text("test")

       doc = indexer.index_document(file_path, "doc123")

       assert doc.original_filename == "my_document.pdf"
   ```
7. **Update CLI** to display original filename
8. **Migrate existing data** (set to file_path basename if null)

## Dependencies

None - can be implemented independently

## Testing Strategy

- Test original filename captured during indexing
- Test search by original filename
- Test migration on existing database
- Test with special characters in filename
- Test with very long filenames

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- All other issues (independent change)

## Migration Strategy

For existing databases:
```sql
UPDATE documents
SET original_filename = substr(file_path, instr(file_path, '/') + 1)
WHERE original_filename IS NULL;
```

## Notes

- Consider max length for filename (255 chars typical)
- Handle special characters in filenames
- May want to store file extension separately
- Consider normalizing filenames (lowercase, no spaces)
- Useful for search: "Find all PDFs with 'report' in filename"
