<file_1>
<path>ragnostic/__init__.py</path>
<content>
```python

```
</content>
</file_1>

<file_2>
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
</file_2>

<file_3>
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
    
    def get_documents(self, skip: int = 0, limit: int = 10) -> List[schema.Document]:
        """Get all documents with pagination."""
        with self.get_session() as session:
            documents = session.query(models.Document).offset(skip).limit(limit).all()
            return [schema.Document.model_validate(d) for d in documents]
        
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
</file_3>

<file_4>
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
</file_4>

<file_5>
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
</file_5>

<file_6>
<path>ragnostic/extraction/__init__.py</path>
<content>
```python

```
</content>
</file_6>

<file_7>
<path>ragnostic/extraction/workflow/__init__.py</path>
<content>
```python

```
</content>
</file_7>

<file_8>
<path>ragnostic/extraction/workflow/actions.py</path>
<content>
```python
import pathlib
from burr.core import State, action, ApplicationBuilder
from burr.core import when

from ragnostic import utils

@action(reads=[], writes=["document_kind"])
def document_router(state: State, doc_id: str, db_connection) -> State:
    """Determine how to process the doc"""

    # Determine how to process the doc id based on the library entry
    # - Is it a PDF or a HTML?
    # - has it already been processed before?

    #Design Choices:
    # - should we load the document here or later?
    # - if loaded should we store it in the state as a python object?
    return state.update(document_kind='pdf')

@action(reads=[], writes=[])
def text_extraction(state: State, db_connection) -> State:
    """extract text"""
    # Extract text from pdf
    # - use the docling parser
    # - grab the raw text as is initially

    # Design Choices:
    # - should we store the docling parsed object in state and run various extraction steps on it?
    return state

@action(reads=[], writes=[])
def image_extraction(state: State, db_connection) -> State:
    """extract image"""

    # Extract and add images to database
    # - take docling object and put images with their metadata in the database
    
    # Design Choices:
    # - what inputs do we need? the docling objkect? the doc id and load it from database?
    
    return state

@action(reads=[], writes=[])
def table_extraction(state: State, db_connection) -> State:
    """extract table"""
    # Extract and add tables to database
    # - take docling object and put tables with their metadata in the database
    
    # Design Choices:
    # - what inputs do we need? the docling object? the doc id and load it from database?
    
    return state

@action(reads=[], writes=[])
def wikipedia_extraction(state: State, db_connection) -> State:
    """extract wikipedia"""

    # Design choices
    # Should we grab the HTML and store it then parse?
    # - should we just use the wikipedia API?
    # - should we do an image step later as well? 
    # - how would we identify images?
    return state

@action(reads=[], writes=[])
def metadata_extraction(state: State, db_connection) -> State:
    """extract table"""

    # Compile the metadata based on the previous steps
    # - does it have images, tables, etc?
    # - how many pages, etc
    # - status updates on the steps, flags, etc.
    
    return state
    
# Build and visualize graph/logic
(
    ApplicationBuilder()
    .with_actions(
        route=document_router, 
        pdf_text=text_extraction, 
        pdf_image=image_extraction, 
        pdf_table=table_extraction,
        pdf_metadata=metadata_extraction,
        wiki_extraction=wikipedia_extraction,
    )
    .with_transitions(
        ("route", "pdf_text", when(document_kind='pdf')),
        ("pdf_text", "pdf_image"),
        ("pdf_image", "pdf_table"),
        ("pdf_table", "pdf_metadata"),
        ("route", "wiki_extraction", ~when(document_kind='pdf')),
        ("wiki_extraction", "pdf_metadata"),
    )
    .with_entrypoint("route")
    .build()
)
```
</content>
</file_8>

<file_9>
<path>ragnostic/ingestion/__init__.py</path>
<content>
```python
"""Ingtestion package initialization."""
from .workflow import *

from .monitor import *
from .validation import *
from .processor import *
from .indexing import *
from .utils import create_doc_id

```
</content>
</file_9>

