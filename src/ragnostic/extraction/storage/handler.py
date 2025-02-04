"""Storage handlers for extracted content."""
import base64
import io
import logging
from pathlib import Path
from PIL import Image
from typing import Optional, Tuple

from ragnostic.db.client import DatabaseClient

from .schema import (
    StorageType,
    StorageLocation,
    ImageMetadata,
    StoredImage,
    StorageResult,
    StorageConfig
)

logger = logging.getLogger(__name__)


class StorageHandler:
    """Handles storage of extracted content."""
    
    def __init__(
        self,
        db_client: DatabaseClient,
        config: StorageConfig,
    ):
        """Initialize storage handler.
        
        Args:
            db_client: Database client for content storage
            config: Storage configuration
        """
        self.db = db_client
        self.config = config
        
        # Ensure storage directory exists
        self.config.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def store_image(
        self,
        image_data: bytes,
        doc_id: str,
        section_id: str,
        caption: Optional[str] = None,
    ) -> StorageResult:
        """Store image using appropriate storage strategy.
        
        Args:
            image_data: Raw image bytes
            doc_id: Document ID
            section_id: Section ID
            caption: Optional image caption
            
        Returns:
            Storage result with location information
        """
        try:
            # Extract image metadata
            metadata = self._extract_image_metadata(image_data)
            
            # Determine storage strategy based on size
            if metadata.size_bytes <= self.config.db_image_size_limit:
                # Store in database
                location = self._store_image_in_db(
                    image_data=image_data,
                    doc_id=doc_id,
                    section_id=section_id,
                    metadata=metadata,
                    caption=caption
                )
            else:
                # Store in filesystem
                location = self._store_image_in_fs(
                    image_data=image_data,
                    doc_id=doc_id,
                    metadata=metadata
                )
            
            return StorageResult(
                content_id=location.reference,
                location=location,
                metadata=metadata.model_dump()
            )
            
        except Exception as e:
            error_msg = f"Failed to store image: {str(e)}"
            logger.exception(error_msg)
            return StorageResult(
                content_id="ERROR",
                location=StorageLocation(
                    storage_type=StorageType.DATABASE,
                    reference="ERROR"
                ),
                error_message=error_msg
            )
    
    def _extract_image_metadata(self, image_data: bytes) -> ImageMetadata:
        """Extract metadata from image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Image metadata
            
        Raises:
            ValueError: If image format not supported
        """
        img = Image.open(io.BytesIO(image_data))
        
        if img.format not in self.config.supported_image_formats:
            raise ValueError(f"Unsupported image format: {img.format}")
        
        return ImageMetadata(
            format=img.format,
            width=img.width,
            height=img.height,
            size_bytes=len(image_data),
            dpi=img.info.get('dpi'),
            color_space=img.mode
        )
    
    def _store_image_in_db(
        self,
        image_data: bytes,
        doc_id: str,
        section_id: str,
        metadata: ImageMetadata,
        caption: Optional[str] = None
    ) -> StorageLocation:
        """Store image in database.
        
        Args:
            image_data: Raw image bytes
            doc_id: Document ID
            section_id: Section ID
            metadata: Image metadata
            caption: Optional image caption
            
        Returns:
            Storage location
        """
        # Convert to base64
        b64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Create database record
        image = self.db.create_image(
            doc_id=doc_id,
            section_id=section_id,
            image_data=b64_data,
            caption=caption,
            page_number=-1  # TODO: Add page number to params
        )
        
        return StorageLocation(
            storage_type=StorageType.DATABASE,
            reference=str(image.id)
        )
    
    def _store_image_in_fs(
        self,
        image_data: bytes,
        doc_id: str,
        metadata: ImageMetadata,
    ) -> StorageLocation:
        """Store image in filesystem.
        
        Args:
            image_data: Raw image bytes
            doc_id: Document ID
            metadata: Image metadata
            
        Returns:
            Storage location
        """
        # Create doc directory if needed
        doc_dir = self.config.storage_dir / doc_id / "images"
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        image_path = doc_dir / f"{doc_id}_{metadata.format.lower()}"
        
        # Save image
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        return StorageLocation(
            storage_type=StorageType.FILESYSTEM,
            reference=str(image_path)
        )
    
    def get_image(self, location: StorageLocation) -> Optional[bytes]:
        """Retrieve image data from storage.
        
        Args:
            location: Storage location information
            
        Returns:
            Raw image bytes if found, None if not found
        """
        try:
            if location.storage_type == StorageType.DATABASE:
                # Get from database
                image = self.db.get_image(int(location.reference))
                if not image:
                    return None
                return base64.b64decode(image.image_data)
                
            else:
                # Get from filesystem
                image_path = Path(location.reference)
                if not image_path.exists():
                    return None
                return image_path.read_bytes()
                
        except Exception as e:
            logger.exception(f"Failed to retrieve image: {str(e)}")
            return None