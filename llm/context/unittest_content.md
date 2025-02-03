<file_1>
<path>ingestion_indexer/__init__.py</path>
<content>
```python

```
</content>
</file_1>

<file_2>
<path>ingestion_indexer/conftest.py</path>
<content>
```python
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

@pytest.fixture
def sample_page_chunks():
    """Sample page chunks from pymupdf4llm."""
    return [
        {
            'metadata': {
                'title': 'Test Document',
                'author': 'John Doe; Jane Smith',
                'creationDate': 'D:20240201120000',
                'language': 'en',
                'page_count': 10
            },
            'text': 'First page content...'
        },
        {
            'text': 'Second page content...'
        }
    ]

@pytest.fixture
def partial_page_chunks():
    """Page chunks with partial metadata."""
    return [
        {
            'metadata': {
                'title': 'Test Document',
                # Missing other fields
            },
            'text': 'Some content...'
        }
    ]
```
</content>
</file_2>

<file_3>
<path>ingestion_indexer/test_extraction.py</path>
<content>
```python
"""Tests for PDF extraction functionality."""
from datetime import datetime
from unittest.mock import patch, Mock
import pytest

from ragnostic.ingestion.indexing.extraction import PDFExtractor


def test_successful_metadata_extraction(tmp_path, sample_page_chunks):
    """Test successful metadata extraction from PDF."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert metadata is not None
        assert metadata.title == "Test Document"
        assert len(metadata.authors) == 2
        assert "John Doe" in metadata.authors
        assert metadata.language == "en"
        assert metadata.page_count == 10
        assert metadata.text_preview.startswith("First page")


def test_metadata_extraction_with_text(tmp_path, sample_page_chunks):
    """Test metadata extraction with text preview."""
    extractor = PDFExtractor(text_preview_chars=20)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    # TODO: make expected preview based on fixture, test against it truncated to the length
    chunk_texts = [page_chunk.get('text','') for page_chunk in sample_page_chunks]
    expected_text_preview = "\n".join(chunk_texts)
    preview_chars = 20

    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert len(metadata.text_preview) <= preview_chars
        assert metadata.text_preview == expected_text_preview[:preview_chars]


def test_metadata_extraction_without_text(tmp_path, partial_page_chunks):
    """Test metadata extraction without text preview."""
    extractor = PDFExtractor(text_preview_chars=0)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', return_value=partial_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert metadata.title == "Test Document"
        assert metadata.authors is None
        assert metadata.language is None
        assert metadata.text_preview is not None


def test_failed_metadata_extraction(tmp_path):
    """Test handling of failed metadata extraction."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', side_effect=Exception("PDF Error")):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert metadata is None
        assert error is not None
        assert "PDF Error" in error


@pytest.mark.parametrize("author_str,expected", [
    ("John Doe; Jane Smith", ["John Doe", "Jane Smith"]),
    ("John Doe, Jane Smith", ["John Doe", "Jane Smith"]),
    ("Single Author", ["Single Author"]),
    ("", None),
    (None, None),
])
def test_author_parsing(author_str, expected):
    """Test different author string formats."""
    extractor = PDFExtractor()
    result = extractor._parse_authors(author_str)
    assert result == expected


def test_custom_preview_length(tmp_path, sample_page_chunks):
    """Test custom text preview length."""
    extractor = PDFExtractor(text_preview_chars=10)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert len(metadata.text_preview) <= 10
        assert metadata.text_preview == "First page"


def test_empty_metadata_handling(tmp_path):
    """Test handling of empty metadata fields."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    empty_chunks = [{'metadata': {}, 'text': 'content'}]
    with patch('pymupdf4llm.to_markdown', return_value=empty_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert metadata is not None
        assert metadata.title is None
        assert metadata.authors is None
        assert metadata.creation_date is None
        assert metadata.language is None
        assert metadata.page_count is None
        assert metadata.text_preview is not None


@pytest.mark.parametrize("chunks,expected_preview", [
    ([{'text': 'page1'}, {'text': 'page2'}], "page1\npage2"),
    ([{}], ""),
    ([], ""),
])
def test_page_chunks_text_concatenation(chunks, expected_preview):
    """Test text concatenation from multiple page chunks."""
    extractor = PDFExtractor()
    metadata = extractor._parse_page_chunks(chunks)
    assert metadata.text_preview.strip() == expected_preview.strip()
```
</content>
</file_3>