<file_10>
<path>ragnostic/ingestion/indexing/__init__.py</path>
<content>
```python
"""Document indexing package."""
from .indexer import DocumentIndexer
from .schema import IndexingResult, BatchIndexingResult, IndexingStatus

__all__ = [
    "DocumentIndexer",
    "IndexingResult",
    "BatchIndexingResult",
    "IndexingStatus"
]
```
</content>
</file_10>

<file_11>
<path>ragnostic/ingestion/indexing/extraction.py</path>
<content>
```python
"""PDF metadata and text extraction functionality."""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf4llm

from .schema import DocumentMetadataExtracted

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Handles PDF metadata and text extraction using pymupdf4llm."""
    
    def __init__(self, text_preview_chars: int = 1000):
        """Initialize the PDF extractor.
        
        Args:
            extract_text: Whether to extract text preview
            text_preview_chars: Number of characters to extract for preview
        """
        self.text_preview_chars = text_preview_chars
    
    def extract_metadata(self, filepath: Path) -> Tuple[Optional[DocumentMetadataExtracted], Optional[str]]:
        """Extract metadata and optional text preview from PDF.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            Tuple of (metadata, error_message)
            If successful, error_message will be None
        """
        try:
            # Open PDF with pymupdf4llm
            page_chunks  = pymupdf4llm.to_markdown(str(filepath), page_chunks=True)
            
            # Extract basic metadata
            metadata = self._parse_page_chunks(page_chunks)
            
            # Extract text preview if enabled
            text = metadata.text_preview
            if text:
                metadata.text_preview = text[:self.text_preview_chars]

        except Exception as e:
            error_msg = f"Metadata extraction failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
        
        return metadata, None
            
        
    def _parse_authors(self, author_str: Optional[str]) -> Optional[List[str]]:
        """Parse author string into list of authors."""
        if not author_str:
            return None
        # Split on common separators and clean up
        authors = [a.strip() for a in author_str.replace(";", ",").split(",")]
        return [a for a in authors if a]  # Remove empty strings
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse PDF date string into datetime object."""
        if not date_str:
            return None
        try:
            # Handle common PDF date formats
            # TODO: Implement proper PDF date parsing
            return datetime.now()  # Placeholder
        except Exception:
            return None
        
    def _parse_page_chunks(self, page_chunks: list[dict],) -> DocumentMetadataExtracted:
        """Parse page chunks from pymupdf4llm into document metadata.
        
        Args:
            page_chunks: List of page chunk dictionaries from pymupdf4llm
            
        Returns:
            DocumentMetadataExtracted with parsed metadata and text preview
            
        Notes:
            - Uses first chunk for document-level metadata
            - Combines preview text from multiple chunks up to limit
            - Handles missing or empty metadata fields
        """
        if not page_chunks:
            return DocumentMetadataExtracted(text_preview="") #without this it returns None..
        
        # Get metadata from first chunk as it contains document info
        first_chunk = page_chunks[0]
        metadata = first_chunk.get('metadata', {})
        
        # Extract creation date
        creation_date = None
        if date_str := metadata.get('creationDate'):
            try:
                # TODO: Implement PDF date string parsing
                creation_date = self._parse_date(date_str)
            except Exception:
                pass
                
        # Build text preview from chunks
        chunk_texts = []
        for chunk in page_chunks:
            if chunk_text := chunk.get('text', ''):
                chunk_texts.append(chunk_text)
        
        text_preview = "\n".join(chunk_texts)
        if len(text_preview) >= self.text_preview_chars:
            text_preview = text_preview[:self.text_preview_chars]
                        
        # Parse authors if present
        authors = self._parse_authors(metadata.get('author'))
                    
        return DocumentMetadataExtracted(
            title=metadata.get('title'),
            authors=authors,
            creation_date=creation_date,
            page_count=metadata.get('page_count'),
            language=metadata.get('language'),
            text_preview=text_preview.strip()
        )
```
</content>
</file_11>

