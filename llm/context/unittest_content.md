<file_1>
<path>__init__.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/tests/__init__.py'
</content>
</file_1>

<file_2>
<path>conftest.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/tests/conftest.py'
</content>
</file_2>

<file_3>
<path>test_processor.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/tests/test_processor.py'
</content>
</file_3>

<file_4>
<path>test_schema.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/tests/test_schema.py'
</content>
</file_4>

<file_5>
<path>test_storage.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/tests/test_storage.py'
</content>
</file_5>

<file_6>
<path>ingestion_validation/__init__.py</path>
<content>
```python

```
</content>
</file_6>

<file_7>
<path>ingestion_validation/conftest.py</path>
<content>
```python
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
```
</content>
</file_7>

<file_8>
<path>ingestion_validation/test_checks.py</path>
<content>
```python
"""Tests for validation check functions."""
from pathlib import Path
import pytest
from unittest.mock import Mock

from ragnostic.ingestion.validation.checks import (
    compute_file_hash,
    check_file_exists,
    check_file_hash,
    check_file_size,
    check_mime_type,
    check_hash_unique,
)
from ragnostic.ingestion.validation.schema import ValidationCheckType, ValidationCheckFailure


def test_compute_file_hash(sample_pdf, large_pdf):
    """Test computing file hash."""
    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:
        # Test valid file
        hash_value = compute_file_hash(pdf_file)
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA-256 produces 64 character hex string
        
        # Test same file produces same hash
        assert compute_file_hash(pdf_file) == hash_value
        
        # Test non-existent file
        assert compute_file_hash(Path("nonexistent.pdf")) is None


def test_check_file_exists(sample_pdf, large_pdf, non_existent_pdf, tmp_path):
    """Test file existence check."""
    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:

        # Test existing file
        result = check_file_exists(pdf_file)
        assert result is True
        
    # Test non-existent file
    result = check_file_exists(non_existent_pdf)
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.OTHER
    
    # Test directory instead of file
    result = check_file_exists(tmp_path)
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.OTHER


def test_check_file_hash(sample_pdf, large_pdf, corrupt_pdf):
    """Test file hash check."""
    pdf_files = [sample_pdf, large_pdf, corrupt_pdf]
    for pdf_file in pdf_files:
        # Test valid file
        result = check_file_hash(pdf_file)
        assert isinstance(result, str)
        assert len(result) == 64
    
def test_check_file_size(sample_pdf, large_pdf,):
    """Test file size check."""
    # Test file under size limit
    result = check_file_size(sample_pdf, max_size=1024*1024)  # 1MB limit
    assert isinstance(result, int)
    assert result > 0
    
    # Test file over size limit
    result = check_file_size(large_pdf, max_size=1)  # 1 byte limit
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.FILE_TOO_LARGE
    assert 'file_size' in result.details
    assert 'max_size' in result.details

@pytest.mark.parametrize("mime_types,expected_valid", [
    (['application/pdf'], True),
    (['application/x-pdf'], False),
    (['image/jpeg'], False),
    ([], False),
])

def test_check_mime_type(sample_pdf, large_pdf, mime_types, expected_valid):
    """Test mime type check with different mime type lists."""
    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:

        result = check_mime_type(pdf_file, mime_types)
        
        if expected_valid:
            assert isinstance(result, str)
            assert result in mime_types
        else:
            assert isinstance(result, ValidationCheckFailure)
            assert result.check_type == ValidationCheckType.INVALID_MIMETYPE
            assert 'mime_type' in result.details

def test_check_mime_type_corrupt_file(corrupt_pdf):
    """Test mime type check with corrupt file."""
    result = check_mime_type(corrupt_pdf, ['application/pdf'])
    assert isinstance(result, ValidationCheckFailure)
    assert result.check_type == ValidationCheckType.INVALID_MIMETYPE


def test_check_hash_unique(sample_pdf, large_pdf, mock_db_client):
    """Test hash uniqueness check."""
    

    pdf_files = [sample_pdf, large_pdf]
    for pdf_file in pdf_files:
        # Compute the hash
        file_hash = compute_file_hash(pdf_file)
        
        # Test unique hash
        # - db client returns None if no identical hash found
        mock_db_client.get_document_by_hash.return_value = None
        result = check_hash_unique(pdf_file, file_hash, mock_db_client)
        assert result is True
    
        # Test duplicate hash
        # - db client returns a db.schema.Document obj, which has id attribute
        mock_db_client.get_document_by_hash.return_value = Mock(id="existing_doc_id")
        result = check_hash_unique(pdf_file, file_hash, mock_db_client)
        assert isinstance(result, ValidationCheckFailure)
        assert result.check_type == ValidationCheckType.DUPLICATE_HASH
        assert 'existing_doc_id' in result.details

```
</content>
</file_8>