<file_4>
<path>ingestion_indexer/test_indexer.py</path>
<content>
```python
"""Tests for document indexer functionality."""
from pathlib import Path
from unittest.mock import patch, Mock, ANY
import pytest

from ragnostic.ingestion.indexing import DocumentIndexer, IndexingStatus
from ragnostic.ingestion.indexing.schema import DocumentMetadataExtracted
from ragnostic.db.schema import DocumentCreate, DocumentMetadataCreate

def test_indexer_initialization(mock_db_client):
    """Test DocumentIndexer initialization."""
    indexer = DocumentIndexer(mock_db_client)
    assert indexer.db_client == mock_db_client
    assert indexer.extractor is not None

def test_successful_indexing(mock_db_client, sample_pdf_path, sample_page_chunks):
    """Test successful document indexing with metadata."""
    indexer = DocumentIndexer(mock_db_client)
    
    # Mock metadata extraction
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        result = indexer.index_document(sample_pdf_path)
    
    # Verify success
    assert result.status == IndexingStatus.SUCCESS
    assert result.doc_id == mock_db_client.create_document.return_value.id
    assert result.filepath == sample_pdf_path
    assert result.error_message is None
    
    # Verify document creation
    mock_db_client.create_document.assert_called_once()
    doc_create = mock_db_client.create_document.call_args[0][0]
    assert isinstance(doc_create, DocumentCreate)
    assert doc_create.raw_file_path == str(sample_pdf_path)
    
    # Verify metadata creation
    mock_db_client.create_metadata.assert_called_once()
    metadata_create = mock_db_client.create_metadata.call_args[0][0]
    assert isinstance(metadata_create, DocumentMetadataCreate)
    assert metadata_create.doc_id == result.doc_id

def test_indexing_without_metadata(mock_db_client, sample_pdf_path):
    """Test successful document indexing when metadata extraction fails."""
    indexer = DocumentIndexer(mock_db_client)
    
    # Mock failed metadata extraction
    with patch('pymupdf4llm.to_markdown', side_effect=Exception("Extraction failed")):
        result = indexer.index_document(sample_pdf_path)
    
    # Should still succeed but without metadata
    assert result.status == IndexingStatus.SUCCESS
    assert result.doc_id == mock_db_client.create_document.return_value.id
    mock_db_client.create_document.assert_called_once()
    mock_db_client.create_metadata.assert_not_called()

def test_indexing_with_database_error(mock_db_client, sample_pdf_path, sample_page_chunks):
    """Test handling of database errors during indexing."""
    indexer = DocumentIndexer(mock_db_client)
    
    # Mock database error
    mock_db_client.create_document.side_effect = ValueError("Duplicate document")
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        result = indexer.index_document(sample_pdf_path)
    
    assert result.status == IndexingStatus.DATABASE_ERROR
    assert "Duplicate document" in result.error_message
    mock_db_client.create_metadata.assert_not_called()

def test_batch_indexing_success(mock_db_client, multiple_pdf_paths, sample_page_chunks):
    """Test successful batch indexing of multiple documents."""
    indexer = DocumentIndexer(mock_db_client)
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        results = indexer.index_batch(multiple_pdf_paths)
    
    assert results.success_count == len(multiple_pdf_paths)
    assert results.failure_count == 0
    assert len(results.successful_docs) == len(multiple_pdf_paths)
    assert not results.failed_docs
    
    # Verify each document was processed
    assert mock_db_client.create_document.call_count == len(multiple_pdf_paths)
    assert mock_db_client.create_metadata.call_count == len(multiple_pdf_paths)

def test_batch_indexing_with_failures(mock_db_client, multiple_pdf_paths, sample_page_chunks):
    """Test batch indexing with mixed success and failures."""
    indexer = DocumentIndexer(mock_db_client)
    
    # Make every other document fail
    def alternate_success(*args, **kwargs):
        if not hasattr(alternate_success, 'count'):
            alternate_success.count = 0
        alternate_success.count += 1
        if alternate_success.count % 2 == 0:
            raise ValueError("Simulated error")
        return mock_db_client.create_document.return_value
    
    mock_db_client.create_document.side_effect = alternate_success
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        results = indexer.index_batch(multiple_pdf_paths)
    
    expected_successes = (len(multiple_pdf_paths) + 1) // 2
    expected_failures = len(multiple_pdf_paths) // 2
    
    assert results.success_count == expected_successes
    assert results.failure_count == expected_failures
    assert len(results.successful_docs) == expected_successes
    assert len(results.failed_docs) == expected_failures


def test_metadata_creation_error(mock_db_client, sample_pdf_path, sample_page_chunks):
    """Test handling of metadata creation errors."""
    indexer = DocumentIndexer(mock_db_client)
    
    # Mock metadata creation error
    mock_db_client.create_metadata.side_effect = ValueError("Invalid metadata")
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        result = indexer.index_document(sample_pdf_path)
    
    # Should still succeed even if metadata creation fails
    assert result.status == IndexingStatus.SUCCESS
    assert result.doc_id == mock_db_client.create_document.return_value.id
    mock_db_client.create_document.assert_called_once()
    mock_db_client.create_metadata.assert_called_once()

def test_text_extraction_options(mock_db_client, sample_pdf_path, sample_page_chunks):
    """Test different text extraction configurations."""
    # Test with custom preview length
    indexer = DocumentIndexer(mock_db_client, text_preview_chars=50)
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        result = indexer.index_document(sample_pdf_path)
    
    assert result.status == IndexingStatus.SUCCESS
    assert result.extracted_metadata is not None
    assert len(result.extracted_metadata.text_preview) <= 50

def test_empty_batch_indexing(mock_db_client):
    """Test batch indexing with empty list."""
    indexer = DocumentIndexer(mock_db_client)
    results = indexer.index_batch([])
    
    assert results.success_count == 0
    assert results.failure_count == 0
    assert not results.successful_docs
    assert not results.failed_docs
    mock_db_client.create_document.assert_not_called()
    mock_db_client.create_metadata.assert_not_called()

@pytest.mark.parametrize("mock_mime_type,expected_status", [
    ("application/pdf", IndexingStatus.SUCCESS),
    ("application/x-pdf", IndexingStatus.SUCCESS),
    ("image/jpeg", IndexingStatus.METADATA_ERROR),
    ("text/plain", IndexingStatus.METADATA_ERROR),
])
def test_file_type_validation(mock_db_client, sample_pdf_path, mock_mime_type, expected_status):
    """Test handling of different file types."""
    indexer = DocumentIndexer(mock_db_client)
    
    with patch('magic.from_file', return_value=mock_mime_type):
        result = indexer.index_document(sample_pdf_path)
    
    assert result.status == expected_status
    if expected_status == IndexingStatus.SUCCESS:
        mock_db_client.create_document.assert_called_once()
    else:
        mock_db_client.create_document.assert_not_called()
```
</content>
</file_4>

