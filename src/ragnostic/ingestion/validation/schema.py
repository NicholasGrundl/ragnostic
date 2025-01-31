"""Validation schemas for the ingestion pipeline."""
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

class ValidationErrorType(str, Enum):
    """Types of validation errors that can occur."""
    DUPLICATE_HASH = "duplicate_hash"
    INVALID_MIMETYPE = "invalid_mimetype"
    CORRUPTED_FILE = "corrupted_file"
    FILE_TOO_LARGE = "file_too_large"
    PERMISSION_ERROR = "permission_error"
    OTHER = "other"

class ValidationError(BaseModel):
    """Represents a validation error for a file."""
    filepath: Path
    error_type: ValidationErrorType
    message: str
    details: Optional[dict] = Field(default=None, description="Additional error details")

class ValidationResult(BaseModel):
    """Result of validating a single file."""
    filepath: Path
    is_valid: bool
    file_hash: Optional[str] = None
    errors: List[ValidationError] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default=None, description="File metadata if validation successful")

class BatchValidationResult(BaseModel):
    """Results from validating multiple files."""
    valid_files: List[ValidationResult] = Field(default_factory=list)
    invalid_files: List[ValidationResult] = Field(default_factory=list)
    
    @property
    def has_valid_files(self) -> bool:
        """Check if any files passed validation."""
        return len(self.valid_files) > 0
    
    @property
    def has_invalid_files(self) -> bool:
        """Check if any files failed validation."""
        return len(self.invalid_files) > 0