<file_9>
<path>ingestion_validation/test_schema.py</path>
<content>
```python
"""Tests for validation schemas."""
from pathlib import Path
import pytest
from ragnostic.ingestion.validation.schema import (
    ValidationCheckType,
    ValidationCheckFailure,
    ValidationResult,
    BatchValidationResult,
)


def test_validation_check_failure():
    """Test ValidationCheckFailure creation and properties."""
    failure = ValidationCheckFailure(
        filepath=Path("/test.pdf"),
        check_type=ValidationCheckType.CORRUPTED_FILE,
        message="Test failure",
        details={"extra": "info"}
    )
    
    assert failure.filepath == Path("/test.pdf")
    assert failure.check_type == ValidationCheckType.CORRUPTED_FILE
    assert failure.message == "Test failure"
    assert failure.details == {"extra": "info"}


def test_validation_result():
    """Test ValidationResult creation and properties."""
    # Test valid result
    valid_result = ValidationResult(
        filepath=Path("/test.pdf"),
        is_valid=True,
        file_hash="abc123",
        mime_type="application/pdf",
        file_size_bytes=1024,
    )
    
    assert valid_result.is_valid
    assert valid_result.file_hash == "abc123"
    assert not valid_result.check_failures
    
    # Test invalid result
    failure = ValidationCheckFailure(
        filepath=Path("/test.pdf"),
        check_type=ValidationCheckType.CORRUPTED_FILE,
        message="Test failure"
    )
    
    invalid_result = ValidationResult(
        filepath=Path("/test.pdf"),
        is_valid=False,
        check_failures=[failure]
    )
    
    assert not invalid_result.is_valid
    assert invalid_result.file_hash is None
    assert len(invalid_result.check_failures) == 1


def test_batch_validation_result():
    """Test BatchValidationResult creation and properties."""
    valid_result = ValidationResult(
        filepath=Path("/valid.pdf"),
        is_valid=True,
        file_hash="abc123"
    )
    
    invalid_result = ValidationResult(
        filepath=Path("/invalid.pdf"),
        is_valid=False,
        check_failures=[
            ValidationCheckFailure(
                filepath=Path("/invalid.pdf"),
                check_type=ValidationCheckType.CORRUPTED_FILE,
                message="Test failure"
            )
        ]
    )
    
    batch = BatchValidationResult(
        valid_files=[valid_result],
        invalid_files=[invalid_result]
    )
    
    assert batch.has_valid_files
    assert batch.has_invalid_files
    assert len(batch.valid_files) == 1
    assert len(batch.invalid_files) == 1


def test_empty_batch_validation_result():
    """Test empty BatchValidationResult."""
    batch = BatchValidationResult()
    
    assert not batch.has_valid_files
    assert not batch.has_invalid_files
    assert len(batch.valid_files) == 0
    assert len(batch.invalid_files) == 0
```
</content>
</file_9>

