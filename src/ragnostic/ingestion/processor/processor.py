"""Document processing functionality."""
import logging
from pathlib import Path
from typing import List

from ragnostic.ingestion.utils import create_doc_id
from .schema import BatchProcessingResult, ProcessingResult, ProcessingStatus
from .storage import store_document


logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing and storage operations."""
    
    def __init__(self, doc_id_prefix: str = "DOC"):
        """Initialize processor with configuration.
        
        Args:
            doc_id_prefix: Prefix to use for document IDs
        """
        self.doc_id_prefix = doc_id_prefix
    
    def process_documents(
        self,
        file_paths: List[Path],
        storage_dir: Path
    ) -> BatchProcessingResult:
        """Process a batch of validated documents.
        
        Args:
            file_paths: List of paths to validated documents
            storage_dir: Directory to store processed documents
        
        Returns:
            BatchProcessingResult containing results for all documents
        """
        results = BatchProcessingResult()
        
        for file_path in file_paths:
            try:
                result = self._process_single_document(file_path, storage_dir)
                
                if result.status == ProcessingStatus.SUCCESS:
                    results.successful_docs.append(result)
                else:
                    results.failed_docs.append(result)
                    
            except Exception as e:
                logger.exception(f"Unexpected error processing {file_path}")
                results.failed_docs.append(
                    ProcessingResult(
                        doc_id="ERROR",
                        original_path=file_path,
                        status=ProcessingStatus.UNKNOWN_ERROR,
                        error_message=str(e),
                        error_code="UNEXPECTED_ERROR"
                    )
                )
        
        return results
    
    def _process_single_document(
        self,
        file_path: Path,
        storage_dir: Path
    ) -> ProcessingResult:
        """Process a single document.
        
        Args:
            file_path: Path to document to process
            storage_dir: Directory to store processed document
        
        Returns:
            ProcessingResult with status and details
        """
        # Generate document ID
        doc_id = create_doc_id(prefix=self.doc_id_prefix)
        
        # Store document
        result = store_document(
            source_path=file_path,
            storage_dir=storage_dir,
            doc_id=doc_id
        )
        
        return result