<file_5>
<path>ingestion_indexer/test_schema.py</path>
<content>
```python
"""Tests for indexing schema models."""
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from ragnostic.ingestion.indexing.schema import (
    DocumentMetadataExtracted,
    IndexingResult,
    BatchIndexingResult,
    IndexingStatus,
)


def test_document_metadata_extracted_validation():
    """Test DocumentMetadataExtracted validation."""
    # Test valid metadata
    metadata = DocumentMetadataExtracted(
        title="Test Doc",
        authors=["Author 1", "Author 2"],
        creation_date=datetime.now(),
        page_count=10,
        language="en",
        text_preview="Sample text"
    )
    assert metadata.title == "Test Doc"
    assert len(metadata.authors) == 2
    assert metadata.page_count == 10
    
    # Test optional fields
    metadata = DocumentMetadataExtracted()
    assert metadata.title is None
    assert metadata.authors is None
    
    # Test invalid page count
    with pytest.raises(ValidationError):
        DocumentMetadataExtracted(page_count=-1)


def test_indexing_result_validation():
    """Test IndexingResult validation."""
    # Test successful result
    result = IndexingResult(
        doc_id="DOC123",
        filepath=Path("/path/test.pdf"),
        status=IndexingStatus.SUCCESS
    )
    assert result.doc_id == "DOC123"
    assert result.status == IndexingStatus.SUCCESS
    assert result.error_message is None
    
    # Test failed result with error
    result = IndexingResult(
        doc_id="ERROR",
        filepath=Path("/path/test.pdf"),
        status=IndexingStatus.METADATA_ERROR,
        error_message="Failed to extract metadata"
    )
    assert result.status == IndexingStatus.METADATA_ERROR
    assert result.error_message == "Failed to extract metadata"
    
    # Test required fields
    with pytest.raises(ValidationError):
        IndexingResult(
            filepath=Path("/path/test.pdf"),
            status=IndexingStatus.SUCCESS
        )


def test_batch_indexing_result():
    """Test BatchIndexingResult functionality."""
    # Create some test results
    success_result = IndexingResult(
        doc_id="DOC1",
        filepath=Path("/path/test1.pdf"),
        status=IndexingStatus.SUCCESS
    )
    failed_result = IndexingResult(
        doc_id="DOC2",
        filepath=Path("/path/test2.pdf"),
        status=IndexingStatus.METADATA_ERROR,
        error_message="Extraction failed"
    )
    
    # Test empty batch
    batch = BatchIndexingResult()
    assert batch.success_count == 0
    assert batch.failure_count == 0
    assert not batch.has_failures
    
    # Test mixed results
    batch = BatchIndexingResult(
        successful_docs=[success_result],
        failed_docs=[failed_result]
    )
    assert batch.success_count == 1
    assert batch.failure_count == 1
    assert batch.has_failures
    
    # Test successful batch
    batch = BatchIndexingResult(
        successful_docs=[success_result, success_result]
    )
    assert batch.success_count == 2
    assert batch.failure_count == 0
    assert not batch.has_failures


def test_indexing_status_values():
    """Test IndexingStatus enumeration."""
    # Test all status values
    assert IndexingStatus.SUCCESS == "success"
    assert IndexingStatus.METADATA_ERROR == "metadata_error"
    assert IndexingStatus.EXTRACTION_ERROR == "extraction_error"
    assert IndexingStatus.DATABASE_ERROR == "database_error"
    assert IndexingStatus.UNKNOWN_ERROR == "unknown_error"
    
    # Test status comparison
    assert IndexingStatus.SUCCESS != IndexingStatus.METADATA_ERROR
    
    # Test status in result
    result = IndexingResult(
        doc_id="DOC1",
        filepath=Path("/path/test.pdf"),
        status=IndexingStatus.SUCCESS
    )
    assert result.status == IndexingStatus.SUCCESS
```
</content>
</file_5>