<file_12>
<path>ragnostic/ingestion/indexing/indexer.py</path>
<content>
```python
"""Document indexing functionality."""
import logging
from pathlib import Path
from typing import List, Optional, Set

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import Document, DocumentCreate, DocumentMetadata, DocumentMetadataCreate
from ragnostic.ingestion.validation.checks import compute_file_hash
import magic

from .extraction import PDFExtractor
from .schema import IndexingResult, BatchIndexingResult, IndexingStatus

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Handles document indexing operations."""
    
    SUPPORTED_MIME_TYPES: Set[str] = {'application/pdf', 'application/x-pdf'}

    def __init__(self, 
                 db_client: DatabaseClient,
                 text_preview_chars: int = 1000):
        """Initialize document indexer.
        
        Args:
            db_client: Database client instance
            extract_text: Whether to extract text preview
            text_preview_chars: Number of characters for text preview
        """
        self.db_client = db_client
        self.extractor = PDFExtractor(
            text_preview_chars=text_preview_chars
        )
    
    def index_document(self, filepath: Path) -> IndexingResult:
        """Index a single document with metadata.
        
        Args:
            filepath: Path to document to index
            
        Returns:
            IndexingResult with status and details
        """
        try:
            # Validate mime type first
            mime_type = magic.from_file(str(filepath), mime=True)
            if mime_type not in self.SUPPORTED_MIME_TYPES:
                return IndexingResult(
                    doc_id=filepath.stem,
                    filepath=filepath,
                    status=IndexingStatus.METADATA_ERROR,
                    error_message=f"Unsupported file type: {mime_type}"
                )
            
            # Get certain metadata
            file_hash = compute_file_hash(filepath)
            if not file_hash:
                return IndexingResult(
                    doc_id="ERROR",
                    filepath=filepath,
                    status=IndexingStatus.METADATA_ERROR,
                    error_message="Failed to compute file hash"
                )
            
            file_size = filepath.stat().st_size
            
            # Create document record
            doc = DocumentCreate(
                id=filepath.stem,  # Using filename as ID for now
                raw_file_path=str(filepath),
                file_hash=file_hash,
                file_size_bytes=file_size,
                mime_type=mime_type
            )
            
            try:
                db_doc = self.db_client.create_document(doc)
            except ValueError as e:
                return IndexingResult(
                    doc_id=doc.id,
                    filepath=filepath,
                    status=IndexingStatus.DATABASE_ERROR,
                    error_message=str(e)
                )
            
            # Extract optional metadata
            extracted_metadata, error = self.extractor.extract_metadata(filepath)
            if extracted_metadata:
                # Create metadata record
                metadata = DocumentMetadataCreate(
                    doc_id=db_doc.id,
                    title=extracted_metadata.title,
                    authors=extracted_metadata.authors,
                    creation_date=extracted_metadata.creation_date,
                    page_count=extracted_metadata.page_count,
                    language=extracted_metadata.language
                )
                
                try:
                    self.db_client.create_metadata(metadata)
                except ValueError as e:
                    logger.warning(f"Failed to store metadata: {e}")
                    # Continue without metadata
            
            return IndexingResult(
                doc_id=db_doc.id,
                filepath=filepath,
                status=IndexingStatus.SUCCESS,
                extracted_metadata=extracted_metadata
            )
            
        except Exception as e:
            error_msg = f"Indexing failed: {str(e)}"
            logger.error(error_msg)
            return IndexingResult(
                doc_id="ERROR",
                filepath=filepath,
                status=IndexingStatus.UNKNOWN_ERROR,
                error_message=error_msg
            )
    
    def index_batch(self, filepaths: List[Path]) -> BatchIndexingResult:
        """Index multiple documents.
        
        Args:
            filepaths: List of paths to documents to index
            
        Returns:
            BatchIndexingResult with combined results
        """
        results = BatchIndexingResult()
        
        for filepath in filepaths:
            result = self.index_document(filepath)
            if result.status == IndexingStatus.SUCCESS:
                results.successful_docs.append(result)
            else:
                results.failed_docs.append(result)
        
        return results
```
</content>
</file_12>

