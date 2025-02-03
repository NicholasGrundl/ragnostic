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