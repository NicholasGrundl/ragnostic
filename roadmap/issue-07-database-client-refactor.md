# Issue 07: Refactor Database Client Architecture

**Priority:** Medium
**Estimated Effort:** 2-3 days
**Labels:** `refactoring`, `architecture`, `database`
**Phase:** 1 - Complete Ingestion

## Problem Statement

From ACTIONITEMS.md:
- "Decouple from business logic"
- "Create base CRUD API caller"
- "Create indexing-specific wrapper with business logic"

Current issues:
- Database client mixes infrastructure and business logic
- CRUD operations entangled with domain logic
- Difficult to test business logic separately
- Tight coupling makes it hard to swap database implementations
- No clear separation of concerns

## Current State

**Current Architecture:**
```
DatabaseClient (src/ragnostic/db/client.py)
├── Low-level SQLAlchemy operations
├── Business logic (validation, transformations)
└── Domain-specific queries (all mixed together)
```

**Problems:**
- Single responsibility principle violated
- Cannot easily mock database for testing business logic
- Cannot reuse CRUD operations for different entities
- Hard to add new database backends

## Proposed Solution

Implement a layered architecture:

```
┌─────────────────────────────────────────┐
│   IndexingService (Business Logic)      │  ← Domain-specific operations
├─────────────────────────────────────────┤
│   DocumentRepository (Data Access)      │  ← Entity-specific queries
├─────────────────────────────────────────┤
│   BaseRepository (Generic CRUD)         │  ← Reusable CRUD operations
├─────────────────────────────────────────┤
│   DatabaseClient (Connection/Session)   │  ← Database infrastructure
└─────────────────────────────────────────┘
```

### 1. Database Client (Infrastructure Layer)

Manages connections and sessions only:
```python
# src/ragnostic/db/client.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

class DatabaseClient:
    """Manages database connections and sessions."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    @contextmanager
    def session(self) -> Session:
        """Provide a transactional scope for database operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
```

### 2. Base Repository (Generic CRUD)

Reusable CRUD operations:
```python
# src/ragnostic/db/repository/base.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Generic repository with CRUD operations."""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, id: str) -> Optional[T]:
        return self.session.query(self.model).filter_by(id=id).first()

    def get_all(self) -> List[T]:
        return self.session.query(self.model).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, obj: T) -> T:
        self.session.merge(obj)
        self.session.flush()
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.flush()
```

### 3. Document Repository (Entity-specific)

Domain-specific queries:
```python
# src/ragnostic/db/repository/document.py
from typing import Optional, List
from sqlalchemy.orm import Session
from ragnostic.db.models import Document
from ragnostic.db.repository.base import BaseRepository

class DocumentRepository(BaseRepository[Document]):
    """Repository for Document entity with domain-specific queries."""

    def __init__(self, session: Session):
        super().__init__(session, Document)

    def get_by_hash(self, file_hash: str) -> Optional[Document]:
        """Find document by file hash (for duplicate detection)."""
        return self.session.query(Document).filter_by(file_hash=file_hash).first()

    def get_by_status(self, status: str) -> List[Document]:
        """Get all documents with given status."""
        return self.session.query(Document).filter_by(status=status).all()

    def search_by_title(self, title: str) -> List[Document]:
        """Search documents by title."""
        return self.session.query(Document).filter(
            Document.title.ilike(f"%{title}%")
        ).all()
```

### 4. Indexing Service (Business Logic)

High-level operations with business rules:
```python
# src/ragnostic/ingestion/services/indexing_service.py
from ragnostic.db.client import DatabaseClient
from ragnostic.db.repository.document import DocumentRepository
from ragnostic.db.schemas import DocumentCreate

class IndexingService:
    """Service for document indexing with business logic."""

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    def index_document(self, doc_data: DocumentCreate) -> Document:
        """Index a document with validation and business rules."""

        with self.db_client.session() as session:
            repo = DocumentRepository(session)

            # Business logic: Check for duplicates
            existing = repo.get_by_hash(doc_data.file_hash)
            if existing:
                raise ValueError(f"Document already exists: {existing.id}")

            # Business logic: Validate and transform
            doc_data = self._validate_and_transform(doc_data)

            # Create document
            document = Document(**doc_data.model_dump())
            return repo.create(document)

    def _validate_and_transform(self, doc_data: DocumentCreate) -> DocumentCreate:
        """Apply business rules and transformations."""
        # Business logic here
        return doc_data
```

