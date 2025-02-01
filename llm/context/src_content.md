<file_1>
<path>ragnostic/db/__init__.py</path>
<content>
```python
"""Database package initialization."""
from pathlib import Path
from typing import Optional

from .client import DatabaseClient
from .models import Base
from .schema import (
    Document,
    DocumentCreate,
    DocumentMetadata,
    DocumentMetadataCreate,
    DocumentSection,
    DocumentSectionCreate,
    DocumentImage,
    DocumentImageCreate,
    DocumentTable,
    DocumentTableCreate,
)


def create_sqlite_url(db_path: Optional[str] = None) -> str:
    """Create SQLite database URL.
    
    Args:
        db_path: Optional path to SQLite database file. If not provided,
                creates a database in the user's home directory.
    
    Returns:
        Database URL string
    """
    if not db_path:
        db_path = str(Path.home() / ".ragnostic" / "ragnostic.db")
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    return f"sqlite:///{db_path}"


__all__ = [
    "DatabaseClient",
    "Base",
    "Document",
    "DocumentCreate",
    "DocumentMetadata",
    "DocumentMetadataCreate",
    "DocumentSection",
    "DocumentSectionCreate",
    "DocumentImage",
    "DocumentImageCreate",
    "DocumentTable",
    "DocumentTableCreate",
    "create_sqlite_url",
]

```
</content>
</file_1>

<file_2>
<path>ragnostic/db/client.py</path>
<content>
```python
"""Database client for handling all database operations."""
from typing import Optional, List
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from . import models, schema


class DatabaseClient:
    """Client for handling database operations using SQLAlchemy and Pydantic models."""

    def __init__(self, database_url: str):
        """Initialize database client with connection URL."""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create all tables
        models.Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def create_document(self, document: schema.DocumentCreate) -> schema.Document:
        """Create a new document."""
        with self.get_session() as session:
            db_document = models.Document(**document.model_dump())
            session.add(db_document)
            try:
                session.commit()
                session.refresh(db_document)
                return schema.Document.model_validate(db_document)
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Document with hash {document.file_hash} already exists")

    def get_document_by_id(self, doc_id: str) -> Optional[schema.Document]:
        """Get document by ID."""
        with self.get_session() as session:
            result = session.query(models.Document).filter(
                models.Document.id == doc_id
            ).first()
            return schema.Document.model_validate(result) if result else None

    def get_document_by_hash(self, file_hash: str) -> Optional[schema.Document]:
        """Get document by hash."""
        with self.get_session() as session:
            result = session.query(models.Document).filter(
                models.Document.file_hash == file_hash
            ).first()
            return schema.Document.model_validate(result) if result else None

    def create_metadata(self, metadata: schema.DocumentMetadataCreate) -> schema.DocumentMetadata:
        """Create document metadata."""
        with self.get_session() as session:
            db_metadata = models.DocumentMetadata(**metadata.model_dump())
            session.add(db_metadata)
            try:
                session.commit()
                session.refresh(db_metadata)
                return schema.DocumentMetadata.model_validate(db_metadata)
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Metadata for document {metadata.doc_id} already exists")

    def get_metadata(self, doc_id: str) -> Optional[schema.DocumentMetadata]:
        """Get document metadata."""
        with self.get_session() as session:
            result = session.query(models.DocumentMetadata).filter(
                models.DocumentMetadata.doc_id == doc_id
            ).first()
            return schema.DocumentMetadata.model_validate(result) if result else None

    def create_section(self, 
                      section: schema.DocumentSectionCreate, 
                      content: schema.SectionContentCreate) -> schema.DocumentSection:
        """Create document section with its content."""
        with self.get_session() as session:
            # Create section
            db_section = models.DocumentSection(**section.model_dump())
            session.add(db_section)
            
            # Create section content
            db_content = models.SectionContent(**content.model_dump())
            session.add(db_content)
            
            try:
                session.commit()
                session.refresh(db_section)
                
                # Update document metrics
                doc = session.query(models.Document).filter(
                    models.Document.id == section.doc_id
                ).first()
                doc.total_sections += 1
                session.commit()
                
                # Get the complete section with content
                result = (
                    session.query(models.DocumentSection)
                    .filter(models.DocumentSection.section_id == section.section_id)
                    .first()
                )
                return schema.DocumentSection.model_validate(result)
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Section {section.section_id} already exists")

    def get_document_sections(self, doc_id: str) -> List[schema.DocumentSection]:
        """Get all sections for a document ordered by sequence."""
        with self.get_session() as session:
            sections = (
                session.query(models.DocumentSection)
                .filter(models.DocumentSection.doc_id == doc_id)
                .order_by(models.DocumentSection.sequence_order)
                .all()
            )
            return [schema.DocumentSection.model_validate(s) for s in sections]

    def create_image(self, image: schema.DocumentImageCreate) -> schema.DocumentImage:
        """Create document image and update metrics."""
        with self.get_session() as session:
            db_image = models.DocumentImage(**image.model_dump())
            session.add(db_image)
            session.commit()
            
            # Update metrics
            doc = session.query(models.Document).filter(
                models.Document.id == image.doc_id
            ).first()
            doc.total_images += 1
            
            section = session.query(models.DocumentSection).filter(
                models.DocumentSection.section_id == image.section_id
            ).first()
            section.image_count += 1
            session.commit()
            session.refresh(db_image)
            
            return schema.DocumentImage.model_validate(db_image)

    def create_table(self, table: schema.DocumentTableCreate) -> schema.DocumentTable:
        """Create document table and update metrics."""
        with self.get_session() as session:
            db_table = models.DocumentTable(**table.model_dump())
            session.add(db_table)
            session.commit()
            
            # Update metrics
            doc = session.query(models.Document).filter(
                models.Document.id == table.doc_id
            ).first()
            doc.total_tables += 1
            
            section = session.query(models.DocumentSection).filter(
                models.DocumentSection.section_id == table.section_id
            ).first()
            section.table_count += 1
            session.commit()
            session.refresh(db_table)
            
            return schema.DocumentTable.model_validate(db_table)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and all its related data."""
        with self.get_session() as session:
            document = session.query(models.Document).filter(
                models.Document.id == doc_id
            ).first()
            if document:
                session.delete(document)
                session.commit()
                return True
            return False

```
</content>
</file_2>

