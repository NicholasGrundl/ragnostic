# Document Extraction Technical Specification

## Overview

### Purpose
This document specifies the document processing/extraction system implementation, which transforms raw documents (PDFs and web content) into extracted content with features (text, images, tables) and their associated metadata within the RAGnostic architecture.

### Scope
The system is responsible for:
- Extracting clean text content from documents
- Identifying and extracting document structure (sections, headers)
- Extracting and processing images and tables
- Generating captions for media content
- Storing processed content in structured database format
- Maintaining relationships between document elements

### System Context
- Input: Raw PDF documents and web content from Document Ingestion pipeline
- Output: Structured document content in SQLite database
- Dependencies: Document Ingestion system

## System Architecture

```mermaid
flowchart LR
    %% Input nodes
    pdf[PDF Files]
    web[Web Content]

    %% PDF Processing Flow
    subgraph pdf_flow[PDF Processing]
        direction TB
        doc_ext[Document Extraction]
        
        subgraph pdf_proc[Content Extraction]
            direction TB
            text_ext[Text Extraction]
            img_ext[Image Extraction] 
            tbl_ext[Table Extraction]
        end
        
        subgraph pdf_feature[Feature Processing]
            direction TB
            img_cap[Image Captioning]
            tbl_cap[Table Captioning]
            txt_clean[Text Cleaning]
        end
    end

    %% Web Processing Flow    
    subgraph web_flow[Web Processing]
        direction TB
        web_ext[Content Extraction]
        
        subgraph web_proc[Content Parsing]
            direction TB
            html_text[HTML Text]
            html_img[Images]
            html_tbl[Tables]
        end
        
        subgraph web_feature[Feature Processing]
            direction TB
            web_img_cap[Image Description]
            web_tbl_cap[Table Description]
            web_clean[Text Formatting]
        end
    end

    %% Storage
    subgraph store[Document Database]
        direction TB
        doc_sections[(Document Sections)]
        doc_images[(Document Images)]
        doc_tables[(Document Tables)]
    end

    %% PDF Flow Connections
    pdf --> doc_ext
    doc_ext --> text_ext & img_ext & tbl_ext
    text_ext --> txt_clean
    img_ext --> img_cap
    tbl_ext --> tbl_cap

    %% Web Flow Connections
    web --> web_ext
    web_ext --> html_text & html_img & html_tbl
    html_text --> web_clean
    html_img --> web_img_cap
    html_tbl --> web_tbl_cap

    %% Storage Connections
    txt_clean & web_clean --> doc_sections
    img_cap & web_img_cap --> doc_images
    tbl_cap & web_tbl_cap --> doc_tables

    classDef input fill:#e1f5fe,stroke:#333,color:#000
    classDef process fill:#f3e5f5,stroke:#333,color:#000
    classDef feature fill:#fff3e0,stroke:#333,color:#000
    classDef storage fill:#dcedc8,stroke:#333,color:#000
    
    class pdf,web input
    class doc_ext,web_ext,text_ext,img_ext,tbl_ext,html_text,html_img,html_tbl process
    class img_cap,tbl_cap,txt_clean,web_img_cap,web_tbl_cap,web_clean feature
    class doc_sections,doc_images,doc_tables storage
```

## 1. PDF Processing Pipeline
### 1.1 Document Extraction
- Input: Raw PDF file
- Primary tools: `docling` and `marker-pdf`
- Process:
  * Load PDF document
  * Extract document structure
  * Identify sections and headers
  * Track page numbers and positions
- Output: Initial document structure with section markers

### 1.2 Content Extraction
- Text Extraction:
  * Clean text content
  * Header identification
  * Section boundary detection
  * Page tracking
- Image Extraction:
  * Image location identification
  * Image data extraction
  * Format standardization
  * Reference tracking
- Table Extraction:
  * Table boundary detection
  * Structure preservation
  * Cell content extraction
  * Position tracking

### 1.3 Feature Processing
- Text Cleaning:
  * Format standardization
  * Special character handling
  * Section relationship mapping
  * Content validation
- Image Captioning:
  * Context assembly
  * Caption generation
  * Quality validation
- Table Captioning:
  * Structure analysis
  * Content summarization
  * Context integration

## 2. Web Content Pipeline
### 2.1 Content Extraction
- Input: Web article URL or content
- Primary tools: `wikipedia` and `wikipedia-api`
- Process:
  * Content retrieval
  * Structure parsing
  * Media reference extraction

### 2.2 Content Parsing
- HTML Text:
  * Clean text extraction
  * Structure preservation
  * Link handling
- Image Processing:
  * Reference extraction
  * Metadata collection
  * Source tracking
- Table Processing:
  * Structure extraction
  * Format preservation
  * Cell content parsing

