"""Action definitions for document ingestion workflow."""
from pathlib import Path
from typing import List

from burr.core import State, action

from ragnostic.db.client import DatabaseClient
from ragnostic.ingestion.monitor import DirectoryMonitor, MonitorStatus
from ragnostic.ingestion.validation import DocumentValidator
from ragnostic.ingestion.processor import DocumentProcessor
from ragnostic.ingestion.indexing import DocumentIndexer


@action(reads=[], writes=["monitor_result","error"])
def monitor_action(state: State, ingest_dir: str) -> State:
    """Monitor directory for new files to process.
    
    Args:
        state: Current workflow state
        ingest_dir: Directory path to monitor
        
    Returns:
        Updated state with monitor_result
    """
    monitor = DirectoryMonitor()
    result = monitor.get_ingestible_files(ingest_dir)
    
    if result.status == MonitorStatus.ERROR:
        return state.update(
            monitor_result=result,
            error=f"Monitor error: {result.error_message}"
        )
        
    return state.update(monitor_result=result, error=None)


@action(
    reads=["monitor_result"],
    writes=["validation_result","error"]
)
def validation_action(
    state: State,
    db_client: DatabaseClient,
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
) -> State:
    """Validate monitored files.
    
    Args:
        state: Current workflow state
        db_client: Database client for duplicate checks
        max_file_size: Maximum allowed file size in bytes
        
    Returns:
        Updated state with validation results
    """
    monitor_result = state.get("monitor_result")
    if not monitor_result.has_files:
        return state.update(
            validation_result=None,
            error="No files to validate"
        )
        
    validator = DocumentValidator(
        db_client=db_client,
        max_file_size=max_file_size
    )
    
    validation_result = validator.validate_files(monitor_result.files)
    return state.update(validation_result=validation_result, error=None)


@action(
    reads=["validation_result"],
    writes=["processing_result","error"]
)
def processing_action(state: State, storage_dir: str) -> State:
    """Process validated documents.
    
    Args:
        state: Current workflow state
        storage_dir: Directory for processed document storage
        
    Returns:
        Updated state with processing results
    """
    validation_result = state.get("validation_result")
    if not validation_result or not validation_result.has_valid_files:
        return state.update(
            processing_result=None,
            error="No valid files to process"
        )
    
    # Get valid file paths
    valid_files = [result.filepath for result in validation_result.valid_files]
    
    processor = DocumentProcessor()
    processing_result = processor.process_documents(
        file_paths=valid_files,
        storage_dir=Path(storage_dir)
    )
    
    return state.update(processing_result=processing_result, error=None)


@action(
    reads=["processing_result"],
    writes=["indexing_result", "error"]
)
def indexing_action(
    state: State,
    db_client: DatabaseClient,
    text_preview_chars: int = 1000
) -> State:
    """Index processed documents.
    
    Args:
        state: Current workflow state
        db_client: Database client for document indexing
        text_preview_chars: Number of characters for text preview
        
    Returns:
        Updated state with indexing results
    """
    processing_result = state.get("processing_result")
    if processing_result is None or len(processing_result.successful_docs)==0:
        return state.update(
            indexing_result=None,
            error="No successfully processed documents to index"
        )
    # Get successful document paths
    successful_paths = [
        Path(result.storage_path)
        for result in processing_result.successful_docs
    ]
    
    indexer = DocumentIndexer(
        db_client=db_client,
        text_preview_chars=text_preview_chars
    )
    
    indexing_result = indexer.index_batch(successful_paths)
    return state.update(indexing_result=indexing_result, error=None)