<file_3>
<path>ragnostic/db/models.py</path>
<content>
```python
"""SQLAlchemy models for the document database."""
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Document(Base):
    """Core document tracking table."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    raw_file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    ingestion_date = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    
    # Document metrics
    total_sections = Column(Integer, nullable=False, default=0)
    total_images = Column(Integer, nullable=False, default=0)
    total_tables = Column(Integer, nullable=False, default=0)
    total_pages = Column(Integer, nullable=False, default=0)

 
class DocumentMetadata(Base):
    """Document metadata table."""
    __tablename__ = "document_metadata"

    doc_id = Column(String, ForeignKey("documents.id"), primary_key=True)
    title = Column(String)
    authors = Column(JSON)  # JSON array of authors
    creation_date = Column(DateTime)
    page_count = Column(Integer)
    language = Column(String)

    

class DocumentSection(Base):
    """Document's physical section structure."""
    __tablename__ = "document_sections"

    section_id = Column(String, primary_key=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    parent_section_id = Column(String, ForeignKey("document_sections.section_id"))
    level = Column(Integer, nullable=False)  # Header level (1=H1, etc)
    sequence_order = Column(Integer, nullable=False)  # Order in document
    
    # Section metrics
    word_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)

    # Hierarchical relationships
    parent_section = relationship("DocumentSection", remote_side=[section_id])
    child_sections = relationship("DocumentSection", overlaps="parent_section")
    
    # Content relationship
    content = relationship("SectionContent", uselist=False, backref="section")

class SectionContent(Base):
    """Dimension table for section content."""
    __tablename__ = "section_contents"
    
    section_id = Column(String, ForeignKey("document_sections.section_id"), 
                       primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    page_start = Column(Integer)
    page_end = Column(Integer)


class DocumentImage(Base):
    """Fact table for document images."""
    __tablename__ = "document_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    section_id = Column(String, ForeignKey("document_sections.section_id"), 
                       nullable=False)
    page_number = Column(Integer, nullable=False)
    image_data = Column(Text, nullable=False)  # Base64 encoded
    caption = Column(Text)


class DocumentTable(Base):
    """Fact table for document tables."""
    __tablename__ = "document_tables"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    section_id = Column(String, ForeignKey("document_sections.section_id"), 
                       nullable=False)
    page_number = Column(Integer, nullable=False)
    table_data = Column(JSON, nullable=False)  # JSON structured data
    caption = Column(Text)

```
</content>
</file_3>

