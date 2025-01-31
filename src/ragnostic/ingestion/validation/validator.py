"""Validation logic for ingestion pipeline."""
import hashlib
from pathlib import Path
from typing import List, Optional
import magic  # python-magic for mime type detection

from ragnostic.db.client import DatabaseClient
from .schema import (
    ValidationResult,
    BatchValidationResult,
    ValidationError,
    ValidationErrorType,
)

class DocumentValidator:
    """Validates documents before ingestion."""
    
    def __init__(
        self,
        db_client: DatabaseClient,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB default
        supported_mimetypes: Optional[List[str]] = None
    ):
        """Initialize validator with configuration.
        
        Args:
            db_client: Database client for checking duplicates
            max_file_size: Maximum file size in bytes
            supported_mimetypes: List of supported mime types. If None, defaults to
                               PDF types only.
        """
        self.db_client = db_client
        self.max_file_size = max_file_size
        self.supported_mimetypes = supported_mimetypes or [
            'application/pdf',
            'application/x-pdf',
        ]
    
    def _compute_file_hash(self, filepath: Path) -> Optional[str]:
        """Compute SHA-256 hash of file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None
    
    def _validate_single_file(self, filepath: Path) -> ValidationResult:
        """Validate a single file against all validation rules."""
        errors: List[ValidationError] = []
        file_hash: Optional[str] = None
        
        # Check if file exists and is readable
        if not filepath.exists() or not filepath.is_file():
            errors.append(ValidationError(
                filepath=filepath,
                error_type=ValidationErrorType.OTHER,
                message="File does not exist or is not a regular file"
            ))
            return ValidationResult(filepath=filepath, is_valid=False, errors=errors)
        
        # Check file size
        try:
            file_size = filepath.stat().st_size
            if file_size > self.max_file_size:
                errors.append(ValidationError(
                    filepath=filepath,
                    error_type=ValidationErrorType.FILE_TOO_LARGE,
                    message=f"File exceeds maximum size of {self.max_file_size} bytes",
                    details={"file_size": file_size, "max_size": self.max_file_size}
                ))
        except Exception as e:
            errors.append(ValidationError(
                filepath=filepath,
                error_type=ValidationErrorType.PERMISSION_ERROR,
                message=f"Unable to check file size: {str(e)}"
            ))
        
        # Check mime type
        try:
            mime_type = magic.from_file(str(filepath), mime=True)
            if mime_type not in self.supported_mimetypes:
                errors.append(ValidationError(
                    filepath=filepath,
                    error_type=ValidationErrorType.INVALID_MIMETYPE,
                    message=f"Unsupported mime type: {mime_type}",
                    details={"mime_type": mime_type}
                ))
        except Exception as e:
            errors.append(ValidationError(
                filepath=filepath,
                error_type=ValidationErrorType.OTHER,
                message=f"Unable to determine mime type: {str(e)}"
            ))
        
        # Compute hash and check for duplicates
        file_hash = self._compute_file_hash(filepath)
        if file_hash:
            existing_doc = self.db_client.get_document_by_hash(file_hash)
            if existing_doc:
                errors.append(ValidationError(
                    filepath=filepath,
                    error_type=ValidationErrorType.DUPLICATE_HASH,
                    message="Document with same hash already exists",
                    details={"existing_doc_id": existing_doc.id}
                ))
        else:
            errors.append(ValidationError(
                filepath=filepath,
                error_type=ValidationErrorType.CORRUPTED_FILE,
                message="Unable to compute file hash"
            ))
        
        # Create validation result
        is_valid = len(errors) == 0
        metadata = None
        if is_valid:
            metadata = {
                "file_size": file_size,
                "mime_type": mime_type,
            }
        
        return ValidationResult(
            filepath=filepath,
            is_valid=is_valid,
            file_hash=file_hash,
            errors=errors,
            metadata=metadata
        )
    
    def validate_files(self, filepaths: List[Path]) -> BatchValidationResult:
        """Validate multiple files and return batch results.
        
        Args:
            filepaths: List of paths to validate
            
        Returns:
            BatchValidationResult containing valid and invalid files
        """
        results = BatchValidationResult()
        
        for filepath in filepaths:
            result = self._validate_single_file(filepath)
            if result.is_valid:
                results.valid_files.append(result)
            else:
                results.invalid_files.append(result)
        
        return results