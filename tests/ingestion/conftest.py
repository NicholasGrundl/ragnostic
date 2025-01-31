"""Test fixtures for validation tests."""
import os
from pathlib import Path
import pytest
from unittest.mock import Mock

from ragnostic.db.client import DatabaseClient

from pathlib import Path
import pytest
from typing import Optional


@pytest.fixture
def sample_pdf(tmp_path) -> Path:
    """Create a simple PDF file for testing."""
    output_path = tmp_path / "sample.pdf"
    with open(output_path, "wb") as f:
        # PDF header
        f.write(b"%PDF-1.4\n")
        # Required PDF objects
        f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        f.write(b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n")

        # PDF trailer and EOF marker
        f.write(b"xref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n")
        f.write(b"trailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n183\n%%EOF\n")
    
    return output_path


@pytest.fixture
def large_pdf(tmp_path) -> Path:
    """Create a large PDF file for testing."""
    size = 2 * 1024 * 1024  # 2MB
    
    output_path = tmp_path / "large.pdf"
    with open(output_path, "wb") as f:
        # PDF header
        f.write(b"%PDF-1.4\n")
        # Required PDF objects
        f.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        f.write(b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n")
        # Pad content for size
        f.write(b"%" + b"0" * size + b"\n")
        # PDF trailer and EOF marker
        f.write(b"xref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n")
        f.write(b"trailer\n<< /Root 1 0 R /Size 3 >>\nstartxref\n183\n%%EOF\n")
    
    return output_path


@pytest.fixture
def corrupt_pdf(tmp_path) -> Path:
    """Create a corrupted PDF file for testing."""
    pdf_path = tmp_path / "corrupt.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"Not a PDF file")
    return pdf_path


@pytest.fixture
def non_existent_pdf(tmp_path) -> Path:
    """Return path to non-existent PDF."""
    return tmp_path / "does_not_exist.pdf"


@pytest.fixture
def mock_db_client() -> DatabaseClient:
    """Create mock database client."""
    client = Mock(spec=DatabaseClient)
    client.get_document_by_hash.return_value = None
    return client