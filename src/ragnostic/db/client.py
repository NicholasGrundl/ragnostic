"""Database client for handling all database operations."""
from typing import Optional, List
from sqlalchemy import create_engine
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

    def create_section(self, section: schema.DocumentSectionCreate) -> schema.DocumentSection:
        """Create document section."""
        with self.get_session() as session:
            db_section = models.DocumentSection(**section.model_dump())
            session.add(db_section)
            try:
                session.commit()
                session.refresh(db_section)
                return schema.DocumentSection.model_validate(db_section)
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Section {section.section_id} already exists")

    def get_document_sections(self, doc_id: str) -> List[schema.DocumentSection]:
        """Get all sections for a document ordered by sequence."""
        with self.get_session() as session:
            results = session.query(models.DocumentSection).filter(
                models.DocumentSection.doc_id == doc_id
            ).order_by(models.DocumentSection.sequence_order).all()
            return [schema.DocumentSection.model_validate(r) for r in results]

    def create_image(self, image: schema.DocumentImageCreate) -> schema.DocumentImage:
        """Create document image."""
        with self.get_session() as session:
            db_image = models.DocumentImage(**image.model_dump())
            session.add(db_image)
            session.commit()
            session.refresh(db_image)
            return schema.DocumentImage.model_validate(db_image)

    def get_section_images(self, section_id: str) -> List[schema.DocumentImage]:
        """Get all images for a section."""
        with self.get_session() as session:
            results = session.query(models.DocumentImage).filter(
                models.DocumentImage.section_id == section_id
            ).order_by(models.DocumentImage.page_number).all()
            return [schema.DocumentImage.model_validate(r) for r in results]

    def create_table(self, table: schema.DocumentTableCreate) -> schema.DocumentTable:
        """Create document table."""
        with self.get_session() as session:
            db_table = models.DocumentTable(**table.model_dump())
            session.add(db_table)
            session.commit()
            session.refresh(db_table)
            return schema.DocumentTable.model_validate(db_table)

    def get_section_tables(self, section_id: str) -> List[schema.DocumentTable]:
        """Get all tables for a section."""
        with self.get_session() as session:
            results = session.query(models.DocumentTable).filter(
                models.DocumentTable.section_id == section_id
            ).order_by(models.DocumentTable.page_number).all()
            return [schema.DocumentTable.model_validate(r) for r in results]

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
