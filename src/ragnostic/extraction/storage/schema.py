"""Storage schemas for the extraction system."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class StorageType(str, Enum):
    """Type of storage used for content."""
    DATABASE = "database"
    FILESYSTEM = "filesystem"


class StorageLocation(BaseModel):
    """Location of stored content."""
    storage_type: StorageType
    reference: str = Field(description="Database ID or filesystem path")
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))


class ImageMetadata(BaseModel):
    """Metadata for stored image."""
    format: str
    width: int
    height: int
    size_bytes: int
    dpi: Optional[tuple[int, int]] = None
    color_space: Optional[str] = None
    
    
class StoredImage(BaseModel):
    """Details about a stored image."""
    image_id: str
    doc_id: str
    section_id: str
    location: StorageLocation
    metadata: ImageMetadata
    caption: Optional[str] = None


class StorageResult(BaseModel):
    """Result of storage operation."""
    content_id: str
    location: StorageLocation
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class StorageConfig:
    """Configuration for storage system."""
    storage_dir: Path
    db_image_size_limit: int = 1_000_000  # 1MB default
    supported_image_formats: set[str] = Field(
        default_factory=lambda: {"PNG", "JPEG", "JPG"}
    )