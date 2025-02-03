"""Schema definitions for document processing."""
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Status of document processing operation."""
    SUCCESS = "success"
    STORAGE_ERROR = "storage_error"
    COPY_ERROR = "copy_error"
    RENAME_ERROR = "rename_error"
    UNKNOWN_ERROR = "unknown_error"


class ProcessingResult(BaseModel):
    """Result of processing a single document."""
    doc_id: str
    original_path: Path
    storage_path: Optional[Path] = None
    status: ProcessingStatus
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    model_config = dict(arbitrary_types_allowed=True)


class BatchProcessingResult(BaseModel):
    """Results from processing multiple documents."""
    successful_docs: List[ProcessingResult] = Field(default_factory=list)
    failed_docs: List[ProcessingResult] = Field(default_factory=list)

    model_config = dict(arbitrary_types_allowed=True)

    @property
    def has_failures(self) -> bool:
        """Check if any documents failed processing."""
        return len(self.failed_docs) > 0

    @property
    def success_count(self) -> int:
        """Get count of successfully processed documents."""
        return len(self.successful_docs)

    @property
    def failure_count(self) -> int:
        """Get count of failed documents."""
        return len(self.failed_docs)