<file_4>
<path>ragnostic/db/schema.py</path>
<content>
```python
"""Pydantic models for the document database using Pydantic v2."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DocumentBase(BaseModel):
    """Base document schema."""
    id: str
    raw_file_path: str
    file_hash: str
    file_size_bytes: int
    mime_type: str


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    pass


class Document(DocumentBase):
    """Schema for reading a document."""
    ingestion_date: datetime
    total_sections: int = Field(default=0)
    total_images: int = Field(default=0)
    total_tables: int = Field(default=0)
    total_pages: int = Field(default=0)

    model_config = ConfigDict(from_attributes=True)


class DocumentMetadataBase(BaseModel):
    """Base document metadata schema."""
    doc_id: str
    title: Optional[str] = None
    authors: Optional[List[str]] = Field(default=None, description="List of authors")
    creation_date: Optional[datetime] = None
    page_count: Optional[int] = None
    language: Optional[str] = None


class DocumentMetadataCreate(DocumentMetadataBase):
    """Schema for creating document metadata."""
    pass


class DocumentMetadata(DocumentMetadataBase):
    """Schema for reading document metadata."""
    model_config = ConfigDict(from_attributes=True)


class SectionContentBase(BaseModel):
    """Base section content schema."""
    section_id: str
    title: str
    content: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None


class SectionContentCreate(SectionContentBase):
    """Schema for creating section content."""
    pass


class SectionContent(SectionContentBase):
    """Schema for reading section content."""
    model_config = ConfigDict(from_attributes=True)


class DocumentSectionBase(BaseModel):
    """Base document section schema."""
    section_id: str
    doc_id: str
    parent_section_id: Optional[str] = None
    level: int = Field(description="Header level (1=H1, etc)")
    sequence_order: int
    word_count: int = Field(default=0)
    image_count: int = Field(default=0)
    table_count: int = Field(default=0)


class DocumentSectionCreate(DocumentSectionBase):
    """Schema for creating a document section."""
    pass


class DocumentSection(DocumentSectionBase):
    """Schema for reading a document section."""
    child_sections: List["DocumentSection"] = Field(default_factory=list)
    content: Optional[SectionContent] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentImageBase(BaseModel):
    """Base document image schema."""
    doc_id: str
    section_id: str
    image_data: str = Field(description="Base64 encoded image data")
    caption: Optional[str] = None
    page_number: int


class DocumentImageCreate(DocumentImageBase):
    """Schema for creating a document image."""
    pass


class DocumentImage(DocumentImageBase):
    """Schema for reading a document image."""
    id: int

    model_config = ConfigDict(from_attributes=True)


class DocumentTableBase(BaseModel):
    """Base document table schema."""
    doc_id: str
    section_id: str
    caption: Optional[str] = None
    table_data: Dict[str, Any] = Field(description="JSON structured table data")
    page_number: int


class DocumentTableCreate(DocumentTableBase):
    """Schema for creating a document table."""
    pass


class DocumentTable(DocumentTableBase):
    """Schema for reading a document table."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# Update forward references for nested models
DocumentSection.model_rebuild()
```
</content>
</file_4>

