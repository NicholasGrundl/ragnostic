"""Core schemas for the extraction system."""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Types of content that can be extracted."""
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"


class ContentLocation(BaseModel):
    """Location of content within document."""
    page: int
    bbox: tuple[float, float, float, float] = Field(
        description="Bounding box coordinates (x1, y1, x2, y2)"
    )
    

class ExtractedContent(BaseModel):
    """Base class for extracted content."""
    content_type: ContentType
    content_id: str = Field(description="Unique identifier for this content")
    location: ContentLocation
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Confidence score for extraction"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedText(ExtractedContent):
    """Text content extracted from document."""
    content_type: ContentType = ContentType.TEXT
    text: str
    is_header: bool = False
    header_level: Optional[int] = Field(
        None, ge=1, le=6,
        description="Header level (1-6) if is_header=True"
    )


class ExtractedImage(ExtractedContent):
    """Image extracted from document."""
    content_type: ContentType = ContentType.IMAGE
    image_data: str = Field(description="base 64 encoded image data")
    format: str = Field(description="Image format (e.g., 'png', 'jpg')")
    size_bytes: int = Field(description="Size of image in bytes")
    caption: Optional[str] = None


class ExtractedTable(ExtractedContent):
    """Table extracted from document."""
    content_type: ContentType = ContentType.TABLE
    table_data: List[List[str]] = Field(description="Table data as 2D array")
    headers: Optional[List[str]] = None
    caption: Optional[str] = None



class ExtractionError(BaseModel):
    """Error encountered during extraction."""
    error_type: str
    message: str
    page_number: Optional[int] = None
    section_id: Optional[str] = None
    recoverable: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """Results of document extraction."""
    doc_id: str
    content: List[ExtractedContent] = Field(default_factory=list)
    extraction_date: datetime = Field(
        default_factory=lambda: datetime.now(datetime.UTC)
    )
    extractor_name: str
    error_messages: List[ExtractionError] = Field(default_factory=list)