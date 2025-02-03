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