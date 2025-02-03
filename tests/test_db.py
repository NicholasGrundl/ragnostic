"""Tests for database operations."""
import pytest
from datetime import datetime
from pathlib import Path

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import (
    DocumentCreate,
    Document,
    DocumentMetadataCreate,
    DocumentMetadata,
    DocumentSectionCreate,
    DocumentSection,
    SectionContentCreate,
    DocumentImageCreate,
    DocumentTableCreate,
)


@pytest.fixture
def db_path(tmp_path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test.db"


@pytest.fixture
def db_client(db_path) -> DatabaseClient:
    """Create a database client for testing."""
    return DatabaseClient(f"sqlite:///{db_path}")


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
        sequence_order=1,
        word_count=100,
        image_count=0,
        table_count=0
    )


@pytest.fixture
def sample_section_content() -> SectionContentCreate:
    """Create sample section content for testing."""
    return SectionContentCreate(
        section_id="sec1",
        title="Introduction",
        content="This is the introduction section.",
        page_start=1,
        page_end=2
    )


@pytest.fixture
def sample_image() -> DocumentImageCreate:
    """Create sample document image for testing."""
    return DocumentImageCreate(
        doc_id="doc1",
        section_id="sec1",
        page_number=1,
        image_data="base64_encoded_data",
        caption="Test image"
    )


@pytest.fixture
def sample_table() -> DocumentTableCreate:
    """Create sample document table for testing."""
    return DocumentTableCreate(
        doc_id="doc1",
        section_id="sec1",
        page_number=1,
        table_data={"headers": ["Col1"], "rows": [["Data1"]]},
        caption="Test table"
    )


def test_create_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test creating a document."""
    doc = db_client.create_document(sample_document)
    assert isinstance(doc, Document)
    assert doc.id == sample_document.id
    assert doc.file_hash == sample_document.file_hash
    assert doc.total_sections == 0
    assert doc.total_images == 0
    assert doc.total_tables == 0


def test_get_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test retrieving a document."""
    created_doc = db_client.create_document(sample_document)
    retrieved_doc = db_client.get_document_by_id(created_doc.id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.file_hash == created_doc.file_hash


def test_get_document_by_hash(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test retrieving a document by hash."""
    created_doc = db_client.create_document(sample_document)
    retrieved_doc = db_client.get_document_by_hash(created_doc.file_hash)
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
    assert metadata.authors == sample_metadata.authors


def test_get_metadata(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_metadata: DocumentMetadataCreate
):
    """Test retrieving document metadata."""
    db_client.create_document(sample_document)
    created_metadata = db_client.create_metadata(sample_metadata)
    retrieved_metadata = db_client.get_metadata(created_metadata.doc_id)
    assert retrieved_metadata is not None
    assert retrieved_metadata.doc_id == created_metadata.doc_id
    assert retrieved_metadata.title == created_metadata.title


def test_create_section(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate
):
    """Test creating a document section with content."""
    db_client.create_document(sample_document)
    section = db_client.create_section(sample_section, sample_section_content)
    assert isinstance(section, DocumentSection)
    assert section.section_id == sample_section.section_id
    assert section.content is not None
    assert section.content.title == sample_section_content.title
    
    # Verify document metrics were updated
    doc = db_client.get_document_by_id(sample_document.id)
    assert doc is not None
    assert doc.total_sections == 1


def test_get_document_sections(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate
):
    """Test retrieving document sections."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section, sample_section_content)
    
    sections = db_client.get_document_sections(sample_document.id)
    assert len(sections) == 1
    assert sections[0].section_id == sample_section.section_id
    assert sections[0].content is not None
    assert sections[0].content.title == sample_section_content.title


def test_create_image(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate,
    sample_image: DocumentImageCreate
):
    """Test creating a document image."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section, sample_section_content)
    image = db_client.create_image(sample_image)
    
    assert image.doc_id == sample_image.doc_id
    assert image.section_id == sample_image.section_id
    
    # Verify metrics were updated
    doc = db_client.get_document_by_id(sample_document.id)
    assert doc.total_images == 1
    
    sections = db_client.get_document_sections(sample_document.id)
    assert sections[0].image_count == 1


def test_create_table(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate,
    sample_table: DocumentTableCreate
):
    """Test creating a document table."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section, sample_section_content)
    table = db_client.create_table(sample_table)
    
    assert table.doc_id == sample_table.doc_id
    assert table.section_id == sample_table.section_id
    
    # Verify metrics were updated
    doc = db_client.get_document_by_id(sample_document.id)
    assert doc.total_tables == 1
    
    sections = db_client.get_document_sections(sample_document.id)
    assert sections[0].table_count == 1


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