## Acceptance Criteria

- [ ] `DatabaseClient` only manages connections/sessions
- [ ] `BaseRepository` provides generic CRUD operations
- [ ] `DocumentRepository` provides entity-specific queries
- [ ] Business logic moved to service layer
- [ ] All existing functionality preserved
- [ ] Tests updated to use new architecture
- [ ] Documentation updated
- [ ] No breaking changes to external API

## Implementation Steps

1. **Create base repository:**
   - Create `src/ragnostic/db/repository/__init__.py`
   - Implement `BaseRepository` with generic CRUD

2. **Create document repository:**
   - Implement `DocumentRepository` extending `BaseRepository`
   - Move all query logic from `DatabaseClient`

3. **Refactor database client:**
   - Remove business logic
   - Keep only connection/session management
   - Simplify to infrastructure concerns

4. **Create indexing service:**
   - Create `src/ragnostic/ingestion/services/indexing_service.py`
   - Move business logic from database client
   - Use repository for data access

5. **Update existing code:**
   - Update indexer to use `IndexingService`
   - Update tests to use new architecture
   - Ensure backward compatibility

6. **Add tests:**
   - Unit tests for `BaseRepository`
   - Unit tests for `DocumentRepository`
   - Unit tests for `IndexingService` (with mocked repository)
   - Integration tests for full stack

## Dependencies

**Required before:**
- Issue #03 (package installation)
- Issue #06 (pytest markers for better test organization)

**Enhanced by:**
- Issue #05 (logging helps debug the refactoring)

## Testing Strategy

### Unit Tests (with mocks)

```python
@pytest.mark.fast
@pytest.mark.unit
def test_indexing_service_duplicate_detection(mocker):
    """Test duplicate detection without real database."""
    mock_repo = mocker.Mock()
    mock_repo.get_by_hash.return_value = Document(id="existing")

    service = IndexingService(mock_db_client)
    # Inject mock repository
    with pytest.raises(ValueError, match="already exists"):
        service.index_document(doc_data)
```

### Integration Tests (with real database)

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.database
def test_document_repository_integration(db_client):
    """Test repository with real database."""
    with db_client.session() as session:
        repo = DocumentRepository(session)
        doc = repo.create(Document(...))
        assert doc.id is not None
        retrieved = repo.get_by_id(doc.id)
        assert retrieved.id == doc.id
```

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #05 (logging)
- Issue #09 (cleanup on success)
- Issue #11 (original filename)

Should be worked **before**:
- Issue #10 (document search - benefits from repository pattern)
- Issue #08 (integration tests - easier with layered architecture)

## Migration Strategy

### Phase 1: Add new layers (non-breaking)
- Create new repository and service classes
- Keep existing `DatabaseClient` methods

### Phase 2: Deprecate old methods
- Add deprecation warnings to old methods
- Update documentation to use new API

### Phase 3: Remove deprecated code
- Remove old methods after migration complete
- Clean up imports

## Benefits

1. **Testability:**
   - Can mock repositories for unit testing services
   - Can test repositories in isolation
   - Easier to test business logic

2. **Maintainability:**
   - Clear separation of concerns
   - Each layer has single responsibility
   - Easier to understand and modify

3. **Flexibility:**
   - Can swap database implementations
   - Can add caching layer
   - Can add different repositories for different entities

4. **Reusability:**
   - Base repository reusable for all entities
   - Generic CRUD operations shared
   - Service patterns reusable

## Notes

- Consider using dependency injection framework (e.g., `injector` or `dependency-injector`)
- Repository pattern is well-suited for SQLAlchemy
- Service layer can be async if needed (FastAPI, etc.)
- Consider adding Unit of Work pattern for complex transactions
- May want to add caching decorator to repository methods