<file_10>
<path>ingestion_validation/test_validator.py</path>
<content>
```python
"""Tests for document validator."""
import pytest
from pathlib import Path
from unittest.mock import Mock

from ragnostic.ingestion.validation.validator import DocumentValidator
from ragnostic.ingestion.validation.schema import ValidationCheckType


def test_validator_init(mock_db_client):
    """Test validator initialization."""
    validator = DocumentValidator(mock_db_client)
    assert validator.max_file_size == 100 * 1024 * 1024
    assert 'application/pdf' in validator.supported_mimetypes
    
    custom_validator = DocumentValidator(
        mock_db_client,
        max_file_size=1024,
        supported_mimetypes=['custom/type']
    )
    assert custom_validator.max_file_size == 1024
    assert custom_validator.supported_mimetypes == ['custom/type']


def test_validate_non_existent_file(mock_db_client, non_existent_pdf):
    """Test validation of non-existent file."""
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(non_existent_pdf)
    
    assert not result.is_valid
    assert len(result.check_failures) == 1
    assert result.check_failures[0].check_type == ValidationCheckType.OTHER


def test_validate_corrupt_file(mock_db_client, corrupt_pdf):
    """Test validation of corrupt file."""
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(corrupt_pdf)
    
    assert not result.is_valid
    assert result.file_hash is None
    assert any(f.check_type == ValidationCheckType.INVALID_MIMETYPE 
              for f in result.check_failures)


def test_validate_large_file(mock_db_client, large_pdf):
    """Test validation of file exceeding size limit."""
    # Verify file is actually larger than limit
    file_size = large_pdf.stat().st_size
    max_size = 1024  # 1KB limit
    assert file_size > max_size, f"Test file size ({file_size} bytes) should be larger than {max_size} bytes"
    
    validator = DocumentValidator(mock_db_client, max_file_size=max_size)
    result = validator._validate_single_file(large_pdf)
    print(result)
    assert not result.is_valid
    assert any(f.check_type == ValidationCheckType.FILE_TOO_LARGE 
              for f in result.check_failures)
    
    assert any(f.details.get('file_size') > f.details.get('max_size')
              for f in result.check_failures)


def test_validate_duplicate_file(mock_db_client, sample_pdf):
    """Test validation of duplicate file."""
    # Mock DB to return existing document
    mock_db_client.get_document_by_hash.return_value = Mock(id="existing_doc")
    
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(sample_pdf)
    
    assert not result.is_valid
    assert any(f.check_type == ValidationCheckType.DUPLICATE_HASH 
              for f in result.check_failures)
    assert any(f.details.get('existing_doc_id') == "existing_doc" 
              for f in result.check_failures)


def test_validate_valid_file(mock_db_client, sample_pdf):
    """Test validation of valid file."""
    # Ensure DB returns no existing document
    mock_db_client.get_document_by_hash.return_value = None
    
    validator = DocumentValidator(mock_db_client)
    result = validator._validate_single_file(sample_pdf)
    
    assert result.is_valid
    assert result.file_hash is not None
    assert result.mime_type == "application/pdf"
    assert result.file_size_bytes > 0
    assert not result.check_failures


def test_batch_validation(mock_db_client, sample_pdf, corrupt_pdf, non_existent_pdf):
    """Test batch validation of multiple files."""
    # Ensure DB returns no existing documents
    mock_db_client.get_document_by_hash.return_value = None
    
    validator = DocumentValidator(mock_db_client)
    batch_result = validator.validate_files([
        sample_pdf,
        corrupt_pdf,
        non_existent_pdf
    ])
    
    assert batch_result.has_valid_files
    assert batch_result.has_invalid_files
    assert len(batch_result.valid_files) == 1
    assert len(batch_result.invalid_files) == 2
    
    # Check valid file result
    valid_result = batch_result.valid_files[0]
    assert valid_result.filepath == sample_pdf
    assert valid_result.is_valid
    assert valid_result.file_hash is not None
    assert valid_result.mime_type == "application/pdf"
    
    # Check invalid file results
    invalid_paths = [r.filepath for r in batch_result.invalid_files]
    assert corrupt_pdf in invalid_paths
    assert non_existent_pdf in invalid_paths

```
</content>
</file_10>

