"""Core extraction interfaces and implementations."""
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol, Iterator, Optional

from .schema import ExtractionResult


class DocumentExtractor(Protocol):
    """Protocol for document extractors."""
    
    @property
    def name(self) -> str:
        """Name of the extractor."""
        ...
    
    def extract_document(self, file_path: Path) -> ExtractionResult:
        """Extract content from document.
        
        Args:
            file_path: Path to document to process
            
        Returns:
            Extraction results including all content and sections
            
        Raises:
            ExtractionError: If extraction fails
        """
        ...


class ExtractionProgress(ABC):
    """Abstract base class for tracking extraction progress."""
    
    def __init__(self, doc_id: str, total_pages: int):
        """Initialize progress tracker.
        
        Args:
            doc_id: Document ID being processed
            total_pages: Total pages in document
        """
        self.doc_id = doc_id
        self.total_pages = total_pages
        self.current_page = 0
        self.section_count = 0
        self.image_count = 0
        self.table_count = 0
    
    @property
    def progress(self) -> float:
        """Current progress as percentage."""
        return self.current_page / max(1, self.total_pages)
    
    @abstractmethod
    def update(
        self,
        page: Optional[int] = None,
        sections: int = 0,
        images: int = 0,
        tables: int = 0
    ) -> None:
        """Update progress counts.
        
        Args:
            page: Current page number if changed
            sections: Number of new sections found
            images: Number of new images found
            tables: Number of new tables found
        """
        if page is not None:
            self.current_page = page
        self.section_count += sections
        self.image_count += images
        self.table_count += tables


@contextmanager
def track_extraction(doc_id: str, total_pages: int) -> Iterator[ExtractionProgress]:
    """Context manager for tracking extraction progress.
    
    Args:
        doc_id: Document ID being processed
        total_pages: Total pages in document
        
    Yields:
        Progress tracker instance
    """
    tracker = ExtractionProgress(doc_id, total_pages)
    try:
        yield tracker
    finally:
        # Log final statistics
        pass  # TODO: Add logging