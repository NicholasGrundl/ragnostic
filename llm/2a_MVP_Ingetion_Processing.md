# Document Ingestion and Processing Implementation Plan (MVP)

## Overview
This document outlines the minimal viable implementation plan for document processing, focusing on basic ingestion, storage, and initial metadata capture without complex processing pipelines.

## System Architecture

### Processing Stages

```mermaid
flowchart LR
    A[Document Monitor] --> B[Duplicate Check]
    B --> C[Raw Storage]
    C --> D[Document Library DB]
    D --> E[Basic Processing]
```

## 1. Document Monitor

### File Monitor Service
- Implements Python watchdog for directory monitoring
- Supports PDF files initially
- Basic validation:
  * File exists and is readable
  * Valid PDF format
  * File size check

### Duplicate Detection
- Calculate file hash (SHA-256)
- Check against existing document hashes in database
- Skip ingestion if duplicate found

## 2. Raw Storage System

### File Organization
```
/raw_documents/
└── {doc_id}.pdf
```

### Storage Operations
- Move file to raw storage with new doc_id-based filename
- Basic file system operations only
- No complex processing at this stage

## 3. Document Library Database

### Database Schema

```sql
-- Core document tracking
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    raw_file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    ingestion_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Basic metadata extracted during ingestion
CREATE TABLE document_metadata (
    doc_id TEXT PRIMARY KEY,
    title TEXT,
    authors TEXT, -- JSON array
    creation_date DATETIME,
    modification_date DATETIME,
    page_count INTEGER,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

-- Document images
CREATE TABLE document_images (
    id INTEGER PRIMARY KEY,
    doc_id TEXT NOT NULL,
    name TEXT NOT NULL,
    base64_data TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    description TEXT, -- text description of image
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    UNIQUE(doc_id, name)
);

-- Simple processing outputs
CREATE TABLE document_content (
    doc_id TEXT PRIMARY KEY,
    extracted_text TEXT,
    processed_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);
```

## 4. Basic Processing

### Initial Processing
1. Extract basic text content
    - docling 
    - markerpdf
    - placeholder for images and tables in text
    - store tables as images as well
2. Identify and save any images
    - send to llm for captioning?


## Error Handling

### Basic Error Types
1. File System Errors:
   - File not found
   - Permission denied
   - Storage full

2. Processing Errors:
   - Invalid file format
   - Extraction failure

### Error Response
- Log error details
- Skip problematic documents
- Continue processing others

## Monitoring

### Basic Metrics
- Number of documents ingested
- Storage usage
- Basic error counts
- Processing success/failure rates
