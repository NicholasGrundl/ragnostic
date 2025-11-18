# Issue 08: Add Integration Tests for Ingestion Flow

**Priority:** High
**Estimated Effort:** 2-3 days
**Labels:** `testing`, `integration`, `quality`
**Phase:** 1 - Complete Ingestion

## Problem Statement

From ACTIONITEMS.md: "Integration test for ingestion flow"

Current state:
- Unit tests exist for individual components (72 tests, 1,629 LOC)
- No end-to-end integration tests for complete workflow
- Components tested in isolation only
- No validation that pipeline stages work together
- Edge cases and failure modes not tested comprehensively

## Current State

**Existing Tests:**
- `test_monitor.py` - Directory monitoring (unit)
- `test_validator.py` - Document validation (unit)
- `test_processor.py` - Document processing (unit)
- `test_indexer.py` - Document indexing (unit)
- `test_db.py` - Database operations (unit)

**Missing:**
- End-to-end workflow tests
- Error propagation between stages
- State management across pipeline
- Recovery from failures
- Concurrent document processing

## Proposed Solution

Create comprehensive integration test suite for the complete ingestion pipeline:

```
Monitor → Validate → Process → Index
   ↓         ↓          ↓        ↓
  (1)       (2)        (3)      (4)
```

Test scenarios:
1. Happy path (successful ingestion)
2. Duplicate detection
3. Invalid documents (various failure modes)
4. Error recovery and rollback
5. Batch processing
6. State persistence

### Test Structure

Create `tests/integration/test_ingestion_workflow.py`:

```python
import pytest
from pathlib import Path
from ragnostic.db import DatabaseClient
from ragnostic.ingestion.workflow import IngestionWorkflow

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.workflow
class TestIngestionWorkflowIntegration:
    """Integration tests for complete ingestion pipeline."""

    def test_successful_single_document_ingestion(
        self, tmp_path: Path, db_client: DatabaseClient, sample_pdf: Path
    ):
        """Test successful ingestion of a single PDF document.

        Validates:
        - File is discovered by monitor
        - Document passes validation
        - File is copied to storage
        - Metadata is extracted and indexed
        - Database record is created
        - Workflow state transitions correctly
        """
        # Setup: Copy sample PDF to monitored directory
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        test_pdf = input_dir / "test.pdf"
        test_pdf.write_bytes(sample_pdf.read_bytes())

        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Execute: Run ingestion workflow
        workflow = IngestionWorkflow(
            input_directory=str(input_dir),
            storage_directory=str(storage_dir),
            db_client=db_client,
        )
        result = workflow.run()

        # Assert: Workflow succeeded
        assert result.status == "completed"
        assert result.documents_processed == 1
        assert result.documents_failed == 0

        # Assert: File copied to storage
        stored_files = list(storage_dir.glob("*.pdf"))
        assert len(stored_files) == 1

        # Assert: Database record created
        docs = db_client.get_all_documents()
        assert len(docs) == 1
        doc = docs[0]
        assert doc.original_filename == "test.pdf"
        assert doc.status == "indexed"
        assert doc.page_count is not None

    def test_duplicate_document_handling(
        self, tmp_path: Path, db_client: DatabaseClient, sample_pdf: Path
    ):
        """Test that duplicate documents are detected and rejected.

        Validates:
        - First ingestion succeeds
        - Second ingestion of same file is rejected
        - Database has only one record
        - Duplicate is not stored twice
        """
        # Setup
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        workflow = IngestionWorkflow(
            input_directory=str(input_dir),
            storage_directory=str(storage_dir),
            db_client=db_client,
        )

        # First ingestion
        test_pdf = input_dir / "test.pdf"
        test_pdf.write_bytes(sample_pdf.read_bytes())
        result1 = workflow.run()
        assert result1.documents_processed == 1

        # Second ingestion (duplicate)
        test_pdf2 = input_dir / "test_copy.pdf"
        test_pdf2.write_bytes(sample_pdf.read_bytes())  # Same content, different name
        result2 = workflow.run()

        # Assert: Duplicate detected
        assert result2.documents_skipped == 1
        assert result2.documents_processed == 0

        # Assert: Only one database record
        docs = db_client.get_all_documents()
        assert len(docs) == 1

    def test_invalid_document_handling(
        self, tmp_path: Path, db_client: DatabaseClient
    ):
        """Test handling of invalid documents.

        Validates:
        - Invalid PDF is rejected
        - Error is logged appropriately
        - No database record created
        - Workflow continues processing other files
        """
        # Setup
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        # Create invalid PDF (corrupted file)
        invalid_pdf = input_dir / "invalid.pdf"
        invalid_pdf.write_text("This is not a valid PDF")

        # Execute
        workflow = IngestionWorkflow(
            input_directory=str(input_dir),
            storage_directory=str(storage_dir),
            db_client=db_client,
        )
        result = workflow.run()

        # Assert: Document rejected
        assert result.documents_failed == 1
        assert result.documents_processed == 0

        # Assert: No database record
        docs = db_client.get_all_documents()
        assert len(docs) == 0

        # Assert: Error logged
        assert len(result.errors) == 1
        error = result.errors[0]
        assert "invalid.pdf" in error.filename
        assert "validation" in error.stage.lower()

    def test_batch_ingestion(
        self, tmp_path: Path, db_client: DatabaseClient, sample_pdfs: List[Path]
    ):
        """Test ingestion of multiple documents in batch.

        Validates:
        - Multiple documents processed
        - Processing order maintained
        - All valid documents succeed
        - Invalid documents don't block batch
        - Database has correct number of records
        """
        # Setup: 10 PDFs (8 valid, 2 invalid)
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        storage_dir = tmp_path / "storage"
        storage_dir.mkdir()

        for i, pdf_path in enumerate(sample_pdfs[:8]):
            dest = input_dir / f"doc_{i:03d}.pdf"
            dest.write_bytes(pdf_path.read_bytes())

        # Add 2 invalid files
        (input_dir / "invalid_1.pdf").write_text("invalid")
        (input_dir / "invalid_2.pdf").write_text("invalid")

        # Execute
        workflow = IngestionWorkflow(
            input_directory=str(input_dir),
            storage_directory=str(storage_dir),
            db_client=db_client,
        )
        result = workflow.run()

        # Assert: Correct counts
        assert result.documents_processed == 8
        assert result.documents_failed == 2
        assert result.total_documents == 10

        # Assert: Database has 8 records
        docs = db_client.get_all_documents()
        assert len(docs) == 8

        # Assert: All valid documents stored
        stored_files = list(storage_dir.glob("*.pdf"))
        assert len(stored_files) == 8

    def test_workflow_state_persistence(
        self, tmp_path: Path, db_client: DatabaseClient, sample_pdf: Path
    ):
        """Test that workflow state persists across interruptions.

        Validates:
        - State is saved after each stage
        - Workflow can resume from last checkpoint
        - Partial progress is not lost
        """
        # This test validates the Burr workflow state management
        # Implementation depends on Burr configuration

    def test_error_recovery(
        self, tmp_path: Path, db_client: DatabaseClient, sample_pdf: Path
    ):
        """Test error recovery and rollback mechanisms.

        Validates:
        - Database transaction rollback on error
        - Files not copied if indexing fails
        - Workflow can continue after error
        """
        # Test implementation

    def test_concurrent_ingestion(
        self, tmp_path: Path, db_client: DatabaseClient, sample_pdfs: List[Path]
    ):
        """Test concurrent processing of multiple documents.

        Validates:
        - Multiple workflows can run simultaneously
        - No race conditions in database writes
        - File locking prevents conflicts
        """
        # Test implementation for future concurrent processing feature
```

