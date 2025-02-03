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