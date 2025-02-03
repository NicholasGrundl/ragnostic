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