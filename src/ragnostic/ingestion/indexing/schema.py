"""Schema definitions for document indexing."""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class IndexingStatus(str, Enum):
    """Status of document indexing operation."""
    SUCCESS = "success"
    METADATA_ERROR = "metadata_error"
    EXTRACTION_ERROR = "extraction_error"
    DATABASE_ERROR = "database_error"
    UNKNOWN_ERROR = "unknown_error"


class DocumentMetadataExtracted(BaseModel):
    """Optional metadata that requires PDF parsing."""
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    creation_date: Optional[datetime] = None
    page_count: Optional[int] = Field(None, ge=0, description="Total number of pages in document. Must be >= 0 if provided")
    language: Optional[str] = None
    text_preview: Optional[str] = Field(None, description="First page or N characters of text")

    model_config = dict(arbitrary_types_allowed=True)


class IndexingResult(BaseModel):
    """Result of indexing a single document."""
    doc_id: str
    filepath: Path
    status: IndexingStatus
    error_message: Optional[str] = None
    extracted_metadata: Optional[DocumentMetadataExtracted] = None
    
    model_config = dict(arbitrary_types_allowed=True)


class BatchIndexingResult(BaseModel):
    """Results from indexing multiple documents."""
    successful_docs: List[IndexingResult] = Field(default_factory=list)
    failed_docs: List[IndexingResult] = Field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        """Check if any documents failed indexing."""
        return len(self.failed_docs) > 0

    @property
    def success_count(self) -> int:
        """Get count of successfully indexed documents."""
        return len(self.successful_docs)

    @property
    def failure_count(self) -> int:
        """Get count of failed documents."""
        return len(self.failed_docs)