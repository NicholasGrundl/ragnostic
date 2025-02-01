"""Shared fixtures for indexing tests."""
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import Document, DocumentMetadata


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF file content."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<<\n"
        b"/Title (Test Document)\n"
        b"/Author (Test Author)\n"
        b"/CreationDate (D:20240201000000)\n"
        b">>\n"
        b"endobj\n"
        b"%%EOF"
    )


@pytest.fixture
def sample_pdf_path(tmp_path, sample_pdf_bytes):
    """Create a sample PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(sample_pdf_bytes)
    return pdf_path


@pytest.fixture
def mock_db_client():
    """Create a mock database client."""
    client = Mock(spec=DatabaseClient)
    
    # Setup default document return
    client.create_document.return_value = Document(
        id="DOC123",
        raw_file_path="/path/test.pdf",
        file_hash="abc123",
        file_size_bytes=1000,
        mime_type="application/pdf",
        ingestion_date=datetime.now(),
        total_sections=0,
        total_images=0,
        total_tables=0,
        total_pages=0
    )
    
    # Setup default metadata return
    client.create_metadata.return_value = DocumentMetadata(
        doc_id="DOC123",
        title="Test Doc",
        authors=["Test Author"],
        creation_date=datetime.now(),
        page_count=10,
        language="en"
    )
    
    return client


@pytest.fixture
def mock_pdf_processor():
    """Create a mock PDFProcessor."""
    mock_proc = MagicMock()
    
    # Setup metadata
    mock_proc.doc.metadata = {
        "title": "Test Document",
        "author": "Test Author",
        "creationDate": "D:20240201000000",
        "language": "en"
    }
    
    # Setup document properties
    mock_proc.doc.__len__.return_value = 10
    
    # Setup text extraction
    mock_proc.doc.__getitem__.return_value.get_text.return_value = "Sample text content"
    
    return mock_proc


@pytest.fixture
def corrupted_pdf_path(tmp_path):
    """Create a corrupted PDF file for testing."""
    pdf_path = tmp_path / "corrupted.pdf"
    pdf_path.write_bytes(b"Not a valid PDF file")
    return pdf_path


@pytest.fixture
def multiple_pdf_paths(tmp_path, sample_pdf_bytes):
    """Create multiple PDF files for batch testing."""
    paths = []
    for i in range(3):
        pdf_path = tmp_path / f"test_{i}.pdf"
        pdf_path.write_bytes(sample_pdf_bytes)
        paths.append(pdf_path)
    return paths