<file_5>
<path>ragnostic/ingestion/validation/__init__.py</path>
<content>
```python

```
</content>
</file_5>

<file_6>
<path>ragnostic/ingestion/validation/checks.py</path>
<content>
```python
"""Individual validation checks for document ingestion."""
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Union
import magic

from ragnostic.db.client import DatabaseClient
from .schema import ValidationCheckType, ValidationCheckFailure


def compute_file_hash(filepath: Path) -> Optional[str]:
    """Compute SHA-256 hash of file."""
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


def check_file_hash(filepath: Path) -> Union[str,ValidationCheckFailure]:
    """Compute SHA-256 hash of file.
    
    Returns:
        Tuple of (hash_value, check_failure). If successful, check_failure will be None.
    """
    hash_value = compute_file_hash(filepath)
    if hash_value is None:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.CORRUPTED_FILE,
            message="Unable to compute file hash"
        )
    return hash_value


def check_file_exists(filepath: Path) -> Union[bool, ValidationCheckFailure]:
    """Check if file exists and is a regular file."""
    if not filepath.exists() or not filepath.is_file():
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.OTHER,
            message="File does not exist or is not a regular file"
        )
    return True


def check_file_size(filepath: Path, max_size: int) -> Union[int, ValidationCheckFailure]:
    """Check if file size is within limits."""
    try:
        file_size = filepath.stat().st_size
    except Exception as e:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.PERMISSION_ERROR,
            message=f"Unable to check file size: {str(e)}"
        )
        
    if file_size > max_size:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.FILE_TOO_LARGE,
            message=f"File exceeds maximum size of {max_size} bytes",
            details={"file_size": file_size, "max_size": max_size}
        )
    return file_size
    

def check_mime_type(filepath: Path, supported_types: list[str]) -> Union[str, ValidationCheckFailure]:
    """Check if file mime type is supported."""
    try:
        mime_type = magic.from_file(str(filepath), mime=True)
        if mime_type not in supported_types:
            return ValidationCheckFailure(
                filepath=filepath,
                check_type=ValidationCheckType.INVALID_MIMETYPE,
                message=f"Unsupported mime type: {mime_type}",
                details={"mime_type": mime_type}
            )
    except Exception as e:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.OTHER,
            message=f"Unable to determine mime type: {str(e)}"
        )
    return mime_type
    

def check_hash_unique(filepath: Path, file_hash: str, db_client: DatabaseClient) -> Union[bool, ValidationCheckFailure]:
    """Check if file hash already exists in database."""
    existing_doc = db_client.get_document_by_hash(file_hash)
    if existing_doc:
        return ValidationCheckFailure(
            filepath=filepath,
            check_type=ValidationCheckType.DUPLICATE_HASH,
            message="Document with same hash already exists",
            details={"existing_doc_id": existing_doc.id}
        )
    return True

```
</content>
</file_6>

<file_7>
<path>ragnostic/ingestion/validation/schema.py</path>
<content>
```python
"""Validation schemas for the ingestion pipeline."""
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

class ValidationCheckType(str, Enum):
    """Types of validation check failures that can occur."""
    DUPLICATE_HASH = "duplicate_hash"
    INVALID_MIMETYPE = "invalid_mimetype"
    CORRUPTED_FILE = "corrupted_file"
    FILE_TOO_LARGE = "file_too_large"
    PERMISSION_ERROR = "permission_error"
    OTHER = "other"

class ValidationCheckFailure(BaseModel):
    """Represents a validation check failure for a file."""
    filepath: Path
    check_type: ValidationCheckType
    message: str
    details: Optional[dict] = Field(default=None, description="Additional check details")

class ValidationResult(BaseModel):
    """Result of validating a single file."""
    filepath: Path
    is_valid: bool
    file_hash: Optional[str] = Field(default=None, description="Hash of the file")
    mime_type: Optional[str] = Field(default=None, description="MIME type of the file")
    file_size_bytes: Optional[int] = Field(default=None, description="Size of the file in bytes")
    check_failures: List[ValidationCheckFailure] = Field(default_factory=list)

class BatchValidationResult(BaseModel):
    """Results from validating multiple files."""
    valid_files: List[ValidationResult] = Field(default_factory=list)
    invalid_files: List[ValidationResult] = Field(default_factory=list)
    
    @property
    def has_valid_files(self) -> bool:
        return len(self.valid_files) > 0
    
    @property
    def has_invalid_files(self) -> bool:
        return len(self.invalid_files) > 0
```
</content>
</file_7>

