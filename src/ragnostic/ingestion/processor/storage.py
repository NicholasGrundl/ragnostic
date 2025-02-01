"""Storage operations for document processing."""
from pathlib import Path
from shutil import copy2
from typing import Optional

from .schema import ProcessingStatus, ProcessingResult


def store_document(
    source_path: Path,
    storage_dir: Path,
    doc_id: str
) -> ProcessingResult:
    """Store document in the target location with proper error handling.
    
    Args:
        source_path: Path to source document
        storage_dir: Directory to store document in
        doc_id: Generated document ID
    
    Returns:
        ProcessingResult with status and details
    """
    # Create result with initial values
    result = ProcessingResult(
        doc_id=doc_id,
        original_path=source_path,
        status=ProcessingStatus.SUCCESS
    )
    
    # Validate source file
    if not source_path.is_file():
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": f"Source file not found: {source_path}",
            "error_code": "SOURCE_NOT_FOUND"
        })
    
    # Validate storage directory
    if not storage_dir.is_dir():
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": f"Storage directory invalid: {storage_dir}",
            "error_code": "INVALID_STORAGE_DIR"
        })
    
    try:
        # Generate destination path with original extension
        suffix = source_path.suffix
        dest_filename = f"{doc_id}{suffix}"
        dest_path = storage_dir / dest_filename
        
        # Copy file preserving metadata
        copy2(source_path, dest_path)
        
        return result.model_copy(update={
            "storage_path": dest_path
        })
        
    except PermissionError as e:
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": str(e),
            "error_code": "PERMISSION_DENIED"
        })
    except OSError as e:
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": str(e),
            "error_code": "STORAGE_FAILED"
        })
    except Exception as e:
        return result.model_copy(update={
            "status": ProcessingStatus.UNKNOWN_ERROR,
            "error_message": str(e),
            "error_code": "UNKNOWN"
        })