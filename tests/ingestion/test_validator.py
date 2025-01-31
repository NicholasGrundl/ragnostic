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