<file_8>
<path>ragnostic/ingestion/validation/validator.py</path>
<content>
```python
"""High-level document validation logic."""
from pathlib import Path
from typing import List, Optional

from ragnostic.db.client import DatabaseClient
from .schema import ValidationCheckFailure, ValidationCheckType, ValidationResult, BatchValidationResult
from .checks import (
    check_file_hash,
    check_file_exists,
    check_file_size,
    check_mime_type,
    check_hash_unique,
)

class DocumentValidator:
    """Validates documents before ingestion."""
    
    def __init__(
        self,
        db_client: DatabaseClient,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB default
        supported_mimetypes: Optional[List[str]] = None
    ):
        self.db_client = db_client
        self.max_file_size = max_file_size
        self.supported_mimetypes = supported_mimetypes or [
            'application/pdf',
            'application/x-pdf',
        ]
    
    def _validate_single_file(self, filepath: Path) -> ValidationResult:
        """Validate a single file against all validation checks.
        
        Checks are performed in order of severity and cost:
        1. File existence (fail fast if not found)
        2. File hash (needed for deduplication, fail if corrupted)
        3. Mime type (fail if unsupported type)
        4. File size (fail if too large)
        5. Hash uniqueness (fail if duplicate)
        """
        # Check file exists
        exists_result = check_file_exists(filepath)
        if isinstance(exists_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[exists_result]
            )

        # Check file can be hashed
        hash_result = check_file_hash(filepath)
        if isinstance(hash_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[hash_result]
            )
        file_hash = hash_result
            
        # Check mime type
        mime_result = check_mime_type(filepath, self.supported_mimetypes)
        if isinstance(mime_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[mime_result]
            )
        mime_type = mime_result
            
        # Check file size
        size_result = check_file_size(filepath, self.max_file_size)
        if isinstance(size_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False, 
                check_failures=[size_result]
            )
        file_size = size_result
            
        # Check hash uniqueness
        unique_result = check_hash_unique(filepath, file_hash, self.db_client)
        if isinstance(unique_result, ValidationCheckFailure):
            return ValidationResult(
                filepath=filepath,
                is_valid=False,
                check_failures=[unique_result]
            )
                
        # All checks passed, return successful validation
        return ValidationResult(
            filepath=filepath,
            is_valid=True,
            file_hash=file_hash,
            mime_type=mime_type,
            file_size_bytes=file_size,
            check_failures=[],
        )
    
    def validate_files(self, filepaths: List[Path]) -> BatchValidationResult:
        """Validate multiple files and return batch results."""
        results = BatchValidationResult()
        
        for filepath in filepaths:
            result = self._validate_single_file(filepath)
            if result.is_valid:
                results.valid_files.append(result)
            else:
                results.invalid_files.append(result)
        
        return results
```
</content>
</file_8>

<file_9>
<path>ragnostic/ingestion/__init__.py</path>
<content>
```python

```
</content>
</file_9>

<file_10>
<path>ragnostic/ingestion/monitor.py</path>
<content>
```python
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
```
</content>
</file_10>