<file_13>
<path>ragnostic/ingestion/indexing/schema.py</path>
<content>
```python
"""Schema definitions for document indexing."""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class IndexingStatus(str, Enum):
    """Status of document indexing operation."""
    SUCCESS = "success"
    METADATA_ERROR = "metadata_error"
    EXTRACTION_ERROR = "extraction_error"
    DATABASE_ERROR = "database_error"
    UNKNOWN_ERROR = "unknown_error"


class DocumentMetadataExtracted(BaseModel):
    """Optional metadata that requires PDF parsing."""
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    creation_date: Optional[datetime] = None
    page_count: Optional[int] = Field(None, ge=0, description="Total number of pages in document. Must be >= 0 if provided")
    language: Optional[str] = None
    text_preview: Optional[str] = Field(None, description="First page or N characters of text")

    model_config = dict(arbitrary_types_allowed=True)


class IndexingResult(BaseModel):
    """Result of indexing a single document."""
    doc_id: str
    filepath: Path
    status: IndexingStatus
    error_message: Optional[str] = None
    extracted_metadata: Optional[DocumentMetadataExtracted] = None
    
    model_config = dict(arbitrary_types_allowed=True)


class BatchIndexingResult(BaseModel):
    """Results from indexing multiple documents."""
    successful_docs: List[IndexingResult] = Field(default_factory=list)
    failed_docs: List[IndexingResult] = Field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        """Check if any documents failed indexing."""
        return len(self.failed_docs) > 0

    @property
    def success_count(self) -> int:
        """Get count of successfully indexed documents."""
        return len(self.successful_docs)

    @property
    def failure_count(self) -> int:
        """Get count of failed documents."""
        return len(self.failed_docs)
```
</content>
</file_13>

<file_14>
<path>ragnostic/ingestion/monitor/__init__.py</path>
<content>
```python
"""Directory monitoring functionality for document ingestion."""
from .monitor import DirectoryMonitor
from .schema import MonitorResult, MonitorStatus

__all__ = [
    "DirectoryMonitor",
    "MonitorResult",
    "MonitorStatus",
]

```
</content>
</file_14>

<file_15>
<path>ragnostic/ingestion/monitor/monitor.py</path>
<content>
```python


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
```
</content>
</file_15>

<file_16>
<path>ragnostic/ingestion/monitor/schema.py</path>
<content>
```python
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

```
</content>
</file_16>

<file_17>
<path>ragnostic/ingestion/processor/__init__.py</path>
<content>
```python
"""Document processor package."""
from .processor import DocumentProcessor
from .schema import ProcessingResult, BatchProcessingResult, ProcessingStatus

__all__ = [
    "DocumentProcessor",
    "ProcessingResult", 
    "BatchProcessingResult",
    "ProcessingStatus"
]
```
</content>
</file_17>

