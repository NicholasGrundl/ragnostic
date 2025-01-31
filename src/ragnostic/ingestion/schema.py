"""Pydantic models for the ingestion pipeline."""
from enum import Enum
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class IngestionStatus(str, Enum):
    """Status of the ingestion process."""
    PENDING = "pending"
    MONITORING = "monitoring"
    INGESTING = "ingesting"
    COMPLETED = "completed"
    ERROR = "error"


class MonitorResult(BaseModel):
    """Result of monitoring a directory for files to ingest."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    status: IngestionStatus
    files: List[Path] = Field(default_factory=list)
    error_message: str | None = None

    @property
    def has_files(self) -> bool:
        """Check if any files were found."""
        return len(self.files) > 0


class SupportedFileType(str, Enum):
    """Supported file types for ingestion."""
    PDF = ".pdf"
    PDF_CAPS = ".PDF"  # Some systems might use uppercase extension
    
    @classmethod
    def supported_types(cls) -> set[str]:
        """Get set of all supported file types."""
        return {member.value for member in cls}