<file_6>
<path>ingestion_processor/__init__.py</path>
<content>
```python

```
</content>
</file_6>

<file_7>
<path>ingestion_processor/conftest.py</path>
<content>
```python
"""Shared test fixtures for processor tests."""
import pytest
from pathlib import Path


@pytest.fixture
def sample_pdf_content():
    """Sample PDF file content for testing."""
    return b"%PDF-1.4\n%TEST PDF CONTENT"


@pytest.fixture
def create_pdf_file(tmp_path, sample_pdf_content):
    """Factory fixture to create test PDF files."""
    def _create_pdf(filename: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_bytes(sample_pdf_content)
        return file_path
    return _create_pdf
```
</content>
</file_7>

<file_8>
<path>ingestion_processor/test_processor.py</path>
<content>
```python
"""Tests for document processor functionality."""
from pathlib import Path
import pytest
from unittest.mock import patch, Mock

from ragnostic.ingestion.processor.processor import DocumentProcessor
from ragnostic.ingestion.processor.schema import ProcessingStatus


@pytest.fixture
def processor():
    """Create a processor instance for testing."""
    return DocumentProcessor(doc_id_prefix="TEST")


@pytest.fixture
def mock_files(tmp_path):
    """Create mock files for testing."""
    files = []
    for i in range(3):
        file_path = tmp_path / f"test{i}.pdf"
        file_path.write_text(f"test content {i}")
        files.append(file_path)
    return files


def test_process_single_document_success(processor, tmp_path, mock_files):
    """Test successful processing of a single document."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    
    result = processor._process_single_document(
        mock_files[0],
        storage_dir
    )
    
    assert result.status == ProcessingStatus.SUCCESS
    assert result.storage_path.exists()
    assert result.storage_path.parent == storage_dir
    assert result.doc_id.startswith("TEST_")


def test_process_single_document_failure(processor, tmp_path):
    """Test processing failure with invalid file."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    
    result = processor._process_single_document(
        Path("/nonexistent/file.pdf"),
        storage_dir
    )
    
    assert result.status == ProcessingStatus.STORAGE_ERROR
    assert "Source file not found" in result.error_message
    assert result.storage_path is None


def test_process_documents_batch_success(processor, tmp_path, mock_files):
    """Test successful processing of multiple documents."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    
    results = processor.process_documents(mock_files, storage_dir)
    
    assert results.success_count == len(mock_files)
    assert results.failure_count == 0
    assert not results.has_failures
    
    # Check all files were stored
    for result in results.successful_docs:
        assert result.storage_path.exists()
        assert result.doc_id.startswith("TEST_")


def test_process_documents_mixed_results(processor, tmp_path, mock_files):
    """Test batch processing with some failures."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    
    # Add a non-existent file
    test_files = mock_files + [Path("/nonexistent/file.pdf")]
    
    results = processor.process_documents(test_files, storage_dir)
    
    assert results.success_count == len(mock_files)
    assert results.failure_count == 1
    assert results.has_failures
    
    # Check successful files
    for result in results.successful_docs:
        assert result.storage_path.exists()
    
    # Check failed file
    assert results.failed_docs[0].status == ProcessingStatus.STORAGE_ERROR
    assert "Source file not found" in results.failed_docs[0].error_message


@patch("ragnostic.ingestion.processor.processor.store_document")
def test_process_documents_unexpected_error(mock_store, processor, tmp_path, mock_files):
    """Test handling of unexpected errors during processing."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    
    # Simulate unexpected error
    mock_store.side_effect = Exception("Unexpected error")
    
    results = processor.process_documents(mock_files, storage_dir)
    
    assert results.success_count == 0
    assert results.failure_count == len(mock_files)
    assert results.has_failures
    
    for result in results.failed_docs:
        assert result.status == ProcessingStatus.UNKNOWN_ERROR
        assert "Unexpected error" in result.error_message
        assert result.error_code == "UNEXPECTED_ERROR"
```
</content>
</file_8>

