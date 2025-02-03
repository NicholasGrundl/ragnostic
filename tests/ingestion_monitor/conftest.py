"""Test fixtures for monitor tests."""
import pytest
from pathlib import Path

@pytest.fixture
def temp_dir_with_files(tmp_path):
    """Create a temporary directory with test files."""
    # Create test files
    (tmp_path / "test1.pdf").touch()
    (tmp_path / "test2.PDF").touch()
    (tmp_path / "test3.txt").touch()  # Should be ignored
    
    return tmp_path