<file_18>
<path>ragnostic/ingestion/processor/processor.py</path>
<content>
```python
"""Document processing functionality."""
import logging
from pathlib import Path
from typing import List

from ragnostic.ingestion.utils import create_doc_id
from .schema import BatchProcessingResult, ProcessingResult, ProcessingStatus
from .storage import store_document


logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing and storage operations."""
    
    def __init__(self, doc_id_prefix: str = "DOC"):
        """Initialize processor with configuration.
        
        Args:
            doc_id_prefix: Prefix to use for document IDs
        """
        self.doc_id_prefix = doc_id_prefix
    
    def process_documents(
        self,
        file_paths: List[Path],
        storage_dir: Path
    ) -> BatchProcessingResult:
        """Process a batch of validated documents.
        
        Args:
            file_paths: List of paths to validated documents
            storage_dir: Directory to store processed documents
        
        Returns:
            BatchProcessingResult containing results for all documents
        """
        results = BatchProcessingResult()
        
        for file_path in file_paths:
            try:
                result = self._process_single_document(file_path, storage_dir)
                
                if result.status == ProcessingStatus.SUCCESS:
                    results.successful_docs.append(result)
                else:
                    results.failed_docs.append(result)
                    
            except Exception as e:
                logger.exception(f"Unexpected error processing {file_path}")
                results.failed_docs.append(
                    ProcessingResult(
                        doc_id="ERROR",
                        original_path=file_path,
                        status=ProcessingStatus.UNKNOWN_ERROR,
                        error_message=str(e),
                        error_code="UNEXPECTED_ERROR"
                    )
                )
        
        return results
    
    def _process_single_document(
        self,
        file_path: Path,
        storage_dir: Path
    ) -> ProcessingResult:
        """Process a single document.
        
        Args:
            file_path: Path to document to process
            storage_dir: Directory to store processed document
        
        Returns:
            ProcessingResult with status and details
        """
        # Generate document ID
        doc_id = create_doc_id(prefix=self.doc_id_prefix)
        
        # Store document
        result = store_document(
            source_path=file_path,
            storage_dir=storage_dir,
            doc_id=doc_id
        )
        
        return result
```
</content>
</file_18>

<file_19>
<path>ragnostic/ingestion/processor/schema.py</path>
<content>
```python
"""Schema definitions for document processing."""
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Status of document processing operation."""
    SUCCESS = "success"
    STORAGE_ERROR = "storage_error"
    COPY_ERROR = "copy_error"
    RENAME_ERROR = "rename_error"
    UNKNOWN_ERROR = "unknown_error"


class ProcessingResult(BaseModel):
    """Result of processing a single document."""
    doc_id: str
    original_path: Path
    storage_path: Optional[Path] = None
    status: ProcessingStatus
    error_message: Optional[str] = None
    error_code: Optional[str] = None

    model_config = dict(arbitrary_types_allowed=True)


class BatchProcessingResult(BaseModel):
    """Results from processing multiple documents."""
    successful_docs: List[ProcessingResult] = Field(default_factory=list)
    failed_docs: List[ProcessingResult] = Field(default_factory=list)

    model_config = dict(arbitrary_types_allowed=True)

    @property
    def has_failures(self) -> bool:
        """Check if any documents failed processing."""
        return len(self.failed_docs) > 0

    @property
    def success_count(self) -> int:
        """Get count of successfully processed documents."""
        return len(self.successful_docs)

    @property
    def failure_count(self) -> int:
        """Get count of failed documents."""
        return len(self.failed_docs)
```
</content>
</file_19>

<file_20>
<path>ragnostic/ingestion/processor/storage.py</path>
<content>
```python
"""Storage operations for document processing."""
from pathlib import Path
from shutil import copy2
from typing import Optional

from .schema import ProcessingStatus, ProcessingResult


def store_document(
    source_path: Path,
    storage_dir: Path,
    doc_id: str
) -> ProcessingResult:
    """Store document in the target location with proper error handling.
    
    Args:
        source_path: Path to source document
        storage_dir: Directory to store document in
        doc_id: Generated document ID
    
    Returns:
        ProcessingResult with status and details
    """
    # Create result with initial values
    result = ProcessingResult(
        doc_id=doc_id,
        original_path=source_path,
        status=ProcessingStatus.SUCCESS
    )
    
    # Validate source file
    if not source_path.is_file():
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": f"Source file not found: {source_path}",
            "error_code": "SOURCE_NOT_FOUND"
        })
    
    # Validate storage directory
    if not storage_dir.is_dir():
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": f"Storage directory invalid: {storage_dir}",
            "error_code": "INVALID_STORAGE_DIR"
        })
    
    try:
        # Generate destination path with original extension
        suffix = source_path.suffix
        dest_filename = f"{doc_id}{suffix}"
        dest_path = storage_dir / dest_filename
        
        # Copy file preserving metadata
        copy2(source_path, dest_path)
        
    except PermissionError as e:
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": str(e),
            "error_code": "PERMISSION_DENIED"
        })
    except OSError as e:
        return result.model_copy(update={
            "status": ProcessingStatus.STORAGE_ERROR,
            "error_message": str(e),
            "error_code": "STORAGE_FAILED"
        })
    except Exception as e:
        return result.model_copy(update={
            "status": ProcessingStatus.UNKNOWN_ERROR,
            "error_message": str(e),
            "error_code": "UNKNOWN"
        })
    
    # Success
    return result.model_copy(update={
        "storage_path": dest_path
    })
```
</content>
</file_20>

