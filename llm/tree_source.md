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
<path>ingestion/validation/__init__.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/validation/__init__.py'
</content>
</file_5>

<file_6>
<path>ingestion/validation/checks.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/validation/checks.py'
</content>
</file_6>

<file_7>
<path>ingestion/validation/schema.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/validation/schema.py'
</content>
</file_7>

<file_8>
<path>ingestion/validation/validator.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/validation/validator.py'
</content>
</file_8>

<file_9>
<path>ingestion/__init__.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/__init__.py'
</content>
</file_9>

<file_10>
<path>ingestion/monitor.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/monitor.py'
</content>
</file_10>

<file_11>
<path>ingestion/schema.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/ingestion/schema.py'
</content>
</file_11>

<file_12>
<path>__init__.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/__init__.py'
</content>
</file_12>

<file_13>
<path>dag_ingestion.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/dag_ingestion.py'
</content>
</file_13>

<file_14>
<path>utils.py</path>
<content>

Error reading file: [Errno 2] No such file or directory: '/home/nicholasgrundl/projects/ragnostic/src/utils.py'
</content>
</file_14>
