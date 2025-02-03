# """Tests for the ingestion monitor functionality."""
# from pathlib import Path
# import pytest
# from ragnostic.ingestion.monitor import get_ingestible_files
# from ragnostic.ingestion.schema import IngestionStatus


# @pytest.fixture
# def temp_dir_with_files(tmp_path):
#     """Create a temporary directory with some test files."""
#     # Create test files
#     (tmp_path / "test1.pdf").touch()
#     (tmp_path / "test2.PDF").touch()
#     (tmp_path / "test3.txt").touch()  # Should be ignored
    
#     return tmp_path


# def test_get_ingestible_files_with_pdfs(temp_dir_with_files):
#     """Test finding PDF files in directory."""
#     result = get_ingestible_files(temp_dir_with_files)
    
#     assert result.status == IngestionStatus.MONITORING
#     assert len(result.files) == 2
#     assert all(isinstance(f, Path) for f in result.files)
#     assert all(f.suffix.lower() == '.pdf' for f in result.files)


# def test_get_ingestible_files_nonexistent_dir():
#     """Test handling of non-existent directory."""
#     result = get_ingestible_files("/nonexistent/path")
    
#     assert result.status == IngestionStatus.ERROR
#     assert "does not exist" in result.error_message


# def test_get_ingestible_files_file_as_dir(temp_dir_with_files):
#     """Test handling when path points to a file instead of directory."""
#     file_path = temp_dir_with_files / "test1.pdf"
#     result = get_ingestible_files(file_path)
    
#     assert result.status == IngestionStatus.ERROR
#     assert "not a directory" in result.error_message