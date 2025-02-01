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