<file_9>
<path>ingestion_processor/test_schema.py</path>
<content>
```python
"""Tests for processor schema models."""
from pathlib import Path
import pytest

from ragnostic.ingestion.processor.schema import (
    ProcessingStatus,
    ProcessingResult,
    BatchProcessingResult
)


def test_processing_result_creation():
    """Test creating a ProcessingResult with minimal fields."""
    result = ProcessingResult(
        doc_id="DOC123",
        original_path=Path("/tmp/test.pdf"),
        status=ProcessingStatus.SUCCESS
    )
    
    assert result.doc_id == "DOC123"
    assert result.original_path == Path("/tmp/test.pdf")
    assert result.status == ProcessingStatus.SUCCESS
    assert result.error_message is None
    assert result.error_code is None


def test_processing_result_with_error():
    """Test creating a ProcessingResult with error details."""
    result = ProcessingResult(
        doc_id="DOC123",
        original_path=Path("/tmp/test.pdf"),
        status=ProcessingStatus.STORAGE_ERROR,
        error_message="Permission denied",
        error_code="PERMISSION_ERROR"
    )
    
    assert result.status == ProcessingStatus.STORAGE_ERROR
    assert result.error_message == "Permission denied"
    assert result.error_code == "PERMISSION_ERROR"


def test_batch_processing_result_empty():
    """Test creating an empty BatchProcessingResult."""
    batch = BatchProcessingResult()
    
    assert len(batch.successful_docs) == 0
    assert len(batch.failed_docs) == 0
    assert batch.success_count == 0
    assert batch.failure_count == 0
    assert not batch.has_failures


def test_batch_processing_result_with_docs():
    """Test BatchProcessingResult with successful and failed documents."""
    success_doc = ProcessingResult(
        doc_id="DOC1",
        original_path=Path("/tmp/success.pdf"),
        storage_path=Path("/storage/DOC1.pdf"),
        status=ProcessingStatus.SUCCESS
    )
    
    failed_doc = ProcessingResult(
        doc_id="DOC2",
        original_path=Path("/tmp/failed.pdf"),
        status=ProcessingStatus.STORAGE_ERROR,
        error_message="Access denied"
    )
    
    batch = BatchProcessingResult(
        successful_docs=[success_doc],
        failed_docs=[failed_doc]
    )
    
    assert batch.success_count == 1
    assert batch.failure_count == 1
    assert batch.has_failures
    assert batch.successful_docs[0].doc_id == "DOC1"
    assert batch.failed_docs[0].doc_id == "DOC2"
```
</content>
</file_9>

<file_10>
<path>ingestion_processor/test_storage.py</path>
<content>
```python
"""Tests for document storage operations."""
import os
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

from ragnostic.ingestion.processor.storage import store_document
from ragnostic.ingestion.processor.schema import ProcessingStatus


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def mock_source_file(temp_dir):
    """Create a mock source file."""
    source_file = temp_dir / "test.pdf"
    source_file.write_text("test content")
    return source_file


def test_store_document_success(temp_dir, mock_source_file):
    """Test successful document storage."""
    storage_dir = temp_dir / "storage"
    storage_dir.mkdir()
    
    result = store_document(
        source_path=mock_source_file,
        storage_dir=storage_dir,
        doc_id="DOC123"
    )
    
    assert result.status == ProcessingStatus.SUCCESS
    assert result.storage_path == storage_dir / "DOC123.pdf"
    assert result.storage_path.exists()
    assert result.error_message is None


def test_store_document_missing_source():
    """Test storage with non-existent source file."""
    result = store_document(
        source_path=Path("/nonexistent/file.pdf"),
        storage_dir=Path("/tmp"),
        doc_id="DOC123"
    )
    
    assert result.status == ProcessingStatus.STORAGE_ERROR
    assert "Source file not found" in result.error_message
    assert result.error_code == "SOURCE_NOT_FOUND"


def test_store_document_invalid_storage_dir(mock_source_file):
    """Test storage with invalid storage directory."""
    result = store_document(
        source_path=mock_source_file,
        storage_dir=Path("/nonexistent/dir"),
        doc_id="DOC123"
    )
    
    assert result.status == ProcessingStatus.STORAGE_ERROR
    assert "Storage directory invalid" in result.error_message
    assert result.error_code == "INVALID_STORAGE_DIR"


@pytest.mark.parametrize("error,expected_code", [
    (PermissionError("Access denied"), "PERMISSION_DENIED"),
    (OSError("I/O Error"), "STORAGE_FAILED"),
])
def test_store_document_errors(temp_dir, mock_source_file, error, expected_code):
    """Test various error conditions during storage."""
    storage_dir = temp_dir / "storage"
    storage_dir.mkdir()
    
    with patch("ragnostic.ingestion.processor.storage.copy2", side_effect=error):
        result = store_document(
            source_path=mock_source_file,
            storage_dir=storage_dir,
            doc_id="DOC123"
        )
        
        assert result.status == ProcessingStatus.STORAGE_ERROR
        assert result.error_code == expected_code
        assert str(error) in result.error_message
```
</content>
</file_10>

<file_11>
<path>ingestion_validation/__init__.py</path>
<content>
```python

```
</content>
</file_11>