<file_11>
<path>test_db.py</path>
<content>
```python
"""Tests for database operations."""
import pytest
from datetime import datetime
from pathlib import Path

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import (
    DocumentCreate,
    Document,
    DocumentMetadataCreate,
    DocumentMetadata,
    DocumentSectionCreate,
    DocumentSection,
    SectionContentCreate,
    DocumentImageCreate,
    DocumentTableCreate,
)


@pytest.fixture
def db_path(tmp_path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test.db"


@pytest.fixture
def db_client(db_path) -> DatabaseClient:
    """Create a database client for testing."""
    return DatabaseClient(f"sqlite:///{db_path}")


@pytest.fixture
def sample_document() -> DocumentCreate:
    """Create a sample document for testing."""
    return DocumentCreate(
        id="doc1",
        raw_file_path="/path/to/doc.pdf",
        file_hash="abc123",
        file_size_bytes=1024,
        mime_type="application/pdf"
    )


@pytest.fixture
def sample_metadata() -> DocumentMetadataCreate:
    """Create sample metadata for testing."""
    return DocumentMetadataCreate(
        doc_id="doc1",
        title="Test Document",
        authors=["Author 1", "Author 2"],
        creation_date=datetime(2024, 1, 1),
        page_count=10,
        language="en"
    )


@pytest.fixture
def sample_section() -> DocumentSectionCreate:
    """Create a sample section for testing."""
    return DocumentSectionCreate(
        section_id="sec1",
        doc_id="doc1",
        level=1,
        sequence_order=1,
        word_count=100,
        image_count=0,
        table_count=0
    )


@pytest.fixture
def sample_section_content() -> SectionContentCreate:
    """Create sample section content for testing."""
    return SectionContentCreate(
        section_id="sec1",
        title="Introduction",
        content="This is the introduction section.",
        page_start=1,
        page_end=2
    )


@pytest.fixture
def sample_image() -> DocumentImageCreate:
    """Create sample document image for testing."""
    return DocumentImageCreate(
        doc_id="doc1",
        section_id="sec1",
        page_number=1,
        image_data="base64_encoded_data",
        caption="Test image"
    )


@pytest.fixture
def sample_table() -> DocumentTableCreate:
    """Create sample document table for testing."""
    return DocumentTableCreate(
        doc_id="doc1",
        section_id="sec1",
        page_number=1,
        table_data={"headers": ["Col1"], "rows": [["Data1"]]},
        caption="Test table"
    )


def test_create_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test creating a document."""
    doc = db_client.create_document(sample_document)
    assert isinstance(doc, Document)
    assert doc.id == sample_document.id
    assert doc.file_hash == sample_document.file_hash
    assert doc.total_sections == 0
    assert doc.total_images == 0
    assert doc.total_tables == 0


def test_get_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test retrieving a document."""
    created_doc = db_client.create_document(sample_document)
    retrieved_doc = db_client.get_document_by_id(created_doc.id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.file_hash == created_doc.file_hash


def test_get_document_by_hash(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test retrieving a document by hash."""
    created_doc = db_client.create_document(sample_document)
    retrieved_doc = db_client.get_document_by_hash(created_doc.file_hash)
    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.file_hash == created_doc.file_hash


def test_create_metadata(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_metadata: DocumentMetadataCreate
):
    """Test creating document metadata."""
    db_client.create_document(sample_document)
    metadata = db_client.create_metadata(sample_metadata)
    assert isinstance(metadata, DocumentMetadata)
    assert metadata.doc_id == sample_metadata.doc_id
    assert metadata.title == sample_metadata.title
    assert metadata.authors == sample_metadata.authors


def test_get_metadata(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_metadata: DocumentMetadataCreate
):
    """Test retrieving document metadata."""
    db_client.create_document(sample_document)
    created_metadata = db_client.create_metadata(sample_metadata)
    retrieved_metadata = db_client.get_metadata(created_metadata.doc_id)
    assert retrieved_metadata is not None
    assert retrieved_metadata.doc_id == created_metadata.doc_id
    assert retrieved_metadata.title == created_metadata.title


def test_create_section(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate
):
    """Test creating a document section with content."""
    db_client.create_document(sample_document)
    section = db_client.create_section(sample_section, sample_section_content)
    assert isinstance(section, DocumentSection)
    assert section.section_id == sample_section.section_id
    assert section.content is not None
    assert section.content.title == sample_section_content.title
    
    # Verify document metrics were updated
    doc = db_client.get_document_by_id(sample_document.id)
    assert doc is not None
    assert doc.total_sections == 1


def test_get_document_sections(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate
):
    """Test retrieving document sections."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section, sample_section_content)
    
    sections = db_client.get_document_sections(sample_document.id)
    assert len(sections) == 1
    assert sections[0].section_id == sample_section.section_id
    assert sections[0].content is not None
    assert sections[0].content.title == sample_section_content.title


def test_create_image(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate,
    sample_image: DocumentImageCreate
):
    """Test creating a document image."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section, sample_section_content)
    image = db_client.create_image(sample_image)
    
    assert image.doc_id == sample_image.doc_id
    assert image.section_id == sample_image.section_id
    
    # Verify metrics were updated
    doc = db_client.get_document_by_id(sample_document.id)
    assert doc.total_images == 1
    
    sections = db_client.get_document_sections(sample_document.id)
    assert sections[0].image_count == 1


def test_create_table(
    db_client: DatabaseClient,
    sample_document: DocumentCreate,
    sample_section: DocumentSectionCreate,
    sample_section_content: SectionContentCreate,
    sample_table: DocumentTableCreate
):
    """Test creating a document table."""
    db_client.create_document(sample_document)
    db_client.create_section(sample_section, sample_section_content)
    table = db_client.create_table(sample_table)
    
    assert table.doc_id == sample_table.doc_id
    assert table.section_id == sample_table.section_id
    
    # Verify metrics were updated
    doc = db_client.get_document_by_id(sample_document.id)
    assert doc.total_tables == 1
    
    sections = db_client.get_document_sections(sample_document.id)
    assert sections[0].table_count == 1


def test_duplicate_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test handling duplicate document creation."""
    db_client.create_document(sample_document)
    with pytest.raises(ValueError):
        db_client.create_document(sample_document)


def test_delete_document(db_client: DatabaseClient, sample_document: DocumentCreate):
    """Test document deletion."""
    db_client.create_document(sample_document)
    assert db_client.delete_document(sample_document.id) is True
    assert db_client.get_document_by_id(sample_document.id) is None


def test_get_nonexistent_document(db_client: DatabaseClient):
    """Test retrieving a nonexistent document."""
    assert db_client.get_document_by_id("nonexistent") is None

```
</content>
</file_11>