<file_21>
<path>ragnostic/ingestion/utils.py</path>
<content>
```python
"""
Basic utilities for document ingestion.
"""
import string

from nanoid import generate

DEFAULT_ALPHABET = string.ascii_lowercase + string.digits  # 0-9a-z

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

```
</content>
</file_21>

<file_22>
<path>ragnostic/ingestion/validation/__init__.py</path>
<content>
```python
"""Document processor package."""
from .validator import DocumentValidator
from .schema import ValidationResult, BatchValidationResult, ValidationCheckType, ValidationCheckFailure

__all__ = [
    "DocumentValidator",
    "ValidationResult", 
    "BatchValidationResult",
    "ValidationCheckType",
    "ValidationCheckFailure",
]
```
</content>
</file_22>

<file_23>
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
</file_23>

<file_24>
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
</file_24>

<file_25>
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
</file_25>

<file_26>
<path>ragnostic/ingestion/workflow/__init__.py</path>
<content>
```python
"""Workflow package initialization."""
from .application import build_ingestion_workflow, run_ingestion
from .actions import (
    monitor_action,
    validation_action,
    processing_action,
    indexing_action,
)

__all__ = [
    # Main application builder
    "build_ingestion_workflow",
    "run_ingestion",

    # Individual actions for custom workflows
    "monitor_action",
    "validation_action", 
    "processing_action",
    "indexing_action",
]
```
</content>
</file_26>

<file_27>
<path>ragnostic/ingestion/workflow/actions.py</path>
<content>
```python
"""Action definitions for document ingestion workflow."""
from pathlib import Path
from typing import List

from burr.core import State, action

from ragnostic.db.client import DatabaseClient
from ragnostic.ingestion.monitor import DirectoryMonitor, MonitorStatus
from ragnostic.ingestion.validation import DocumentValidator
from ragnostic.ingestion.processor import DocumentProcessor
from ragnostic.ingestion.indexing import DocumentIndexer


@action(reads=[], writes=["monitor_result","error"])
def monitor_action(state: State, ingest_dir: str) -> State:
    """Monitor directory for new files to process.
    
    Args:
        state: Current workflow state
        ingest_dir: Directory path to monitor
        
    Returns:
        Updated state with monitor_result
    """
    monitor = DirectoryMonitor()
    result = monitor.get_ingestible_files(ingest_dir)
    
    if result.status == MonitorStatus.ERROR:
        return state.update(
            monitor_result=result,
            error=f"Monitor error: {result.error_message}"
        )
        
    return state.update(monitor_result=result, error=None)


@action(
    reads=["monitor_result"],
    writes=["validation_result","error"]
)
def validation_action(
    state: State,
    db_client: DatabaseClient,
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
) -> State:
    """Validate monitored files.
    
    Args:
        state: Current workflow state
        db_client: Database client for duplicate checks
        max_file_size: Maximum allowed file size in bytes
        
    Returns:
        Updated state with validation results
    """
    monitor_result = state.get("monitor_result")
    if not monitor_result.has_files:
        return state.update(
            validation_result=None,
            error="No files to validate"
        )
        
    validator = DocumentValidator(
        db_client=db_client,
        max_file_size=max_file_size
    )
    
    validation_result = validator.validate_files(monitor_result.files)
    return state.update(validation_result=validation_result, error=None)


@action(
    reads=["validation_result"],
    writes=["processing_result","error"]
)
def processing_action(state: State, storage_dir: str) -> State:
    """Process validated documents.
    
    Args:
        state: Current workflow state
        storage_dir: Directory for processed document storage
        
    Returns:
        Updated state with processing results
    """
    validation_result = state.get("validation_result")
    if not validation_result or not validation_result.has_valid_files:
        return state.update(
            processing_result=None,
            error="No valid files to process"
        )
    
    # Get valid file paths
    valid_files = [result.filepath for result in validation_result.valid_files]
    
    processor = DocumentProcessor()
    processing_result = processor.process_documents(
        file_paths=valid_files,
        storage_dir=Path(storage_dir)
    )
    
    return state.update(processing_result=processing_result, error=None)


@action(
    reads=["processing_result"],
    writes=["indexing_result", "error"]
)
def indexing_action(
    state: State,
    db_client: DatabaseClient,
    text_preview_chars: int = 1000
) -> State:
    """Index processed documents.
    
    Args:
        state: Current workflow state
        db_client: Database client for document indexing
        text_preview_chars: Number of characters for text preview
        
    Returns:
        Updated state with indexing results
    """
    processing_result = state.get("processing_result")
    if processing_result is None or len(processing_result.successful_docs)==0:
        return state.update(
            indexing_result=None,
            error="No successfully processed documents to index"
        )
    # Get successful document paths
    successful_paths = [
        Path(result.storage_path)
        for result in processing_result.successful_docs
    ]
    
    indexer = DocumentIndexer(
        db_client=db_client,
        text_preview_chars=text_preview_chars
    )
    
    indexing_result = indexer.index_batch(successful_paths)
    return state.update(indexing_result=indexing_result, error=None)
```
</content>
</file_27>