<file_12>
<path>ingestion_validation/conftest.py</path>
<content>
```python
"""Test fixtures for validation tests."""
import os
from pathlib import Path
import pytest
from unittest.mock import Mock

from ragnostic.db.client import DatabaseClient

from pathlib import Path
import pytest
from typing import Optional


@pytest.fixture
def sample_pdf(tmp_path) -> Path:
    """Create a simple PDF file for testing."""
    output_path = tmp_path / "sample.pdf"
    with open(output_path, "wb") as f:
        # PDF header
        f.write(b"%PDF-1.4\n")
        # Required PDF objects
        f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        f.write(b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n")

        # PDF trailer and EOF marker
        f.write(b"xref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n")
        f.write(b"trailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n183\n%%EOF\n")
    
    return output_path


@pytest.fixture
def large_pdf(tmp_path) -> Path:
    """Create a large PDF file for testing."""
    size = 2 * 1024 * 1024  # 2MB
    
    output_path = tmp_path / "large.pdf"
    with open(output_path, "wb") as f:
        # PDF header
        f.write(b"%PDF-1.4\n")
        # Required PDF objects
        f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        f.write(b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n")
        # Pad content for size
        f.write(b"%" + b"0" * size + b"\n")
        # PDF trailer and EOF marker
        f.write(b"xref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n")
        f.write(b"trailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n183\n%%EOF\n")
    
    return output_path


@pytest.fixture
def corrupt_pdf(tmp_path) -> Path:
    """Create a corrupted PDF file for testing."""
    pdf_path = tmp_path / "corrupt.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"Not a PDF file")
    return pdf_path


@pytest.fixture
def non_existent_pdf(tmp_path) -> Path:
    """Return path to non-existent PDF."""
    return tmp_path / "does_not_exist.pdf"


@pytest.fixture
def mock_db_client() -> DatabaseClient:
    """Create mock database client."""
    client = Mock(spec=DatabaseClient)
    client.get_document_by_hash.return_value = None
    return client
```
</content>
</file_12>

<file_13>
<path>ingestion_validation/test_checks.py</path>
<content>
```python
"""Tests for validation check functions."""
from pathlib import Path
import pytest
from unittest.mock import Mock

from ragnostic.ingestion.validation.checks import (
    compute_file_hash,
    check_file_exists,
    check_file_hash,
    check_file_size,
    check_mime_type,
    check_hash_unique,
)
from ragnostic.ingestion.validation.schema import ValidationCheckType, ValidationCheckFailure


def test_compute_file_hash(sample_pdf, large_pdf):
    """Test computing file hash."""
    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:
        # Test valid file
        hash_value = compute_file_hash(pdf_file)
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA-256 produces 64 character hex string
        
        # Test same file produces same hash
        assert compute_file_hash(pdf_file) == hash_value
        
        # Test non-existent file
        assert compute_file_hash(Path("nonexistent.pdf")) is None


def test_check_file_exists(sample_pdf, large_pdf, non_existent_pdf, tmp_path):
    """Test file existence check."""
    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:

        # Test existing file
        result = check_file_exists(pdf_file)
        assert result is True
        
    # Test non-existent file
    result = check_file_exists(non_existent_pdf)
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.OTHER
    
    # Test directory instead of file
    result = check_file_exists(tmp_path)
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.OTHER


def test_check_file_hash(sample_pdf, large_pdf, corrupt_pdf):
    """Test file hash check."""
    pdf_files = [sample_pdf, large_pdf, corrupt_pdf]
    for pdf_file in pdf_files:
        # Test valid file
        result = check_file_hash(pdf_file)
        assert isinstance(result, str)
        assert len(result) == 64
    
def test_check_file_size(sample_pdf, large_pdf,):
    """Test file size check."""
    # Test file under size limit
    result = check_file_size(sample_pdf, max_size=1024*1024)  # 1MB limit
    assert isinstance(result, int)
    assert result > 0
    
    # Test file over size limit
    result = check_file_size(large_pdf, max_size=1)  # 1 byte limit
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.FILE_TOO_LARGE
    assert 'file_size' in result.details
    assert 'max_size' in result.details

@pytest.mark.parametrize("mime_types,expected_valid", [
    (['application/pdf'], True),
    (['application/x-pdf'], False),
    (['image/jpeg'], False),
    ([], False),
])

def test_check_mime_type(sample_pdf, large_pdf, mime_types, expected_valid):
    """Test mime type check with different mime type lists."""
    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:

        result = check_mime_type(pdf_file, mime_types)
        
        if expected_valid:
            assert isinstance(result, str)
            assert result in mime_types
        else:
            assert isinstance(result, ValidationCheckFailure)
            assert result.check_type == ValidationCheckType.INVALID_MIMETYPE
            assert 'mime_type' in result.details

def test_check_mime_type_corrupt_file(corrupt_pdf):
    """Test mime type check with corrupt file."""
    result = check_mime_type(corrupt_pdf, ['application/pdf'])
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.INVALID_MIMETYPE


def test_check_hash_unique(sample_pdf, large_pdf, mock_db_client):
    """Test hash uniqueness check."""
    

    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:
        # Compute the hash
        file_hash = compute_file_hash(pdf_file)
        
        # Test unique hash
        # - db client returns None if no identical hash found
        mock_db_client.get_document_by_hash.return_value = None
        result = check_hash_unique(pdf_file, file_hash, mock_db_client)
        assert result is True
    
        # Test duplicate hash
        # - db client returns a db.schema.Document obj, which has id attribute
        mock_db_client.get_document_by_hash.return_value = Mock(id="existing_doc_id")
        result = check_hash_unique(pdf_file, file_hash, mock_db_client)
        assert isinstance(result, ValidationCheckFailure)
        assert result.check_type == ValidationCheckType.DUPLICATE_HASH
        assert 'existing_doc_id' in result.details

```
</content>
</file_13>

