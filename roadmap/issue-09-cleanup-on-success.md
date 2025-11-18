# Issue 09: Add Cleanup of Ingestion Source Files Upon Success

**Priority:** Medium
**Estimated Effort:** 0.5-1 day
**Labels:** `feature`, `ingestion`, `enhancement`
**Phase:** 1 - Complete Ingestion

## Problem Statement

From ACTIONITEMS.md: "Cleanup of ingestion upon success"

Current behavior:
- Source files remain in input directory after successful ingestion
- No automatic cleanup mechanism
- Files accumulate over time
- Manual cleanup required
- Risk of re-processing same files

## Current State

After ingestion:
```
input/
├── doc1.pdf    ← Still here after processing
├── doc2.pdf    ← Still here after processing
└── doc3.pdf    ← Still here after processing

storage/
├── abc123.pdf  ← Processed and stored
├── def456.pdf  ← Processed and stored
└── ghi789.pdf  ← Processed and stored
```

**Problems:**
- Source files not removed after successful processing
- Input directory grows indefinitely
- No configurable cleanup strategy
- No archive/backup option before deletion

## Proposed Solution

Implement configurable cleanup strategy with multiple options:

### Option 1: Delete After Success (Simple)
Remove source file immediately after successful indexing.

### Option 2: Move to Archive (Safe)
Move processed files to archive directory with timestamp.

### Option 3: Configurable Retention (Flexible)
Keep files for N days, then delete/archive.

### Recommended Approach: Configurable Cleanup

```python
# src/ragnostic/ingestion/cleanup/cleanup.py
from enum import Enum
from pathlib import Path
from datetime import datetime
import logging
import shutil

logger = logging.getLogger(__name__)

class CleanupStrategy(Enum):
    """Strategy for handling source files after successful ingestion."""
    KEEP = "keep"              # Don't clean up (current behavior)
    DELETE = "delete"          # Delete immediately
    ARCHIVE = "archive"        # Move to archive directory
    ARCHIVE_DATED = "archive_dated"  # Archive with date-based folders

class FileCleanupManager:
    """Manages cleanup of source files after successful ingestion."""

    def __init__(
        self,
        strategy: CleanupStrategy = CleanupStrategy.KEEP,
        archive_dir: Optional[Path] = None,
    ):
        self.strategy = strategy
        self.archive_dir = archive_dir

        if strategy != CleanupStrategy.KEEP and archive_dir:
            archive_dir.mkdir(parents=True, exist_ok=True)

    def cleanup(self, source_file: Path, document_id: str) -> None:
        """Clean up source file according to configured strategy.

        Args:
            source_file: Path to source file
            document_id: ID of successfully ingested document

        Raises:
            FileNotFoundError: If source file doesn't exist
            PermissionError: If insufficient permissions for cleanup
        """
        if not source_file.exists():
            logger.warning(f"Source file not found for cleanup: {source_file}")
            return

        try:
            if self.strategy == CleanupStrategy.KEEP:
                logger.debug(f"Keeping source file: {source_file}")
                return

            elif self.strategy == CleanupStrategy.DELETE:
                logger.info(f"Deleting source file: {source_file}")
                source_file.unlink()

            elif self.strategy == CleanupStrategy.ARCHIVE:
                self._archive_file(source_file, document_id)

            elif self.strategy == CleanupStrategy.ARCHIVE_DATED:
                self._archive_file_dated(source_file, document_id)

            logger.info(f"Cleanup completed for {source_file.name} (strategy: {self.strategy.value})")

        except Exception as e:
            logger.error(f"Failed to cleanup {source_file}: {e}")
            raise

    def _archive_file(self, source_file: Path, document_id: str) -> None:
        """Move file to archive directory."""
        if not self.archive_dir:
            raise ValueError("Archive directory not configured")

        # Use document ID for unique filename
        archive_path = self.archive_dir / f"{document_id}_{source_file.name}"
        logger.info(f"Archiving {source_file} to {archive_path}")
        shutil.move(str(source_file), str(archive_path))

    def _archive_file_dated(self, source_file: Path, document_id: str) -> None:
        """Move file to date-based archive directory."""
        if not self.archive_dir:
            raise ValueError("Archive directory not configured")

        # Create date-based subdirectory (e.g., archive/2025/01/15/)
        date_path = self.archive_dir / datetime.now().strftime("%Y/%m/%d")
        date_path.mkdir(parents=True, exist_ok=True)

        archive_path = date_path / f"{document_id}_{source_file.name}"
        logger.info(f"Archiving {source_file} to {archive_path}")
        shutil.move(str(source_file), str(archive_path))
```

### Configuration

Add to `.env`:
```bash
# Cleanup strategy: keep, delete, archive, archive_dated
CLEANUP_STRATEGY=archive
ARCHIVE_DIRECTORY=./archive
```

### Integration with Workflow

```python
# In ingestion workflow (after successful indexing)
from ragnostic.ingestion.cleanup import FileCleanupManager, CleanupStrategy

class IngestionWorkflow:
    def __init__(self, ..., cleanup_strategy: CleanupStrategy = CleanupStrategy.KEEP):
        # ...
        self.cleanup_manager = FileCleanupManager(
            strategy=cleanup_strategy,
            archive_dir=Path("./archive") if cleanup_strategy != CleanupStrategy.KEEP else None
        )

    def process_document(self, file_path: Path) -> Document:
        # ... existing ingestion logic ...

        # After successful indexing:
        if document.status == "indexed":
            self.cleanup_manager.cleanup(file_path, document.id)

        return document
```

