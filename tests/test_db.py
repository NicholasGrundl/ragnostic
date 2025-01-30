"""Tests for database operations."""
import pytest
from datetime import datetime
from pathlib import Path

from ragnostic.db import (
    DatabaseClient,
    Document,
    DocumentCreate,
    DocumentMetadata,
    DocumentMetadataCreate,
    DocumentSection,
    DocumentSectionCreate,
    create_sqlite_url,
)


@pytest.fixture
def db_path(tmp_path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test.db"


@pytest.fixture
def db_client(db_path) -> DatabaseClient:
    """Create a database client for testing."""
    return DatabaseClient(create_sqlite_url(str(db_path)))


@pytest.fixture
def sample_document() -> DocumentCreate:
    """Create a sample document for testing."""
    return DocumentCreate(
        id="doc1",
        raw_file_path="/path/to/doc.pdf",
        file_hash="abc123",
        file_size_bytes=1024,
        mime_type="application/pdf"
    )


@pytest.fixture
def sample_metadata() -> DocumentMetadataCreate:
    """Create sample metadata for testing."""
    return DocumentMetadataCreate(
        doc_id="doc1",
        title="Test Document",
        authors=["Author 1", "Author 2"],
        description="Test description",
        creation_date=datetime(2024, 1, 1),
        page_count=10,
        language="en"
    )


@pytest.fixture
def sample_section() -> DocumentSectionCreate:
    """Create a sample section for testing."""
    return DocumentSectionCreate(
        section_id="sec1",
        doc_id="doc1",
        level=1,
        title="Introduction",
        content="This is the introduction section.",
        sequence_order=1,
        page_start=1,
        page_end=2
    )


def test_create_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test creating a document."""
    doc = db_client.create_document(sample_document)
    assert isinstance(doc, Document)
    assert doc.id == sample_document.id
    assert doc.file_hash == sample_document.file_hash


def test_get_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test retrieving a document."""
    created_doc = db_client.create_document(sample_document)
    retrieved_doc = db_client.get_document_by_id(created_doc.id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.file_hash == created_doc.file_hash


def test_create_metadata(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_metadata: DocumentMetadataCreate
):
    """Test creating document metadata."""
    db_client.create_document(sample_document)
    metadata = db_client.create_metadata(sample_metadata)
    assert isinstance(metadata, DocumentMetadata)
    assert metadata.doc_id == sample_metadata.doc_id
    assert metadata.title == sample_metadata.title


def test_create_section(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate
):
    """Test creating a document section."""
    db_client.create_document(sample_document)
    section = db_client.create_section(sample_section)
    assert isinstance(section, DocumentSection)
    assert section.section_id == sample_section.section_id
    assert section.title == sample_section.title


def test_get_document_sections(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate
):
    """Test retrieving document sections."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section)
    
    sections = db_client.get_document_sections(sample_document.id)
    assert len(sections) == 1
    assert sections[0].section_id == sample_section.section_id


def test_duplicate_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test handling duplicate document creation."""
    db_client.create_document(sample_document)
    with pytest.raises(ValueError):
        db_client.create_document(sample_document)


def test_delete_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test document deletion."""
    db_client.create_document(sample_document)
    assert db_client.delete_document(sample_document.id) is True
    assert db_client.get_document_by_id(sample_document.id) is None


def test_get_nonexistent_document(db_client: DatabaseClient):
    """Test retrieving a nonexistent document."""
    assert db_client.get_document_by_id("nonexistent") is None


def test_create_sqlite_url():
    """Test SQLite URL creation."""
    path = "/path/to/db.sqlite"
    url = create_sqlite_url(path)
    assert url == f"sqlite:///{path}"


def test_default_sqlite_url():
    """Test default SQLite URL creation."""
    url = create_sqlite_url()
    assert "ragnostic.db" in url
    assert url.startswith("sqlite:///")