## Acceptance Criteria

- [ ] Integration test file created: `tests/integration/test_ingestion_workflow.py`
- [ ] Happy path test covers full pipeline
- [ ] Duplicate detection tested
- [ ] Invalid document handling tested
- [ ] Batch processing tested
- [ ] Error scenarios tested
- [ ] Tests marked with appropriate pytest markers (`@pytest.mark.slow`, `@pytest.mark.integration`)
- [ ] All tests pass
- [ ] Test coverage for integration tests documented
- [ ] CI/CD configured to run integration tests

## Implementation Steps

1. **Create test structure:**
   ```bash
   mkdir -p tests/integration
   touch tests/integration/__init__.py
   touch tests/integration/test_ingestion_workflow.py
   ```

2. **Create fixtures:**
   ```python
   # tests/integration/conftest.py
   import pytest
   from pathlib import Path

   @pytest.fixture
   def sample_pdf() -> Path:
       """Provide a valid sample PDF for testing."""
       return Path("data/article/sample.pdf")

   @pytest.fixture
   def sample_pdfs() -> List[Path]:
       """Provide multiple sample PDFs."""
       return list(Path("data").glob("**/*.pdf"))[:10]
   ```

3. **Implement tests** (see solution section above)

4. **Add to pytest configuration:**
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   # Integration tests are slow
   markers = [
       "workflow: end-to-end workflow tests (slow)",
   ]
   ```

5. **Update Makefile:**
   ```makefile
   .PHONY: test-integration test-workflow

   test-integration:
       pytest tests/integration/ -v

   test-workflow:
       pytest -m workflow -v
   ```

6. **Document in README:**
   ```markdown
   ## Integration Tests

   Run integration tests (requires sample PDFs in data/):
   ```bash
   make test-integration
   ```

   These tests are slower as they test the complete pipeline.
   ```

## Dependencies

**Required before:**
- Issue #03 (package installation)
- Issue #06 (pytest markers)

**Enhanced by:**
- Issue #05 (logging helps debug test failures)
- Issue #07 (cleaner architecture easier to test)

**Uses:**
- Sample PDFs in `data/` directory (already exist)

## Testing Strategy

### Test Data Requirements

- Valid PDF samples (already in `data/`)
- Invalid/corrupted PDFs (create for testing)
- PDFs with various characteristics:
  - Different sizes
  - Different page counts
  - With/without metadata
  - Different document types (article, journal, report, textbook)

### Performance Benchmarks

Integration tests should complete reasonably:
- Single document: <5 seconds
- Batch (10 documents): <30 seconds
- Mark as `@pytest.mark.slow` for CI/CD optimization

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #05 (logging)
- Issue #09 (cleanup on success)
- Issue #11 (original filename)

Should be worked **after**:
- Issue #03 (package installation)
- Issue #06 (pytest markers)

Can be worked **before or after**:
- Issue #07 (database refactor - tests ensure refactor doesn't break anything)

## Coverage Goals

Integration tests should achieve:
- [ ] 100% coverage of workflow orchestration code
- [ ] All error paths exercised
- [ ] All stage transitions validated
- [ ] Edge cases covered

## Notes

- Integration tests use real SQLite database (in-memory or temp file)
- Tests should clean up resources (temp files, database) in teardown
- Consider using `pytest-timeout` to prevent hanging tests
- May want to add performance regression tests
- Consider adding stress tests (large files, many documents)
- Use `pytest-xdist` for parallel test execution (future)