<file_28>
<path>ragnostic/ingestion/workflow/application.py</path>
<content>
```python
import pathlib
from burr.core import ApplicationBuilder
from ragnostic import ingestion
from ragnostic import db

def build_ingestion_workflow(
    storage_dir: str = "./document_storage",
    db_path: str | None = None,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
    text_preview_chars: int = 1000
):
    """Build the document ingestion workflow application.
    
    Args:
        ingest_dir: Directory to monitor for new documents
        storage_dir: Directory to store processed documents
        db_path: Optional path to SQLite database. If None creates a new one
        max_file_size: Maximum allowed file size in bytes
        text_preview_chars: Number of characters for text preview
        
    Returns:
        Configured workflow application
    """
    # Ensure directories exist
    pathlib.Path(storage_dir).mkdir(parents=True, exist_ok=True)
    
    # Create database client
    db_url = db.create_sqlite_url(db_path)
    db_client = db.DatabaseClient(db_url)
    
    # Build workflow
    app = ApplicationBuilder()
    
    # Add monitor action
    app = app.with_actions(
        monitor=ingestion.monitor_action, 
        validation=ingestion.validation_action.bind(db_client=db_client,max_file_size=max_file_size),
        processing=ingestion.processing_action.bind(storage_dir=storage_dir), 
        indexing=ingestion.indexing_action.bind(db_client=db_client, text_preview_chars=text_preview_chars),
    )
    
    app = app.with_transitions(
        ("monitor", "validation"),
        ("validation", "processing"),
        ("processing", "indexing"),
    )
    
    app = app.with_entrypoint("monitor")


    return app.build()

def run_ingestion(ingest_dir = "./ingest", **kwargs):
    """Run the document ingestion workflow.
    
    Args:
        ingest_dir: Directory to monitor for new documents
        **kwargs: Additional arguments for build_ingestion_workflow
    """
    # Default args from environment
    storage_dir = kwargs.get('storage_dir', './storage')
    db_path = kwargs.get('db_path', None)
    max_file_size = kwargs.get('max_file_size', 100 * 1024 * 1024)  # 100MB
    text_preview_chars = kwargs.get('text_preview_chars', 1000)

    workflow = build_ingestion_workflow(**kwargs)
    *_, state = workflow.run(
        halt_after=['indexing'],
        inputs={"ingest_dir": ingest_dir}
    )
    return state

```
</content>
</file_28>
