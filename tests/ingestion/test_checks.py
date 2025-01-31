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

@pytest.mark.parametrize("pdf_file", [
    pytest.param(pytest.lazy_fixture("sample_pdf")),
    pytest.param(pytest.lazy_fixture("large_pdf"))
])
def test_compute_file_hash(pdf_file):
    """Test computing file hash."""
    # Test valid file
    hash_value = compute_file_hash(pdf_file)
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA-256 produces 64 character hex string
    
    # Test same file produces same hash
    assert compute_file_hash(pdf_file) == hash_value
    
    # Test non-existent file
    assert compute_file_hash(Path("nonexistent.pdf")) is None

@pytest.mark.parametrize("pdf_file", ["sample_pdf", "large_pdf"], indirect=True)
def test_check_file_exists(pdf_file, non_existent_pdf, tmp_path):
    """Test file existence check."""
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

@pytest.mark.parametrize("pdf_file", ["sample_pdf", "large_pdf"], indirect=True)
def test_check_file_hash(pdf_file, corrupt_pdf):
    """Test file hash check."""
    # Test valid file
    result = check_file_hash(pdf_file)
    assert isinstance(result, str)
    assert len(result) == 64
    
    # Test corrupt file
    result = check_file_hash(corrupt_pdf)
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.CORRUPTED_FILE

@pytest.mark.parametrize("pdf_file", ["sample_pdf", "large_pdf"], indirect=True)
def test_check_file_size(pdf_file):
    """Test file size check."""
    # Test file under size limit
    result = check_file_size(pdf_file, max_size=1024*1024)  # 1MB limit
    assert isinstance(result, int)
    assert result > 0
    
    # Test file over size limit
    result = check_file_size(pdf_file, max_size=1)  # 1 byte limit
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.FILE_TOO_LARGE
    assert 'file_size' in result.details
    assert 'max_size' in result.details


@pytest.mark.parametrize("mime_types,expected_valid", [
    (['application/pdf'], True),
    (['application/x-pdf'], True),
    (['image/jpeg'], False),
    ([], False),
])
@pytest.mark.parametrize("pdf_file", ["sample_pdf", "large_pdf"], indirect=True)
def test_check_mime_type(pdf_file, mime_types, expected_valid):
    """Test mime type check with different mime type lists."""
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

@pytest.mark.parametrize("pdf_file", ["sample_pdf", "large_pdf"], indirect=True)
def test_check_hash_unique(pdf_file, mock_db_client):
    """Test hash uniqueness check."""
    file_hash = "test_hash_123"
    
    # Test unique hash
    mock_db_client.get_document_by_hash.return_value = None
    result = check_hash_unique(pdf_file, file_hash, mock_db_client)
    assert result is True
    
    # Test duplicate hash
    mock_db_client.get_document_by_hash.return_value = Mock(id="existing_doc")
    result = check_hash_unique(pdf_file, file_hash, mock_db_client)
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.DUPLICATE_HASH
    assert 'existing_doc_id' in result.details
