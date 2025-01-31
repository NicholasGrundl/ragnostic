"""Directory monitoring functionality for document ingestion."""
from pathlib import Path
from typing import List

from .schema import MonitorResult, IngestionStatus, SupportedFileType


def get_ingestible_files(directory: str | Path) -> MonitorResult:
    """
    Check directory for files that can be ingested.
    
    Args:
        directory: Path to directory to monitor
    
    Returns:
        MonitorResult containing status and any found files
        
    Example:
        >>> result = get_ingestible_files("/path/to/docs")
        >>> if result.has_files:
        ...     print(f"Found {len(result.files)} files to ingest")
    """
    path = Path(directory)
    
    # Validate directory exists
    if not path.exists():
        return MonitorResult(
            status=IngestionStatus.ERROR,
            error_message=f"Directory does not exist: {directory}"
        )
    
    # Validate it's actually a directory
    if not path.is_dir():
        return MonitorResult(
            status=IngestionStatus.ERROR,
            error_message=f"Path is not a directory: {directory}"
        )
    
    # Get all files with supported extensions
    supported_types = SupportedFileType.supported_types()
    found_files: List[Path] = []
    
    try:
        for file_path in path.iterdir():
            if file_path.suffix in supported_types:
                found_files.append(file_path.resolve())
    except PermissionError:
        return MonitorResult(
            status=IngestionStatus.ERROR,
            error_message=f"Permission denied accessing directory: {directory}"
        )
    except Exception as e:
        return MonitorResult(
            status=IngestionStatus.ERROR,
            error_message=f"Error scanning directory: {str(e)}"
        )
    
    # Return results
    return MonitorResult(
        status=IngestionStatus.MONITORING,
        files=found_files
    )