<file_11>
<path>ragnostic/ingestion/schema.py</path>
<content>
```python
"""Pydantic models for the ingestion pipeline."""
from enum import Enum
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class IngestionStatus(str, Enum):
    """Status of the ingestion process."""
    PENDING = "pending"
    MONITORING = "monitoring"
    INGESTING = "ingesting"
    COMPLETED = "completed"
    ERROR = "error"


class MonitorResult(BaseModel):
    """Result of monitoring a directory for files to ingest."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    status: IngestionStatus
    files: List[Path] = Field(default_factory=list)
    error_message: str | None = None

    @property
    def has_files(self) -> bool:
        """Check if any files were found."""
        return len(self.files) > 0


class SupportedFileType(str, Enum):
    """Supported file types for ingestion."""
    PDF = ".pdf"
    PDF_CAPS = ".PDF"  # Some systems might use uppercase extension
    
    @classmethod
    def supported_types(cls) -> set[str]:
        """Get set of all supported file types."""
        return {member.value for member in cls}
```
</content>
</file_11>

<file_12>
<path>ragnostic/__init__.py</path>
<content>
```python
def main() -> None:
    print("Hello from ragnostic!")

```
</content>
</file_12>

<file_13>
<path>ragnostic/dag_ingestion.py</path>
<content>
```python
import pathlib
from burr.core import State, action, ApplicationBuilder

from ragnostic import utils

@action(reads=[], writes=["ingestion_status","ingestion_filepaths"])
def monitor(state: State, ingest_dir: str) -> State:
    """Checks if directory has files to ingest"""
    file_paths = []
    # Check filepath is valid
    path = pathlib.Path(ingest_dir)
    if (path.exists()) and (path.is_dir()):
        for p in path.iterdir():
            if p.suffix in ['.PDF','.pdf']:
                file_paths.append(str(p.resolve()))
        ingestion_status = "ingesting"
    else:
        #log status error
        ingestion_status="completed"
    
    return state.update(
        ingestion_status=ingestion_status, 
        ingestion_filepaths=file_paths
    )

@action(reads=["ingestion_filepaths"], writes=["valid_filepaths","invalid_filepaths"])
def validation(state: State, db_connection:str) -> State:
    """Check which files in the ingestion list are valid
    - not duplicates, etc.
    """
    valid_filepaths = []
    invalid_filepaths = []

    for filepath in state.get("ingestion_filepaths"):
        # Check duplicates
        # check with hash against the database?
        # - other checks?
        is_valid=True

        #move to list
        if is_valid:
            valid_filepaths.append(filepath)
        else:
            invalid_filepaths.append(filepath)

    return state.update(
        valid_filepaths=valid_filepaths, 
        invalid_filepaths=invalid_filepaths,
    )


@action(reads=["valid_filepaths"], writes=["successful_docs","failed_docs"])
def ingestion(state: State, storage_dir: str) -> State:
    """Process a batch of documents, tracking successes and failures."""
    
    filepaths = state.get("valid_filepaths")
    successful = []
    failed = []
    
    for p in filepaths:
        
        # Move file to new location
        copy_result = utils.copy_file(src_path=p, dest_dir=storage_dir)
        if not copy_result.success:
            failed.append((p, copy_result.error_code))
            continue
        # Generate new document ID and filename
        doc_id = utils.create_doc_id(prefix="DOC")
        suffix = pathlib.Path(p).suffix
        doc_filename = f"{doc_id}{suffix}"
        # Rename with document ID
        rename_result = utils.rename_file(file_path=copy_result.filepath, new_name=doc_filename)
        if not rename_result.success:
            failed.append((rename_result.filepath, rename_result.error_code))
            continue
        successful.append(rename_result.filepath)
    
    return state.update(successful_docs=successful, failed_docs=failed)

@action(reads=["successful_docs"], writes=["ingestion_status"])
def indexing(state: State, db_connection: str) -> State:
    """Update database with succesfully ingested docs"""
    successful = state.get("successful_docs")

    # Update database with all document ids
    # - primary key is document id
    # - filepath is storage path
    # - should we add metadata here? put a status for further processing?
    ingestion_status = "Completed"
    return state.update(ingestion_status=ingestion_status)

```
</content>
</file_13>

