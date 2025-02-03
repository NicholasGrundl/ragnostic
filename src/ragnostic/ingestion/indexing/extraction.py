"""PDF metadata and text extraction functionality."""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf4llm

from .schema import DocumentMetadataExtracted

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles PDF metadata and text extraction using pymupdf4llm."""
    
    def __init__(self, text_preview_chars: int = 1000):
        """Initialize the PDF extractor.
        
        Args:
            extract_text: Whether to extract text preview
            text_preview_chars: Number of characters to extract for preview
        """
        self.text_preview_chars = text_preview_chars
    
    def extract_metadata(self, filepath: Path) -> Tuple[Optional[DocumentMetadataExtracted], Optional[str]]:
        """Extract metadata and optional text preview from PDF.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Tuple of (metadata, error_message)
            If successful, error_message will be None
        """
        try:
            # Open PDF with pymupdf4llm
            page_chunks  = pymupdf4llm.to_markdown(str(filepath), page_chunks=True)
            
            # Extract basic metadata
            metadata = self._parse_page_chunks(page_chunks)
            
            # Extract text preview if enabled
            text = metadata.text_preview
            if text:
                metadata.text_preview = text[:self.text_preview_chars]

        except Exception as e:
            error_msg = f"Metadata extraction failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
        
        return metadata, None
            
        
    def _parse_authors(self, author_str: Optional[str]) -> Optional[List[str]]:
        """Parse author string into list of authors."""
        if not author_str:
            return None
        # Split on common separators and clean up
        authors = [a.strip() for a in author_str.replace(";", ",").split(",")]
        return [a for a in authors if a]  # Remove empty strings
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse PDF date string into datetime object."""
        if not date_str:
            return None
        try:
            # Handle common PDF date formats
            # TODO: Implement proper PDF date parsing
            return datetime.now()  # Placeholder
        except Exception:
            return None
        
    def _parse_page_chunks(self, page_chunks: list[dict],) -> DocumentMetadataExtracted:
        """Parse page chunks from pymupdf4llm into document metadata.
        
        Args:
            page_chunks: List of page chunk dictionaries from pymupdf4llm
            
        Returns:
            DocumentMetadataExtracted with parsed metadata and text preview
            
        Notes:
            - Uses first chunk for document-level metadata
            - Combines preview text from multiple chunks up to limit
            - Handles missing or empty metadata fields
        """
        if not page_chunks:
            return DocumentMetadataExtracted(text_preview="") #without this it returns None..
        
        # Get metadata from first chunk as it contains document info
        first_chunk = page_chunks[0]
        metadata = first_chunk.get('metadata', {})
        
        # Extract creation date
        creation_date = None
        if date_str := metadata.get('creationDate'):
            try:
                # TODO: Implement PDF date string parsing
                creation_date = self._parse_date(date_str)
            except Exception:
                pass
                
        # Build text preview from chunks
        chunk_texts = []
        for chunk in page_chunks:
            if chunk_text := chunk.get('text', ''):
                chunk_texts.append(chunk_text)
        
        text_preview = "\n".join(chunk_texts)
        if len(text_preview) >= self.text_preview_chars:
            text_preview = text_preview[:self.text_preview_chars]
                        
        # Parse authors if present
        authors = self._parse_authors(metadata.get('author'))
                    
        return DocumentMetadataExtracted(
            title=metadata.get('title'),
            authors=authors,
            creation_date=creation_date,
            page_count=metadata.get('page_count'),
            language=metadata.get('language'),
            text_preview=text_preview.strip()
        )