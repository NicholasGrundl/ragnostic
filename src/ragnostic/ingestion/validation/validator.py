"""High-level document validation logic."""
from pathlib import Path
from typing import List, Optional

from ragnostic.db.client import DatabaseClient
from .schema import ValidationCheckFailure, ValidationCheckType, ValidationResult, BatchValidationResult
from .checks import (
    check_file_hash,
    check_file_exists,
    check_file_size,
    check_mime_type,
    check_hash_unique,
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
        """Validate a single file against all validation checks.
        
        Checks are performed in order of severity and cost:
        1. File existence (fail fast if not found)
        2. File hash (needed for deduplication, fail if corrupted)
        3. Mime type (fail if unsupported type)
        4. File size (fail if too large)
        5. Hash uniqueness (fail if duplicate)
        """
        # Check file exists
        exists_result = check_file_exists(filepath)
        if isinstance(exists_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[exists_result]
            )

        # Check file can be hashed
        hash_result = check_file_hash(filepath)
        if isinstance(hash_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[hash_result]
            )
        file_hash = hash_result
            
        # Check mime type
        mime_result = check_mime_type(filepath, self.supported_mimetypes)
        if isinstance(mime_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[mime_result]
            )
        mime_type = mime_result
            
        # Check file size
        size_result = check_file_size(filepath, self.max_file_size)
        if isinstance(size_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False, 
                check_failures=[size_result]
            )
        file_size = size_result
            
        # Check hash uniqueness
        unique_result = check_hash_unique(filepath, file_hash, self.db_client)
        if isinstance(unique_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[unique_result]
            )
                
        # All checks passed, return successful validation
        return ValidationResult(
            filepath=filepath,
            is_valid=True,
            file_hash=file_hash,
            mime_type=mime_type,
            file_size_bytes=file_size,
            check_failures=[],
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