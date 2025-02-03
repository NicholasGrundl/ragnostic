

"""Directory monitoring implementation."""
from pathlib import Path
from typing import List, Set

from .schema import MonitorResult, MonitorStatus

class DirectoryMonitor:
    """Monitors directory for files to ingest."""
    
    def __init__(self, supported_extensions: Set[str] | None = None):
        """Initialize directory monitor.
        
        Args:
            supported_extensions: Set of supported file extensions (e.g., {'.pdf', '.PDF'})
                                If None, defaults to {'.pdf', '.PDF'}
        """
        self.supported_extensions = supported_extensions or {'.pdf', '.PDF'}
    
    def get_ingestible_files(self, directory: str | Path) -> MonitorResult:
        """Check directory for files that can be ingested.
        
        Args:
            directory: Path to directory to monitor
        
        Returns:
            MonitorResult containing status and any found files
        """
        path = Path(directory)
        
        # Validate directory exists
        if not path.exists():
            return MonitorResult(
                status=MonitorStatus.ERROR,
                error_message=f"Directory does not exist: {directory}"
            )
        
        # Validate it's actually a directory
        if not path.is_dir():
            return MonitorResult(
                status=MonitorStatus.ERROR,
                error_message=f"Path is not a directory: {directory}"
            )
        
        # Get all files with supported extensions
        found_files: List[Path] = []
        
        try:
            for file_path in path.iterdir():
                if file_path.suffix in self.supported_extensions:
                    found_files.append(file_path.resolve())
        except PermissionError:
            return MonitorResult(
                status=MonitorStatus.ERROR,
                error_message=f"Permission denied accessing directory: {directory}"
            )
        except Exception as e:
            return MonitorResult(
                status=MonitorStatus.ERROR,
                error_message=f"Error scanning directory: {str(e)}"
            )
        
        # Return results
        return MonitorResult(
            status=MonitorStatus.MONITORING,
            files=found_files
        )