<file_14>
<path>ingestion_validation/test_schema.py</path>
<content>
```python
"""Tests for validation schemas."""
from pathlib import Path
import pytest
from ragnostic.ingestion.validation.schema import (
    ValidationCheckType,
    ValidationCheckFailure,
    ValidationResult,
    BatchValidationResult,
)


def test_validation_check_failure():
    """Test ValidationCheckFailure creation and properties."""
    failure = ValidationCheckFailure(
        filepath=Path("/test.pdf"),
        check_type=ValidationCheckType.CORRUPTED_FILE,
        message="Test failure",
        details={"extra": "info"}
    )
    
    assert failure.filepath == Path("/test.pdf")
    assert failure.check_type == ValidationCheckType.CORRUPTED_FILE
    assert failure.message == "Test failure"
    assert failure.details == {"extra": "info"}


def test_validation_result():
    """Test ValidationResult creation and properties."""
    # Test valid result
    valid_result = ValidationResult(
        filepath=Path("/test.pdf"),
        is_valid=True,
        file_hash="abc123",
        mime_type="application/pdf",
        file_size_bytes=1024,
    )
    
    assert valid_result.is_valid
    assert valid_result.file_hash == "abc123"
    assert not valid_result.check_failures
    
    # Test invalid result
    failure = ValidationCheckFailure(
        filepath=Path("/test.pdf"),
        check_type=ValidationCheckType.CORRUPTED_FILE,
        message="Test failure"
    )
    
    invalid_result = ValidationResult(
        filepath=Path("/test.pdf"),
        is_valid=False,
        check_failures=[failure]
    )
    
    assert not invalid_result.is_valid
    assert invalid_result.file_hash is None
    assert len(invalid_result.check_failures) == 1


def test_batch_validation_result():
    """Test BatchValidationResult creation and properties."""
    valid_result = ValidationResult(
        filepath=Path("/valid.pdf"),
        is_valid=True,
        file_hash="abc123"
    )
    
    invalid_result = ValidationResult(
        filepath=Path("/invalid.pdf"),
        is_valid=False,
        check_failures=[
            ValidationCheckFailure(
                filepath=Path("/invalid.pdf"),
                check_type=ValidationCheckType.CORRUPTED_FILE,
                message="Test failure"
            )
        ]
    )
    
    batch = BatchValidationResult(
        valid_files=[valid_result],
        invalid_files=[invalid_result]
    )
    
    assert batch.has_valid_files
    assert batch.has_invalid_files
    assert len(batch.valid_files) == 1
    assert len(batch.invalid_files) == 1


def test_empty_batch_validation_result():
    """Test empty BatchValidationResult."""
    batch = BatchValidationResult()
    
    assert not batch.has_valid_files
    assert not batch.has_invalid_files
    assert len(batch.valid_files) == 0
    assert len(batch.invalid_files) == 0
```
</content>
</file_14>

