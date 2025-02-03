"""Validation schemas for the ingestion pipeline."""
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

class ValidationCheckType(str, Enum):
    """Types of validation check failures that can occur."""
    DUPLICATE_HASH = "duplicate_hash"
    INVALID_MIMETYPE = "invalid_mimetype"
    CORRUPTED_FILE = "corrupted_file"
    FILE_TOO_LARGE = "file_too_large"
    PERMISSION_ERROR = "permission_error"
    OTHER = "other"

class ValidationCheckFailure(BaseModel):
    """Represents a validation check failure for a file."""
    filepath: Path
    check_type: ValidationCheckType
    message: str
    details: Optional[dict] = Field(default=None, description="Additional check details")

class ValidationResult(BaseModel):
    """Result of validating a single file."""
    filepath: Path
    is_valid: bool
    file_hash: Optional[str] = Field(default=None, description="Hash of the file")
    mime_type: Optional[str] = Field(default=None, description="MIME type of the file")
    file_size_bytes: Optional[int] = Field(default=None, description="Size of the file in bytes")
    check_failures: List[ValidationCheckFailure] = Field(default_factory=list)

class BatchValidationResult(BaseModel):
    """Results from validating multiple files."""
    valid_files: List[ValidationResult] = Field(default_factory=list)
    invalid_files: List[ValidationResult] = Field(default_factory=list)
    
    @property
    def has_valid_files(self) -> bool:
        return len(self.valid_files) > 0
    
    @property
    def has_invalid_files(self) -> bool:
        return len(self.invalid_files) > 0