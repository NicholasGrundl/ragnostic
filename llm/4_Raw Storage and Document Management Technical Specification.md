# Raw Storage and Document Management Technical Specification

## Overview
The storage system consists of two main components: a flat filesystem structure for raw document storage and a SQLite database for document management and metadata. This design separates raw file preservation from document processing and management, providing a clean, efficient system that supports the hierarchical RAG pipeline while maintaining simplicity for the MVP.

## System Components

### File Storage System
The File Storage System maintains original document files in their raw form using a simple, flat directory structure. It focuses solely on preserving original documents with minimal organizational complexity.

- Base directory structure:
  * /raw_documents
    * /wikipedia  # Wikipedia article downloads
    * /textbooks  # PDF textbooks
    * /journals   # Journal articles
- Simple file naming using document IDs
- Basic file operations (save, delete, retrieve)
- Filesystem monitoring for space and health
- Basic backup support

#### Scaling Considerations
- Cloud storage integration
- Distributed filesystem support
- Enhanced backup strategies
- Multi-node access patterns

### Document Management Database
The Document Management Database (SQLite) tracks all document metadata and processing state, providing a single source of truth for document information while maintaining relationships between raw files and processed content.

#### Database Schema

```sql
-- Core document metadata
CREATE TABLE documents (
    id TEXT PRIMARY KEY,           -- Unique document identifier
    filepath TEXT NOT NULL,        -- Path to raw file
    doc_type TEXT NOT NULL,        -- 'wikipedia', 'textbook', 'journal'
    title TEXT NOT NULL,
    authors TEXT,                  -- JSON array of authors
    publication_date DATE,
    ingestion_date DATETIME NOT NULL,
    last_processed DATETIME,
    has_tables BOOLEAN DEFAULT FALSE,
    has_images BOOLEAN DEFAULT FALSE,
    status TEXT NOT NULL,          -- 'ingested', 'processing', 'complete', 'error'
    file_hash TEXT NOT NULL,       -- For duplicate detection
    metadata JSON                  -- Additional metadata as JSON
);

-- Document text content
CREATE TABLE document_text (
    doc_id TEXT PRIMARY KEY,
    raw_text TEXT NOT NULL,
    text_length INTEGER,
    last_updated DATETIME NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

-- Processing history
CREATE TABLE processing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

-- Index definitions
CREATE INDEX idx_doc_type ON documents(doc_type);
CREATE INDEX idx_status ON documents(status);
CREATE INDEX idx_ingestion ON documents(ingestion_date);
```

#### Database Operations
- Document registration
- Metadata updates
- Processing status tracking
- Error logging
- Basic querying interface

#### Scaling Considerations
- Migration to PostgreSQL
- Partitioning strategies
- Backup and replication
- Connection pooling

## System Operations

### 1. Document Registration
The Document Registration process handles new document ingestion, creating database records and managing file storage.

- Generate unique document ID
- Save raw file to appropriate directory
- Create database record with initial metadata
- Validate file integrity
- Log ingestion event

#### Scaling Considerations
- Batch registration support
- Distributed ID generation
- Enhanced validation rules

### 2. Document Retrieval
The Document Retrieval system provides access to both raw files and document metadata through a unified interface.

- Database metadata queries
- Raw file access
- Combined document information retrieval
- Basic caching

#### Scaling Considerations
- Enhanced caching
- Read replicas
- Content delivery optimization

### 3. Storage Management
The Storage Management system monitors and maintains both file storage and database health.

- Storage usage monitoring
- Database optimization
- Cleanup operations
- Health checking

#### Scaling Considerations
- Distributed storage management
- Advanced optimization strategies
- Automated maintenance

## MVP Scale Support
- Local filesystem storage
- SQLite database
- Single node operation
- Support for initial document set:
  * 25 Wikipedia articles
  * 1 textbook
  * 2 journal articles

## Error Handling and Recovery

### Error Handling
The Error Handling system manages failures in both file operations and database transactions.

- Transaction rollback support
- File operation atomicity
- Error categorization
- Recovery procedures

### Data Validation
The Data Validation system ensures data integrity across both storage systems.

- Schema validation
- File integrity checks
- Cross-reference validation
- Constraint enforcement

## Monitoring and Maintenance

### System Monitoring
The System Monitoring tracks key metrics for both storage systems.

- Storage usage metrics
- Database performance metrics
- Operation latency tracking
- Error rate monitoring

### Maintenance Operations
The Maintenance system performs regular upkeep tasks.

- Database vacuuming
- Index optimization
- Integrity checks
- Backup operations

#### Scaling Considerations
- Automated maintenance scheduling
- Performance optimization
- Enhanced monitoring
- Predictive maintenance