"""Document indexing functionality."""
import logging
from pathlib import Path
from typing import List, Optional, Set

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import Document, DocumentCreate, DocumentMetadata, DocumentMetadataCreate
from ragnostic.ingestion.validation.checks import compute_file_hash
import magic

from .extraction import PDFExtractor
from .schema import IndexingResult, BatchIndexingResult, IndexingStatus

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Handles document indexing operations."""
    
    SUPPORTED_MIME_TYPES: Set[str] = {'application/pdf', 'application/x-pdf'}

    def __init__(self, 
                 db_client: DatabaseClient,
                 text_preview_chars: int = 1000):
        """Initialize document indexer.
        
        Args:
            db_client: Database client instance
            extract_text: Whether to extract text preview
            text_preview_chars: Number of characters for text preview
        """
        self.db_client = db_client
        self.extractor = PDFExtractor(
            text_preview_chars=text_preview_chars
        )
    
    def index_document(self, filepath: Path) -> IndexingResult:
        """Index a single document with metadata.
        
        Args:
            filepath: Path to document to index
            
        Returns:
            IndexingResult with status and details
        """
        try:
            # Validate mime type first
            mime_type = magic.from_file(str(filepath), mime=True)
            if mime_type not in self.SUPPORTED_MIME_TYPES:
                return IndexingResult(
                    doc_id=filepath.stem,
                    filepath=filepath,
                    status=IndexingStatus.METADATA_ERROR,
                    error_message=f"Unsupported file type: {mime_type}"
                )
            
            # Get certain metadata
            file_hash = compute_file_hash(filepath)
            if not file_hash:
                return IndexingResult(
                    doc_id="ERROR",
                    filepath=filepath,
                    status=IndexingStatus.METADATA_ERROR,
                    error_message="Failed to compute file hash"
                )
            
            file_size = filepath.stat().st_size
            
            # Create document record
            doc = DocumentCreate(
                id=filepath.stem,  # Using filename as ID for now
                raw_file_path=str(filepath),
                file_hash=file_hash,
                file_size_bytes=file_size,
                mime_type=mime_type
            )
            
            try:
                db_doc = self.db_client.create_document(doc)
            except ValueError as e:
                return IndexingResult(
                    doc_id=doc.id,
                    filepath=filepath,
                    status=IndexingStatus.DATABASE_ERROR,
                    error_message=str(e)
                )
            
            # Extract optional metadata
            extracted_metadata, error = self.extractor.extract_metadata(filepath)
            if extracted_metadata:
                # Create metadata record
                metadata = DocumentMetadataCreate(
                    doc_id=db_doc.id,
                    title=extracted_metadata.title,
                    authors=extracted_metadata.authors,
                    creation_date=extracted_metadata.creation_date,
                    page_count=extracted_metadata.page_count,
                    language=extracted_metadata.language
                )
                
                try:
                    self.db_client.create_metadata(metadata)
                except ValueError as e:
                    logger.warning(f"Failed to store metadata: {e}")
                    # Continue without metadata
            
            return IndexingResult(
                doc_id=db_doc.id,
                filepath=filepath,
                status=IndexingStatus.SUCCESS,
                extracted_metadata=extracted_metadata
            )
            
        except Exception as e:
            error_msg = f"Indexing failed: {str(e)}"
            logger.error(error_msg)
            return IndexingResult(
                doc_id="ERROR",
                filepath=filepath,
                status=IndexingStatus.UNKNOWN_ERROR,
                error_message=error_msg
            )
    
    def index_batch(self, filepaths: List[Path]) -> BatchIndexingResult:
        """Index multiple documents.
        
        Args:
            filepaths: List of paths to documents to index
            
        Returns:
            BatchIndexingResult with combined results
        """
        results = BatchIndexingResult()
        
        for filepath in filepaths:
            result = self.index_document(filepath)
            if result.status == IndexingStatus.SUCCESS:
                results.successful_docs.append(result)
            else:
                results.failed_docs.append(result)
        
        return results