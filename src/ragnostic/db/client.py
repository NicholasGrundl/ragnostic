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
