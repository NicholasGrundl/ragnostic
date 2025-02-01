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