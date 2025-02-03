"""Shared test fixtures for processor tests."""
import pytest
from pathlib import Path


@pytest.fixture
def sample_pdf_content():
    """Sample PDF file content for testing."""
    return b"%PDF-1.4\n%TEST PDF CONTENT"


@pytest.fixture
def create_pdf_file(tmp_path, sample_pdf_content):
    """Factory fixture to create test PDF files."""
    def _create_pdf(filename: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_bytes(sample_pdf_content)
        return file_path
    return _create_pdf