# ragnostic/ingestion/monitor/schema.py
"""Schema definitions for directory monitoring."""
from enum import Enum
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, ConfigDict

class MonitorStatus(str, Enum):
    """Status of directory monitoring."""
    MONITORING = "monitoring"
    ERROR = "error"

class MonitorResult(BaseModel):
    """Result of monitoring a directory for files to ingest."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    status: MonitorStatus
    files: List[Path] = Field(default_factory=list)
    error_message: str | None = None

    @property
    def has_files(self) -> bool:
        """Check if any files were found."""
        return len(self.files) > 0