<file_15>
<path>ingestion_validation/test_validator.py</path>
<content>
```python
"""Tests for document validator."""
import pytest
from pathlib import Path
from unittest.mock import Mock

from ragnostic.ingestion.validation.validator import DocumentValidator
from ragnostic.ingestion.validation.schema import ValidationCheckType


def test_validator_init(mock_db_client):
    """Test validator initialization."""
    validator = DocumentValidator(mock_db_client)
    assert validator.max_file_size == 100 * 1024 * 1024
    assert 'application/pdf' in validator.supported_mimetypes
    
    custom_validator = DocumentValidator(
        mock_db_client,
        max_file_size=1024,
        supported_mimetypes=['custom/type']
    )
    assert custom_validator.max_file_size == 1024
    assert custom_validator.supported_mimetypes == ['custom/type']


def test_validate_non_existent_file(mock_db_client, non_existent_pdf):
    """Test validation of non-existent file."""
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(non_existent_pdf)
    
    assert not result.is_valid
    assert len(result.check_failures) == 1
    assert result.check_failures[0].check_type == ValidationCheckType.OTHER


def test_validate_corrupt_file(mock_db_client, corrupt_pdf):
    """Test validation of corrupt file."""
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(corrupt_pdf)
    
    assert not result.is_valid
    assert result.file_hash is None
    assert any(f.check_type == ValidationCheckType.INVALID_MIMETYPE 
              for f in result.check_failures)


def test_validate_large_file(mock_db_client, large_pdf):
    """Test validation of file exceeding size limit."""
    # Verify file is actually larger than limit
    file_size = large_pdf.stat().st_size
    max_size = 1024  # 1KB limit
    assert file_size > max_size, f"Test file size ({file_size} bytes) should be larger than {max_size} bytes"
    
    validator = DocumentValidator(mock_db_client, max_file_size=max_size)
    result = validator._validate_single_file(large_pdf)
    print(result)
    assert not result.is_valid
    assert any(f.check_type == ValidationCheckType.FILE_TOO_LARGE 
              for f in result.check_failures)
    
    assert any(f.details.get('file_size') > f.details.get('max_size')
              for f in result.check_failures)


def test_validate_duplicate_file(mock_db_client, sample_pdf):
    """Test validation of duplicate file."""
    # Mock DB to return existing document
    mock_db_client.get_document_by_hash.return_value = Mock(id="existing_doc")
    
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(sample_pdf)
    
    assert not result.is_valid
    assert any(f.check_type == ValidationCheckType.DUPLICATE_HASH 
              for f in result.check_failures)
    assert any(f.details.get('existing_doc_id') == "existing_doc" 
              for f in result.check_failures)


def test_validate_valid_file(mock_db_client, sample_pdf):
    """Test validation of valid file."""
    # Ensure DB returns no existing document
    mock_db_client.get_document_by_hash.return_value = None
    
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(sample_pdf)
    
    assert result.is_valid
    assert result.file_hash is not None
    assert result.mime_type == "application/pdf"
    assert result.file_size_bytes > 0
    assert not result.check_failures


def test_batch_validation(mock_db_client, sample_pdf, corrupt_pdf, non_existent_pdf):
    """Test batch validation of multiple files."""
    # Ensure DB returns no existing documents
    mock_db_client.get_document_by_hash.return_value = None
    
    validator = DocumentValidator(mock_db_client)
    batch_result = validator.validate_files([
        sample_pdf,
        corrupt_pdf,
        non_existent_pdf
    ])
    
    assert batch_result.has_valid_files
    assert batch_result.has_invalid_files
    assert len(batch_result.valid_files) == 1
    assert len(batch_result.invalid_files) == 2
    
    # Check valid file result
    valid_result = batch_result.valid_files[0]
    assert valid_result.filepath == sample_pdf
    assert valid_result.is_valid
    assert valid_result.file_hash is not None
    assert valid_result.mime_type == "application/pdf"
    
    # Check invalid file results
    invalid_paths = [r.filepath for r in batch_result.invalid_files]
    assert corrupt_pdf in invalid_paths
    assert non_existent_pdf in invalid_paths

```
</content>
</file_15>

<file_16>
<path>test_db.py</path>
<content>
```python
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

```
</content>
</file_16>

<file_17>
<path>test_ingestion_monitor.py</path>
<content>
```python
"""Tests for the ingestion monitor functionality."""
from pathlib import Path
import pytest
from ragnostic.ingestion.monitor import get_ingestible_files
from ragnostic.ingestion.schema import IngestionStatus


@pytest.fixture
def temp_dir_with_files(tmp_path):
    """Create a temporary directory with some test files."""
    # Create test files
    (tmp_path / "test1.pdf").touch()
    (tmp_path / "test2.PDF").touch()
    (tmp_path / "test3.txt").touch()  # Should be ignored
    
    return tmp_path


def test_get_ingestible_files_with_pdfs(temp_dir_with_files):
    """Test finding PDF files in directory."""
    result = get_ingestible_files(temp_dir_with_files)
    
    assert result.status == IngestionStatus.MONITORING
    assert len(result.files) == 2
    assert all(isinstance(f, Path) for f in result.files)
    assert all(f.suffix.lower() == '.pdf' for f in result.files)


def test_get_ingestible_files_nonexistent_dir():
    """Test handling of non-existent directory."""
    result = get_ingestible_files("/nonexistent/path")
    
    assert result.status == IngestionStatus.ERROR
    assert "does not exist" in result.error_message


def test_get_ingestible_files_file_as_dir(temp_dir_with_files):
    """Test handling when path points to a file instead of directory."""
    file_path = temp_dir_with_files / "test1.pdf"
    result = get_ingestible_files(file_path)
    
    assert result.status == IngestionStatus.ERROR
    assert "not a directory" in result.error_message
```
</content>
</file_17>