### 2.3 Feature Processing
- Text Formatting:
  * Style normalization
  * Section organization
  * Reference tracking
- Image Description:
  * Context integration
  * Description generation
  * Reference mapping
- Table Description:
  * Structure analysis
  * Content summarization
  * Context integration

## 3. Storage System
### 3.1 Database Schema

**Datamodel Schema**
```sql
-- Document's physical section structure
CREATE TABLE document_sections (
    section_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    parent_section_id TEXT,
    level INTEGER NOT NULL,                 -- Header level (1=H1, etc)
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    sequence_order INTEGER NOT NULL,        -- Order in document
    page_start INTEGER,
    page_end INTEGER,
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    FOREIGN KEY (parent_section_id) REFERENCES document_sections(section_id)
);

-- Document images
CREATE TABLE document_images (
    id INTEGER PRIMARY KEY,
    doc_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    image_data TEXT NOT NULL,               -- Base64 encoded
    caption TEXT,                           -- Extracted or generated caption
    embedding_id TEXT,                      -- Vector store reference
    page_number INTEGER NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    FOREIGN KEY (section_id) REFERENCES document_sections(section_id)
);

-- Document tables
CREATE TABLE document_tables (
    id INTEGER PRIMARY KEY,
    doc_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    caption TEXT,
    table_data TEXT NOT NULL,               -- JSON structured data
    page_number INTEGER NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    FOREIGN KEY (section_id) REFERENCES document_sections(section_id)
);
```

**ER Diagram**
```mermaid
erDiagram
    Document ||--o{ DocumentSection : contains
    DocumentSection ||--o{ DocumentSection : "parent of"
    DocumentSection ||--o{ DocumentImage : contains
    DocumentSection ||--o{ DocumentTable : contains

    Document {
        string id PK
    }

    DocumentSection {
        string section_id PK
        string doc_id FK
        string parent_section_id FK
        integer level
        string title
        text content
        integer sequence_order
        integer page_start
        integer page_end
    }

    DocumentImage {
        integer id PK
        string doc_id FK
        string section_id FK
        text image_data
        string caption
        string embedding_id
        integer page_number
    }

    DocumentTable {
        integer id PK
        string doc_id FK
        string section_id FK
        string caption
        json table_data
        integer page_number
    }
```
  
### 3.2 Storage Operations
- Section Storage:
  * Hierarchical relationship maintenance
  * Order preservation
  * Content integrity checks
- Image Storage:
  * Binary data handling
  * Caption association
  * Section mapping
- Table Storage:
  * Structure preservation
  * JSON serialization
  * Context tracking

## 4. Error Handling
### 4.1 Processing Errors
- Document parsing failures
- Image extraction errors
- Table structure issues
- Caption generation failures

### 4.2 Storage Errors
- Database constraints
- Data integrity issues
- Relationship violations

### 4.3 Recovery Strategy
- Partial content preservation
- Error logging
- Processing continuation
- Cleanup procedures

## 5. Monitoring and Metrics
### 5.1 Processing Metrics
- Document processing time
- Feature extraction success rates
- Caption generation quality
- Error rates by type

### 5.2 Storage Metrics
- Database size
- Query performance
- Relationship integrity
- Storage efficiency

## 6. Future Considerations
- Additional document format support
- Enhanced caption generation
- Improved table structure detection
- Advanced error recovery
- Performance optimization
- Cloud storage integration






# ----- WORKING -----
## Document Database Diagram

```mermaid
erDiagram
    Document ||--|| DocumentMetadata : has
    Document ||--o{ DocumentSection : contains
    Document ||--o{ DocumentImage : has
    Document ||--o{ DocumentTable : has
    DocumentSection ||--|| SectionContent : has
    DocumentSection ||--o{ DocumentSection : "parent of"
    DocumentSection ||--o{ DocumentImage : contains
    DocumentSection ||--o{ DocumentTable : contains

    Document {
        string id PK
        string raw_file_path
        string file_hash
        integer file_size_bytes
        datetime ingestion_date
        integer total_sections
        integer total_images
        integer total_tables
        integer total_pages
    }

    DocumentMetadata {
        string doc_id PK, FK
        string title
        json authors
        string language
        datetime creation_date
    }

    DocumentSection {
        string section_id PK
        string doc_id FK
        string parent_section_id FK
        integer level
        integer sequence_order
        integer word_count
        integer image_count
        integer table_count
    }

    SectionContent {
        string section_id PK, FK
        string title
        text content
        integer page_start
        integer page_end
    }

    DocumentImage {
        integer id PK
        string doc_id FK
        string section_id FK
        integer page_number
        text image_data
        text caption
    }

    DocumentTable {
        integer id PK
        string doc_id FK
        string section_id FK
        integer page_number
        json table_data
        text caption
    }
```    