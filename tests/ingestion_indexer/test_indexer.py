"""Tests for document indexer functionality."""
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
from ragnostic.ingestion.indexing import DocumentIndexer
from ragnostic.ingestion.indexing.schema import IndexingStatus
from ragnostic.db.schema import DocumentCreate, DocumentMetadataCreate


def test_indexer_initialization(mock_db_client):
    """Test DocumentIndexer initialization."""
    indexer = DocumentIndexer(mock_db_client)
    assert indexer.db_client == mock_db_client
    assert indexer.extractor is not None


def test_successful_indexing(mock_db_client, mock_pdf_processor, sample_pdf_path):
    """Test successful document indexing with metadata."""
    with patch('pymupdf4llm.PDFProcessor', return_value=mock_pdf_processor):
        indexer = DocumentIndexer(mock_db_client)
        result = indexer.index_document(sample_pdf_path)
        
        # Check result
        assert result.status == IndexingStatus.SUCCESS
        assert result.doc_id == "DOC123"
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
        assert metadata_create.doc_id == "DOC123"


def test_indexing_without_metadata(mock_db_client, mock_pdf_processor, sample_pdf_path):
    """Test successful document indexing when metadata extraction fails."""
    # Make metadata extraction return None
    with patch('pymupdf4llm.PDFProcessor', side_effect=Exception("PDF Error")):
        indexer = DocumentIndexer(mock_db_client)
        result = indexer.index_document(sample_pdf_path)
        
        # Document should still be created
        assert result.status == IndexingStatus.SUCCESS
        assert result.doc_id == "DOC123"
        
        # Document created but not metadata
        mock_db_client.create_document.assert_called_once()
        mock_db_client.create_metadata.assert_not_called()


def test_indexing_with_database_error(mock_db_client, mock_pdf_processor, sample_pdf_path):
    """Test handling of database errors during indexing."""
    # Make document creation fail
    mock_db_client.create_document.side_effect = ValueError("Document already exists")
    
    with patch('pymupdf4llm.PDFProcessor', return_value=mock_pdf_processor):
        indexer = DocumentIndexer(mock_db_client)
        result = indexer.index_document(sample_pdf_path)
        
        assert result.status == IndexingStatus.DATABASE_ERROR
        assert "Document already exists" in result.error_message
        assert result.doc_id == str(sample_pdf_path.stem)
        
        # Metadata should not be attempted
        mock_db_client.create_metadata.assert_not_called()


def test_batch_indexing_success(mock_db_client, mock_pdf_processor, multiple_pdf_paths):
    """Test successful batch indexing of multiple documents."""
    with patch('pymupdf4llm.PDFProcessor', return_value=mock_pdf_processor):
        indexer = DocumentIndexer(mock_db_client)
        results = indexer.index_batch(multiple_pdf_paths)
        
        assert results.success_count == len(multiple_pdf_paths)
        assert results.failure_count == 0
        assert not results.has_failures
        
        # Verify database calls
        assert mock_db_client.create_document.call_count == len(multiple_pdf_paths)
        assert mock_db_client.create_metadata.call_count == len(multiple_pdf_paths)


def test_batch_indexing_with_failures(mock_db_client, mock_pdf_processor, multiple_pdf_paths):
    """Test batch indexing with mixed success and failures."""
    def mock_create_doc(doc):
        # Make every other document fail
        if "test_1" in doc.raw_file_path:
            raise ValueError("Database error")
        return mock_db_client.create_document.return_value
    
    mock_db_client.create_document.side_effect = mock_create_doc
    
    with patch('pymupdf4llm.PDFProcessor', return_value=mock_pdf_processor):
        indexer = DocumentIndexer(mock_db_client)
        results = indexer.index_batch(multiple_pdf_paths)
        
        assert results.success_count == 2
        assert results.failure_count == 1
        assert results.has_failures
        
        # Check failed document details
        failed_doc = results.failed_docs[0]
        assert failed_doc.status == IndexingStatus.DATABASE_ERROR
        assert "Database error" in failed_doc.error_message


def test_indexing_with_corrupted_file(mock_db_client, corrupted_pdf_path):
    """Test handling of corrupted PDF files."""
    with patch('magic.from_file', side_effect=Exception("Invalid file")):
        indexer = DocumentIndexer(mock_db_client)
        result = indexer.index_document(corrupted_pdf_path)
        
        assert result.status == IndexingStatus.UNKNOWN_ERROR
        assert "Invalid file" in result.error_message
        assert not mock_db_client.create_document.called
        assert not mock_db_client.create_metadata.called


def test_metadata_creation_error(mock_db_client, mock_pdf_processor, sample_pdf_path):
    """Test handling of metadata creation errors."""
    # Make metadata creation fail
    mock_db_client.create_metadata.side_effect = ValueError("Metadata error")
    
    with patch('pymupdf4llm.PDFProcessor', return_value=mock_pdf_processor):
        indexer = DocumentIndexer(mock_db_client)
        result = indexer.index_document(sample_pdf_path)
        
        # Document should still be successful even if metadata fails
        assert result.status == IndexingStatus.SUCCESS
        assert result.doc_id == "DOC123"
        
        # Verify both calls were attempted
        mock_db_client.create_document.assert_called_once()
        mock_db_client.create_metadata.assert_called_once()


def test_text_extraction_options(mock_db_client, mock_pdf_processor, sample_pdf_path):
    """Test different text extraction configurations."""
    with patch('pymupdf4llm.PDFProcessor', return_value=mock_pdf_processor):
        # Test with text extraction disabled
        indexer = DocumentIndexer(mock_db_client, extract_text=False)
        result = indexer.index_document(sample_pdf_path)
        assert result.extracted_metadata.text_preview is None
        
        # Test with custom preview length
        indexer = DocumentIndexer(mock_db_client, extract_text=True, text_preview_chars=50)
        result = indexer.index_document(sample_pdf_path)
        assert result.extracted_metadata.text_preview is not None
        assert len(result.extracted_metadata.text_preview) <= 50


def test_empty_batch_indexing(mock_db_client):
    """Test batch indexing with empty list."""
    indexer = DocumentIndexer(mock_db_client)
    results = indexer.index_batch([])
    
    assert results.success_count == 0
    assert results.failure_count == 0
    assert not results.has_failures
    assert not mock_db_client.create_document.called
    assert not mock_db_client.create_metadata.called