## Acceptance Criteria

- [ ] `FileCleanupManager` class implemented
- [ ] Four cleanup strategies supported (keep, delete, archive, archive_dated)
- [ ] Configuration via environment variables
- [ ] Cleanup only occurs after successful indexing
- [ ] Failed ingestions do not trigger cleanup
- [ ] Proper error handling for permission issues
- [ ] Logging of all cleanup operations
- [ ] Tests for all cleanup strategies
- [ ] Documentation updated
- [ ] `.gitignore` updated to exclude archive directory

## Implementation Steps

1. **Create cleanup module:**
   ```bash
   mkdir -p src/ragnostic/ingestion/cleanup
   touch src/ragnostic/ingestion/cleanup/__init__.py
   touch src/ragnostic/ingestion/cleanup/cleanup.py
   ```

2. **Implement `FileCleanupManager`** (see solution above)

3. **Add configuration:**
   - Update `.env.template` with cleanup settings
   - Add environment variable loading
   - Add validation of cleanup strategy

4. **Integrate with workflow:**
   - Update ingestion workflow to call cleanup after success
   - Ensure cleanup only happens for successfully indexed documents
   - Handle cleanup failures gracefully

5. **Add tests:**
   ```python
   # tests/ingestion_cleanup/test_cleanup.py
   import pytest
   from ragnostic.ingestion.cleanup import FileCleanupManager, CleanupStrategy

   @pytest.mark.fast
   @pytest.mark.unit
   def test_cleanup_delete_strategy(tmp_path):
       """Test DELETE strategy removes file."""
       file = tmp_path / "test.pdf"
       file.write_text("test")

       manager = FileCleanupManager(strategy=CleanupStrategy.DELETE)
       manager.cleanup(file, "doc123")

       assert not file.exists()

   @pytest.mark.fast
   @pytest.mark.unit
   def test_cleanup_archive_strategy(tmp_path):
       """Test ARCHIVE strategy moves file."""
       file = tmp_path / "test.pdf"
       file.write_text("test")
       archive_dir = tmp_path / "archive"

       manager = FileCleanupManager(
           strategy=CleanupStrategy.ARCHIVE,
           archive_dir=archive_dir
       )
       manager.cleanup(file, "doc123")

       assert not file.exists()
       assert (archive_dir / "doc123_test.pdf").exists()

   @pytest.mark.fast
   @pytest.mark.unit
   def test_cleanup_keep_strategy(tmp_path):
       """Test KEEP strategy doesn't remove file."""
       file = tmp_path / "test.pdf"
       file.write_text("test")

       manager = FileCleanupManager(strategy=CleanupStrategy.KEEP)
       manager.cleanup(file, "doc123")

       assert file.exists()
   ```

6. **Update documentation:**
   - Add cleanup section to README
   - Document all cleanup strategies
   - Provide configuration examples

7. **Update `.gitignore`:**
   ```gitignore
   # Archive directory
   archive/
   ```

## Dependencies

**Required before:**
- Issue #03 (package installation)
- Issue #05 (logging for cleanup operations)

**Enhanced by:**
- Issue #08 (integration tests can validate cleanup)

## Testing Strategy

### Unit Tests
- Test each cleanup strategy independently
- Test error handling (permissions, missing files)
- Test configuration validation
- Mock file operations for speed

### Integration Tests
- Test cleanup in full ingestion workflow
- Verify cleanup only happens after successful indexing
- Test cleanup failure doesn't break workflow
- Test with real files and directories

### Edge Cases
- File deleted between indexing and cleanup
- Permission denied during cleanup
- Archive directory doesn't exist
- Disk full during archive
- Invalid cleanup strategy configuration

## Parallel Work Opportunities

Can be worked on **in parallel** with:
- Issue #07 (database refactor)
- Issue #10 (document search)
- Issue #11 (original filename)

Should be worked **after**:
- Issue #03 (package installation)
- Issue #05 (logging)

Can be validated by:
- Issue #08 (integration tests)

## Configuration Examples

### Development (keep files)
```bash
CLEANUP_STRATEGY=keep
```

### Production (archive with dates)
```bash
CLEANUP_STRATEGY=archive_dated
ARCHIVE_DIRECTORY=/var/ragnostic/archive
```

### Testing (delete immediately)
```bash
CLEANUP_STRATEGY=delete
```

## Safety Considerations

1. **Backup before cleanup:**
   - Always use ARCHIVE strategy in production initially
   - Only use DELETE after system is proven stable

2. **Failure handling:**
   - Cleanup failure should not fail entire ingestion
   - Log cleanup failures but continue processing
   - Consider retry mechanism for transient failures

3. **Permissions:**
   - Verify write permissions on archive directory
   - Handle permission errors gracefully
   - Document required permissions

4. **Auditing:**
   - Log all cleanup operations
   - Include document ID, filename, and timestamp
   - Consider keeping cleanup log separate from main log

## Notes

- Consider adding `--dry-run` mode for testing cleanup
- May want to add cleanup statistics to workflow result
- Could add automated cleanup of old archives (future enhancement)
- Consider adding option to compress archived files
- May want notification/webhook on cleanup failures
- Could add cleanup undo functionality (restore from archive)
