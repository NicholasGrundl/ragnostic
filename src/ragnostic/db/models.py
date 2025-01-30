"""SQLAlchemy models for the document database."""
from datetime import datetime
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
    ingestion_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    metadata = relationship("DocumentMetadata", back_populates="document", uselist=False)
    sections = relationship("DocumentSection", back_populates="document")
    images = relationship("DocumentImage", back_populates="document")
    tables = relationship("DocumentTable", back_populates="document")


class DocumentMetadata(Base):
    """Document metadata table."""
    __tablename__ = "document_metadata"

    doc_id = Column(String, ForeignKey("documents.id"), primary_key=True)
    title = Column(String)
    authors = Column(JSON)  # JSON array of authors
    description = Column(Text)
    creation_date = Column(DateTime)
    page_count = Column(Integer)
    language = Column(String)

    # Relationships
    document = relationship("Document", back_populates="metadata")


class DocumentSection(Base):
    """Document's physical section structure."""
    __tablename__ = "document_sections"

    section_id = Column(String, primary_key=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    parent_section_id = Column(String, ForeignKey("document_sections.section_id"))
    level = Column(Integer, nullable=False)  # Header level (1=H1, etc)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sequence_order = Column(Integer, nullable=False)  # Order in document
    page_start = Column(Integer)
    page_end = Column(Integer)

    # Relationships
    document = relationship("Document", back_populates="sections")
    parent_section = relationship("DocumentSection", remote_side=[section_id])
    child_sections = relationship("DocumentSection")
    images = relationship("DocumentImage", back_populates="section")
    tables = relationship("DocumentTable", back_populates="section")


class DocumentImage(Base):
    """Document images table."""
    __tablename__ = "document_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    section_id = Column(String, ForeignKey("document_sections.section_id"), nullable=False)
    image_data = Column(Text, nullable=False)  # Base64 encoded
    caption = Column(Text)
    embedding_id = Column(String)  # Vector store reference
    page_number = Column(Integer, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="images")
    section = relationship("DocumentSection", back_populates="images")


class DocumentTable(Base):
    """Document tables table."""
    __tablename__ = "document_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, ForeignKey("documents.id"), nullable=False)
    section_id = Column(String, ForeignKey("document_sections.section_id"), nullable=False)
    caption = Column(Text)
    table_data = Column(JSON, nullable=False)  # JSON structured data
    page_number = Column(Integer, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="tables")
    section = relationship("DocumentSection", back_populates="tables")