<file_14>
<path>ragnostic/utils.py</path>
<content>
```python
"""
Basic utilities for document ID generation and file operations.
"""
from dataclasses import dataclass
import string
from pathlib import Path
from shutil import copy2
from typing import Optional

from nanoid import generate

DEFAULT_ALPHABET = string.ascii_lowercase + string.digits  # 0-9a-z

@dataclass
class FileOperationResult:
    """
    Result of a file operation containing success status and relevant details.
    
    Attributes:
        success: Whether the operation succeeded
        filepath: Path to the resulting file if successful
        error: Exception object if an error occurred
        error_code: String code indicating the type of error
    """
    success: bool
    filepath: Optional[Path] = None
    error: Optional[Exception] = None
    error_code: Optional[str] = None


def create_doc_id(prefix: str = "DOC", size: int = 12, alphabet: str = DEFAULT_ALPHABET) -> str:
    """
    Create a new document ID with optional prefix.
    
    Args:
        prefix: String prefix for the ID (default: "DOC")
        size: Length of the random portion (default: 12)
        alphabet: String of characters to use for ID generation (default: numbers and lowercase letters)
    
    Returns:
        Document ID string in format {prefix}_{random string}
    
    Example:
        >>> create_doc_id("PDF")
        'PDF_x1y2z3a4b5c6'
    """
    random_id = generate(alphabet=alphabet, size=size)
    return f"{prefix}_{random_id}"

def copy_file(src_path: str | Path, dest_dir: str | Path) -> FileOperationResult:
    """
    Copy a file to destination directory.
    
    Args:
        src_path: Source file path
        dest_dir: Destination directory
        
    Returns:
        FileOperationResult containing success status and details
        
    Example:
        >>> result = copy_file('documents/test.pdf', 'archive/')
        >>> if result.success:
        ...     print(f"File copied to {result.filepath}")
        ... else:
        ...     print(f"Copy failed: {result.error_code}")
    """
    src_path = Path(src_path)
    dest_dir = Path(dest_dir)
    
    # Check source file
    if not src_path.is_file():
        return FileOperationResult(
            success=False,
            error=FileNotFoundError(f"Source file not found: {src_path}"),
            error_code="SOURCE_NOT_FOUND"
        )
    
    # Check destination directory
    if not dest_dir.is_dir():
        return FileOperationResult(
            success=False,
            error=NotADirectoryError(f"Destination is not a directory: {dest_dir}"),
            error_code="INVALID_DESTINATION"
        )
        
    try:
        # Copy file preserving metadata
        new_path = dest_dir / src_path.name
        copy2(src_path, new_path)
        return FileOperationResult(success=True, filepath=new_path)
        
    except PermissionError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="PERMISSION_DENIED"
        )
    except OSError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="COPY_FAILED"
        )

def rename_file(file_path: str | Path, new_name: str) -> FileOperationResult:
    """
    Rename a file in its current directory.
    
    Args:
        file_path: Path to file to rename
        new_name: New filename (not path)
        
    Returns:
        FileOperationResult containing success status and details
        
    Example:
        >>> result = rename_file('archive/old.pdf', 'new.pdf')
        >>> if result.success:
        ...     print(f"File renamed to {result.filepath}")
        ... else:
        ...     print(f"Rename failed: {result.error_code}")
    """
    file_path = Path(file_path)
    
    # Check source file
    if not file_path.is_file():
        return FileOperationResult(
            success=False,
            error=FileNotFoundError(f"File not found: {file_path}"),
            error_code="FILE_NOT_FOUND"
        )
        
    try:
        new_path = file_path.parent / new_name
        file_path.rename(new_path)
        return FileOperationResult(success=True, filepath=new_path)
        
    except PermissionError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="PERMISSION_DENIED"
        )
    except OSError as e:
        return FileOperationResult(
            success=False,
            error=e,
            error_code="RENAME_FAILED"
        )
```
</content>
</file_14>
