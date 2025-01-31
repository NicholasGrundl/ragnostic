"""High-level document validation logic."""
from pathlib import Path
from typing import List, Optional

from ragnostic.db.client import DatabaseClient
from .schema import ValidationCheckFailure, ValidationCheckType, ValidationResult, BatchValidationResult
from .checks import (
    check_file_hash,
    check_file_size,
    check_mime_type,
    check_duplicate,
)

class DocumentValidator:
    """Validates documents before ingestion."""
    
    def __init__(
        self,
        db_client: DatabaseClient,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB default
        supported_mimetypes: Optional[List[str]] = None
    ):
        self.db_client = db_client
        self.max_file_size = max_file_size
        self.supported_mimetypes = supported_mimetypes or [
            'application/pdf',
            'application/x-pdf',
        ]
    
    def _validate_single_file(self, filepath: Path) -> ValidationResult:
        """Validate a single file against all validation checks."""
        check_failures = []
        file_hash = None
        mime_type = None
        
        # Check if file exists and is readable
        if not filepath.exists() or not filepath.is_file():
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[ValidationCheckFailure(
                    filepath=filepath,
                    check_type=ValidationCheckType.OTHER,
                    message="File does not exist or is not a regular file"
                )]
            )
        
        # Run file size check
        if failure := check_file_size(filepath, self.max_file_size):
            check_failures.append(failure)
        
        # Check mime type
        mime_type, failure = check_mime_type(filepath, self.supported_mimetypes)
        if failure:
            check_failures.append(failure)
        
        # Compute hash and check for duplicates
        file_hash, failure = check_file_hash(filepath)
        if failure:
            check_failures.append(failure)
        elif file_hash:  # Only check for duplicates if we got a valid hash
            if failure := check_duplicate(filepath, file_hash, self.db_client):
                check_failures.append(failure)
        
        # Create validation result
        is_valid = len(check_failures) == 0
        metadata = None
        if is_valid:
            metadata = {
                "file_size": filepath.stat().st_size,
                "mime_type": mime_type,
            }
        
        return ValidationResult(
            filepath=filepath,
            is_valid=is_valid,
            file_hash=file_hash,
            check_failures=check_failures,
            metadata=metadata
        )
    
    def validate_files(self, filepaths: List[Path]) -> BatchValidationResult:
        """Validate multiple files and return batch results."""
        results = BatchValidationResult()
        
        for filepath in filepaths:
            result = self._validate_single_file(filepath)
            if result.is_valid:
                results.valid_files.append(result)
            else:
                results.invalid_files.append(result)
        
        return results