<file_12>
<path>test_ingestion_monitor.py</path>
<content>
```python
"""Tests for the ingestion monitor functionality."""
from pathlib import Path
import pytest
from ragnostic.ingestion.monitor import get_ingestible_files
from ragnostic.ingestion.schema import IngestionStatus


@pytest.fixture
def temp_dir_with_files(tmp_path):
    """Create a temporary directory with some test files."""
    # Create test files
    (tmp_path / "test1.pdf").touch()
    (tmp_path / "test2.PDF").touch()
    (tmp_path / "test3.txt").touch()  # Should be ignored
    
    return tmp_path


def test_get_ingestible_files_with_pdfs(temp_dir_with_files):
    """Test finding PDF files in directory."""
    result = get_ingestible_files(temp_dir_with_files)
    
    assert result.status == IngestionStatus.MONITORING
    assert len(result.files) == 2
    assert all(isinstance(f, Path) for f in result.files)
    assert all(f.suffix.lower() == '.pdf' for f in result.files)


def test_get_ingestible_files_nonexistent_dir():
    """Test handling of non-existent directory."""
    result = get_ingestible_files("/nonexistent/path")
    
    assert result.status == IngestionStatus.ERROR
    assert "does not exist" in result.error_message


def test_get_ingestible_files_file_as_dir(temp_dir_with_files):
    """Test handling when path points to a file instead of directory."""
    file_path = temp_dir_with_files / "test1.pdf"
    result = get_ingestible_files(file_path)
    
    assert result.status == IngestionStatus.ERROR
    assert "not a directory" in result.error_message
```
</content>
</file_12>
