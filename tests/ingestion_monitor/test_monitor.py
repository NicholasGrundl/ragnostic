"""Tests for directory monitor functionality."""
from pathlib import Path
import pytest

from ragnostic.ingestion.monitor import DirectoryMonitor, MonitorStatus

def test_monitor_initialization():
    """Test DirectoryMonitor initialization."""
    # Test default extensions
    monitor = DirectoryMonitor()
    assert '.pdf' in monitor.supported_extensions
    assert '.PDF' in monitor.supported_extensions
    
    # Test custom extensions
    custom_extensions = {'.txt', '.doc'}
    monitor = DirectoryMonitor(supported_extensions=custom_extensions)
    assert monitor.supported_extensions == custom_extensions

def test_get_ingestible_files_with_pdfs(temp_dir_with_files):
    """Test finding PDF files in directory."""
    monitor = DirectoryMonitor()
    result = monitor.get_ingestible_files(temp_dir_with_files)
    
    assert result.status == MonitorStatus.MONITORING
    assert len(result.files) == 2
    assert all(isinstance(f, Path) for f in result.files)
    assert all(f.suffix.lower() == '.pdf' for f in result.files)

def test_get_ingestible_files_nonexistent_dir():
    """Test handling of non-existent directory."""
    monitor = DirectoryMonitor()
    result = monitor.get_ingestible_files("/nonexistent/path")
    
    assert result.status == MonitorStatus.ERROR
    assert "does not exist" in result.error_message

def test_get_ingestible_files_file_as_dir(temp_dir_with_files):
    """Test handling when path points to a file instead of directory."""
    monitor = DirectoryMonitor()
    file_path = temp_dir_with_files / "test1.pdf"
    result = monitor.get_ingestible_files(file_path)
    
    assert result.status == MonitorStatus.ERROR
    assert "not a directory" in result.error_message

def test_get_ingestible_files_permission_error(tmp_path, monkeypatch):
    """Test handling of permission errors."""
    monitor = DirectoryMonitor()
    
    def mock_iterdir(*args):
        raise PermissionError("Access denied")
    
    monkeypatch.setattr(Path, "iterdir", mock_iterdir)
    result = monitor.get_ingestible_files(tmp_path)
    
    assert result.status == MonitorStatus.ERROR
    assert "Permission denied" in result.error_message

def test_get_ingestible_files_custom_extensions(temp_dir_with_files):
    """Test finding files with custom extensions."""
    monitor = DirectoryMonitor(supported_extensions={'.txt'})
    result = monitor.get_ingestible_files(temp_dir_with_files)
    
    assert result.status == MonitorStatus.MONITORING
    assert len(result.files) == 1
    assert all(f.suffix == '.txt' for f in result.files)