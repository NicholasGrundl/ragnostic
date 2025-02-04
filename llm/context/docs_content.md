<file_1>
<path>0a_README.md</path>
<content>
```markdown
# Background

This repo is to explore and implement RAG for consulting and technical applications that use heavy PDFs.

# MVP 1:

We will be focusing on an initial MVP to pipe asll the parts of the RAG system together for demoing and exploration as we build.

The main blocks are:

1. Raw document ingestion and storage
2. Document text extraction and labeling
3. Chunking and embedding in vector store
4. Query retrival
5. Evaluations

## Raw Document ingestion and storage

- collect and assemble raw documents to work with
- collect and assemble wikipedia articles to work with
- store documents in a database as blobs

## Document text extraction and labeling

- test various PDF readers and text extraction
- test wikipedia text semantics
- data model objects for documents with metadata
- document summarization for heirarchal RAG and text search
- document labeling based on summaries and metadata classification?


# Resources

We plan to look into the following for PDF reading and extraction:

OpenSource:
- PyMuPDF4LLM: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/
- zerox: https://github.com/getomni-ai/zerox
- marker: https://github.com/VikParuchuri/marker
- docling: https://github.com/DS4SD/docling
- llmsherpa: https://github.com/nlmatics/llmsherpa

ClosedSource:
- llamaparse: https://github.com/run-llama/llama_parse
- unstructured: https://github.com/Unstructured-IO/unstructured
- llmwhisperer: https://github.com/Zipstack/unstract
- google document AI: https://cloud.google.com/python/docs/reference/documentai/latest

We plan to also use the internet for gap filling:

DataSources:
- wikipedia-api (more granular and updated): https://github.com/martin-majlis/Wikipedia-API
- wikipedia (higher level and stale): https://github.com/goldsmith/Wikipedia

Search:
- BraveAPI: https://api.search.brave.com/app/documentation/web-search/get-started
- BraveAPI python client (sync and async, stable): https://github.com/kayvane1/brave-api
- Brave python client alternative(async and uv/docker images): https://github.com/helmut-hoffer-von-ankershoffen/brave-search-python-client


# Installation of packages

## Python version
We require >=3.11

## Installation

The packages are a bit finnicky and some non python packages are required. Due to the pytorch requirement thigns are VERY paltform specific...
- CPU
- GPU
- OS

## MacOS Intel

> Due to pytorch versions being old on intel macOS i didnt get the marker pdf to run. Ill try it again on my WSL beast and see what happends.

1. poppler: image analysis
    - `brew install poppler`

2. Pytorch: CPU or GPU depending on machine
    - `uv add torch torchvision`
    > You may need to install an explicit CPU version, in that case:
    > `uv pip install --index-url https://download.pytorch.org/whl/cpu torch==2.1.0 torchvision==0.16.0`

3. PDF extraction packages
    - `uv add pymupdf4llm`
    - `uv add py-zerox`
    > marker-pdf is an early unstable version on mac intel
    > docling for intel mac with pinned pytorch is incompatible

4. Web search and wikipedia
   - `uv add brave-search`
   - `uv add wikipedia wikipedia-api`

5. Workflows and DAGs
   - `uv add burr[start]`

6. Indexing
   - `uv add llama_index`

## Ubuntu Intel + GPU

We are going to go the more stable and classic route of conda and pip

1. Setup a new miniconda env

2. Install the OS specific packages (mostly OCR)
    a. poppler: image analysis
    - `conda install -c conda-forge poppler`
    b. Tesseract
    - `conda install -c conda-forge tesseract`
    c. graphviz
    - `conda install graphviz`

3. Install CUDA (if GPU enabled)
    a. Install CUDA on WSL
    - https://docs.nvidia.com/cuda/wsl-user-guide/index.html#getting-started-with-cuda-on-wsl-2
    b. Add to `.bashrc`
    ```export PATH=/usr/local/cuda-12.8/bin${PATH:+:${PATH}}
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
    ```

4. Pytorch: CPU or GPU depending on machine
    - see: https://pytorch.org/get-started/locally/
    - in the conda env: `pip install torch torchvision torchaudio`
    - verify the installation
        ```
        import torch
        x = torch.rand(5, 3)
        print(x)
        torch.cuda.is_available()
        ```
        
5. Install packages and dev packages
    a. Use the Makefile routine
    - `make install`
    b. Alternatively use the requiremetns files
    - `requirements.txt`
    - `requirements-dev.txt`


## Envrionment Vars

1. NVIDIA/CUDA/Torch related
    a. specify GPU architecture
    - check with: ``
    - for TheBeast: `export TORCH_CUDA_ARCH_LIST="8.6"`
```
</content>
</file_1>

<file_2>
<path>0b_ACTIONITEMS.md</path>
<content>
```markdown
# Action Items

- change libmagic (python-magic) dependency which is OS level and varied by OS
- consider filetype library stdlib or extensions

## Ingestion flow

Completed the basic ingestion flow and it runs in jupyter.  Whats missing is the following:
- cleanup of ingestion upon success
- possible adding the original filename as a file field on indexing (i.e. change name when indexed with doc_id) and a suffic to the docis for human use
  - can rename files later when we summarize...
- add some logging across the module and custom log setup
- integration test for ingestion flow

Database client
- the client needs some improvement and is tied to business logic currently
- id like the base cvlient to be a CRUD (get, set, update, delete) API caller to the database, we can use this in the API as well
- id like a indexing specific set of functions or database wrapper that have the dusiness logic

Document search and retrieval client
- id like a basic query client or call that runs on a simple keyword search or allows interfacing with the database in code
- basically search the document titles (original title) so humans can use it lightly as a library

## Semantic extraction flow

- just make functions without tests for demo
- run docling and update the database with text, images, tables
- combine all images with descriptions and insert in text at docling location
- assume document level sections and chunk using basic params (overlap and length)

## Query flow
- run standard query using vectors and chunks


# Action Items DevOps:

## CI/CD

- setup linting and formatting make commands
- setup a build command on merge to main (check github actions?)

## Testing

- setup test commands with parameterize.mark tags
- unittest or fast tests tag
- slow tests/ integration tests
- setup make commands for testing
```
</content>
</file_2>

<file_3>
<path>1_System_Requirements.md</path>
<content>
```markdown
# Hierarchical RAG System Requirements

## System Overview & Data Sources
- Wikipedia articles (Initial: 25, Target: 10,000)
- PDF documents
  * Initial: 1 textbook (200 pages), 2 journal articles
  * Target: 20-50 textbooks, thousands of journal articles

## Technical Requirements

### Document Processing & Storage
- Parse Wikipedia articles via API
- Process PDFs using Doculing
- Raw document storage with consistent structure
  * Separate dirs by document type
  * Consistent naming convention
  * Atomic operations
  * Duplicate handling
  * Backup system with periodic snapshots
- Generate and track document metadata
  * Title and author extraction
  * Date and source tracking
  * Parent-child relationships
  * Position tracking
- Create hierarchical summaries and chunks
  * Extractive summarization
  * Configurable length control
  * Semantic boundaries
  * Context preservation
- Compute embeddings at multiple levels
  * Model selection
  * Batch processing

### Vector Database Integration
- ChromaDB or LanceDB implementation
- Collection structure
  * Separate collections per level
  * Metadata schema
- Vector storage operations
  * Batch insertion
  * Update handling
  * Index maintenance
  * Health checks

### Query Pipeline
1. Document summary search via embeddings
2. Filtered chunk search within matched documents
3. Basic reranking system
   * Grouping logic
   * Score combination
   * Result formatting
   * Metadata inclusion
   * Context assembly

### Performance Requirements
- Query response time: Up to 30 seconds acceptable
- Infrequent document updates (daily at most)
- Local deployment initially, cloud migration planned

### Evaluation System
- Accuracy and precision metrics
- Parameter tuning capability
- System performance tracking

## Implementation Pipeline
1. Ingest from monitored directory
   * watchdog for directory monitoring
   * file type detection
2. Parse and extract content
3. Generate metadata
4. Create hierarchical structures
5. Compute embeddings
6. Store in vector database

## Future Considerations
- Cloud deployment
- API service development
- Enhanced reranking system
- Evaluation metrics implementation
- Parameter optimization
```
</content>
</file_3>

<file_4>
<path>2_Ragnostic_Project_Plan.md</path>
<content>
```markdown
# Ragnostic Project Plan 

RAGnostic is a general system to implement heirarchal document retrieval. 

## Overview
More narrowly for the proof of concept we will make a system that searches document summaries first to filter the document list, then performs vector search on smaller chunks within filtered documents. The system consists of four main processing stages:

1. Document Ingestion: Handles raw document intake and validation
2. Content Extraction: Processes documents to extract text, images, and tables
3. Semantic Processing: Creates searchable chunks and embeddings
4. Vector Storage: Manages document and chunk embeddings for search


```mermaid
flowchart LR
    subgraph Document Flow
        direction LR
        A[Document Ingestion] --> B[Document Processing]
        B --> C[Semantic Extraction]
        C --> D[Vector Storage]
    end
    
    subgraph Query Flow
        direction LR
        E[User Query] --> F[Query Embedding]
        F --> G[Document Search]
        G --> H[Section/Chunk Relevance]
        H --> I[Reranking]
    end

    %% Styling
    classDef docflow fill:#deeeff,color:#0f1440
    classDef queryflow fill:#fff0e6,color:#0f1440
    
    class A,B,C,D docflow
    class E,F,G,H,I queryflow
```

## MVP Scope
### Data Sources
- Wikipedia articles
- PDF documents (textbooks, journal articles)

### Initial Scale
- 25 Wikipedia articles
- 1 textbook (200 pages)
- 2 journal articles

### Target Scale
- 10,000 Wikipedia articles
- 20-50 textbooks
- Thousands of journal articles


## 1. Document Flow Components

The document flow covers the complete pipeline from raw document intake through searchable content creation.

```mermaid
flowchart LR
    subgraph Document Flow
        direction LR
        A[Document Ingestion] --> B[Content Extraction]
        B --> C[Semantic Processing]
        C --> D[Vector Storage]
        
        %% Add error handling paths
        A --> E[Error Handler]
        B --> E
        C --> E
        D --> E
        
        %% Add database interactions
        A --> DB[(Document DB)]
        B --> DB
        C --> DB
        C --> VS[(Vector DB)]
        D --> VS
    end

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,color:#0f1440
    classDef storage fill:#deeeff,stroke:#333,color:#0f1440
    classDef error fill:#ffecec,stroke:#333,color:#0f1440
    
    class A,B,C,D default
    class DB,VS storage
    class E error
```


```mermaid
sequenceDiagram
    participant I as Ingestion
    participant DB as Document DB
    participant E as Content Extraction
    participant S as Semantic Proc
    participant V as Vector Storage
    participant VS as Vector DB
    participant ER as Error Handler

    %% Document Processing Phase
    I->>DB: Create document entry
    activate I
    I->>DB: Store raw file path & metadata
    I-->>ER: Report ingestion errors
    I->>E: Process document
    deactivate I
    
    activate E
    E->>DB: Store document sections
    E->>DB: Store images & tables
    E-->>ER: Report extraction errors
    deactivate E
    
    activate S
    S->>DB: Store semantic groups
    S->>DB: Link sections to groups
    S-->>ER: Report semantic errors
    deactivate S

    %% Vector Processing Phase
    V->>DB: Read semantic groups
    activate V
    V->>VS: Store group embeddings
    V->>DB: Read document chunks
    V->>VS: Store chunk embeddings
    V-->>ER: Report storage errors
    deactivate V
```

### Document Ingestion

The document ingestion system serves as the primary entry point for all content entering the hierarchical RAG system. It provides a pipeline for adding new documents (i.e. Wikipedia articles and PDF documents) to the available set of documents in the library. It also manages the library storage system which consists of a flat filesystem structure for raw document/blob storage and a SQLite database for document management and metadata.

Key responsibilities:
- Document validation and deduplication
- Raw document storage management
- Document ID and metadata management
- Basic content extraction for initial processing
- SQLite database management for document tracking


### Content Extraction

The content extraction system processes raw documents into structured content. It provides methods for parsing, labeling, and understanding the content of documents. 

Key responsibilities:
- Text extraction and cleaning
- Image and table identification/extraction
- Image and table caption generation
- Content relationship mapping
- Content storage in structured database format

### Semantic Processing

The semantic processing system prepares content for efficient search. We makes sense of the extracted content for each document organizing around logical section groupings as opposed to document level. Whole semantic group summaries are obtained are added to the document database to help with reranking later on. We also create our individual chunks and assign them relevant Chunk IDs to use later on. Each individual chunk maintains relationships to its higher level section and document(s)

 Key responsibilities:
- Section and chunk boundary detection
- Summary generation at multiple levels
- Semantic group creation and management
- Embedding generation for all content types

### Vector Storage

The vector storage system implements a hierarchical search architecture using ChromaDB. It maintains separate collections for semantic group summaries and chunks, optimizing search performance while preserving relationships. The system provides clean interfaces for updates and searches while ensuring data consistency across collections. The search strategies enabled are a document relvance search, and a filtered chunk relevance search.

Key responsibilities:
- Separate collections for summaries and chunks
- Metadata management for filtering
- Collection consistency maintenance
- Search optimization management
- Relationship preservation across collections

## Database Architecture

The system uses a combination of SQLite and ChromaDB for data management:

### Document Database (SQLite)
Manages four key areas:
- Document Management: Core document tracking and metadata
- Content Storage: Sections, images, and tables
- Semantic Groups: Section groupings and relationships
- Processing Status: Pipeline stage tracking

### Vector Database (ChromaDB)
Maintains two primary collections:
- Semantic Summaries: Document and section-level embeddings
- Semantic Chunks: Fine-grained content embeddings

## System Monitoring and Error Handling

### Error Management
Each pipeline stage implements specific error handling:
- Ingestion: File system and validation errors
- Extraction: Processing and parsing errors
- Semantic: Generation and embedding errors
- Storage: Database and vector store errors

### System Monitoring
Key metrics tracked across stages:
- Processing performance and throughput
- Error rates and types
- Storage utilization and performance
- Search quality and response times

## Document Support

### Supported Document Types
- PDF Documents
  * Academic papers and articles
  * Textbooks and manuals
  * Technical documentation
- Web Content
  * Wikipedia articles
  * HTML documents
  * Structured web pages

### Processing Requirements
Each document type has specific processing needs:
- PDFs: Structure extraction, image/table processing
- Web Content: HTML parsing, media extraction
- Common: Text cleaning, semantic analysis


## 2. Query Flow

The Query flow covers the search based on a user query, along with the reranking and context organization.

```mermaid
flowchart LR
    subgraph Query Flow
        direction LR
        E[User Query] --> F[Query Processing]
        F --> G[Document Search]
        G --> H[Section/Chunk Search]
        H --> I[Chunk Reranking]
    end

    %% Styling
    classDef queryflow fill:#fff0e6,color:#0f1440
    
    class E,F,G,H,I queryflow
```

### Query Processing

The query processing takes a new user query and creates an embedding of it for use in search. Additional query processing may also include query classification/labeling, keyword extraction, query rewriting.

### Document Search

The document search step takes the processed query which contains an embedding and optioonally keywords/labels to help search. The processed query is used to find relevant documents based on the document summary collection. The output of the document search is a list of Doc IDs and their associated search score. The top N Doc IDs are used in subsequent stages

### Section/Chunk Search

The section/chunk search filters the chunk collection based on the Doc IDs then performs a search using the processed query. The output of the section/chunk search is a list of Chunk IDs and their associated search score. This list is used in the reranking stage to determine the best document chunks and context.

### Chunk Reranking

The reranking approach here is based on chunk groups. We rerank based on the largest "contiguous group" and higherst score. Conceptually we want to find sections that have multiple chunks within them of relevancy indicating the section is important. We will use "section chunk coverage" as a metric which is computed as (chunks returned from section)/(total chunks in section).


### Query Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant QP as Query Processor
    participant DS as Document Search
    participant VS as Vector Storage
    participant CS as Chunk Search
    participant RR as Reranker

    User->>QP: Submit query
    QP->>QP: Generate query embedding
    QP->>DS: Search document summaries
    DS->>VS: Get relevant documents
    VS->>DS: Return document matches
    DS->>CS: Filter by matched Doc IDs
    CS->>VS: Search filtered chunks
    VS->>CS: Return chunk matches
    CS->>RR: Chunks for reranking
    RR->>RR: Group by sections
    RR->>User: Return ranked results
```


```
</content>
</file_4>

<file_5>
<path>2a_Document_Ingestion.md</path>
<content>
```markdown
# Document Ingestion Technical Specification

## Overview

### Purpose
This document outlines the document ingestion implementation, which takes new documents and adds them to our database along with text and document information extraction. Ingestion incudes raw blob, metadata, and extracted information storage.

### Scope
The system is responsible for:
- Monitoring ingestion folder for new documents
- Assessing validity of ingestion documents (i.e. no duplicates)
- Assigning doc ids and moving new documents into our document database
- extracting and storing document file metadata (size, etc.)
- running feature extraction on documents (text, images, tables, etc)

### System Context
- Input: New PDF document or wikipedia url
- Output: document database entry, raw file blob
- Dependencies: 

## System Architecture

### Processing Stages

```mermaid
flowchart LR
    subgraph Monitor[Document Monitor]
        direction TB
        F[File Watcher] --> V[Basic Validation]
    end
    
    subgraph Validate[Document Validation]
        direction TB
        H[Hash Check] --> M[Mime Check]
        M --> S[Size Check]
    end
    
    subgraph Raw[Raw Processing]
        direction TB
        ID[Doc ID Service] --> RS[Raw Storage]
    end
    
    subgraph Index[Document Indexing]
        direction TB
        DB[Document DB] --> MC[Metadata Client]
        MC --> BC[Basic Content]
    end
    
    subgraph Status[Status Tracking]
        direction TB
        S1[Ingested] --> S2[Queued]
    end
    
    Monitor --> Validate
    Validate --> Raw
    Raw --> Index
    Index <--> Status

    %% Styling
    classDef monitor fill:#e1f5fe,stroke:#333,color:#000
    classDef validate fill:#fff3e0,stroke:#333,color:#000
    classDef raw fill:#f3e5f5,stroke:#333,color:#000
    classDef index fill:#e8f5e9,stroke:#333,color:#000
    classDef status fill:#fce4ec,stroke:#333,color:#000
    
    class F,V monitor
    class H,M,S validate
    class ID,RS raw
    class DB,MC,BC index
    class S1,S2 status
```    

## 1. Document Monitor
### 1.1 File Monitor Service
- Implements Python watchdog for directory monitoring
- Supports PDF files initially
- Basic validation:
  * File exists and is readable
  * Valid PDF format

## 2. Document Validation
### 2.1 Duplicate Checks
- Calculate file hash (SHA-256)
- Check against existing document hashes in database
- Skip ingestion if duplicate found

### 2.2 Validation Checks
- mime type
- file size limits
- not corrupted



## 3. Raw Processing
### 3.1 Document id service
Issues new document ids for valid documents
- Move file to raw storage with new doc_id-based filename
- Basic file system operations only
- No complex processing at this stage
- updates document database

### 3.2 File Organization
Raw document blobs are stored in a flat filesystem
- will initially store locally
- easy switch to S3 like storage (i.e. cloud)

```
/raw_documents/
└── {doc_id}.pdf
```

## 4. Document Indexing

### 3.1 Document Database Core Schema
For the indexing process and raw file storage we maintain the mapping from raw file to database entry
-  metadata allows for search and retrieval

**Document Core Schema**
```sql
------------------------------------------------------------------
-- Core Document Management
------------------------------------------------------------------

-- Primary document tracking
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    raw_file_path TEXT NOT NULL,            -- Path to original file
    file_hash TEXT NOT NULL,                -- For deduplication
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    ingestion_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Basic document metadata
CREATE TABLE document_metadata (
    doc_id TEXT PRIMARY KEY,
    title TEXT,
    authors TEXT,                           -- JSON array
    description TEXT,
    creation_date DATETIME,
    page_count INTEGER,
    language TEXT,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);
```

**Document ER Diagram**
```mermaid
erDiagram
    Document ||--|| DocumentMetadata : has
    Document ||--|| ProcessingStatus : tracks

    Document {
        string id PK
        string raw_file_path
        string file_hash
        integer file_size_bytes
        string mime_type
        datetime ingestion_date
    }

    DocumentMetadata {
        string doc_id PK, FK
        string title
        json authors
        string description
        datetime creation_date
        integer page_count
        string language
    }

    ProcessingStatus {
        string doc_id PK, FK
        string status
        string error_message
        datetime last_updated
    }
```

### 3.2 Document database python client
- client for accessing database in python
- document CRUD
- document search (fuzzy text search on description and/or title?)
- faceted filter on date ingested, etc.


### 3.3 Basic Document processing

Initial document extaraction is handled by the `pymupdf4llm` package. It pulls easily available raw text and metadata WIHTOUT complex dependencies. The primary role is:
- Store the raw document for processing
- Create initial document metadata entry
- Initial content for basic or fuzzy search (keyword/queries)
- Utilize minimal LLM or heavy pytorch code (can install as a small subset of package and use in many systems)
- Is fast and failure proof



## Error Handling
### Ingestion Error Types
1. File System Errors:
   - File not found
   - Permission denied
   - Storage full
   - Invalid file permissions

2. Validation Errors:
   - Invalid file format
   - File too large
   - Duplicate document
   - Corrupted file

3. Database Errors:
   - Metadata insertion failure
   - Status tracking failure
   - Document record creation failure

Note: Document processing and extraction errors are handled by the Document Extraction system (see Document_Extraction.md)


```
</content>
</file_5>

<file_6>
<path>2b.1_DocumentExtraction_ContentExtraction_Design.md</path>
<content>
```markdown
# Document Extraction System Design

## Overview

The document extraction system processes PDFs to extract text, images, and structural information. It uses a pluggable architecture to support multiple extraction backends while focusing initially on docling.

### Document Extraction Flow

```mermaid
sequenceDiagram
    participant Client
    participant Manager as ExtractionManager
    participant Extractor as DoclingExtractor
    participant DB as DatabaseClient
    participant FS as FileSystem

    Client->>Manager: process_document(doc_id)
    Manager->>DB: get_document(doc_id)
    Manager->>Extractor: extract_document(file_path)
    Extractor-->>Manager: ExtractionResult
    
    Manager->>Manager: _store_sections(sections)
    
    loop For each image
        Manager->>Manager: check_size(image)
        alt image size <= limit
            Manager->>DB: store_image_data(base64)
        else image size > limit
            Manager->>FS: save_image_file()
            Manager->>DB: store_image_path()
        end
    end
    
    Manager-->>Client: ExtractionResult
```

### Implementation Notes

1. **Error Handling**
   - Each component includes detailed error messages
   - Failures in one section don't stop entire process
   - All errors logged and included in result

2. **Image Storage Strategy**
   - Images under size_limit stored as base64 in database
   - Larger images saved to filesystem
   - All metadata stored in database regardless of storage location

3. **Section Confidence**
   - Low default confidence for auto-detected sections
   - Allows for manual verification or semantic processing
   - Sections can be merged/split in semantic stage

4. **Future Considerations**
   - Easy to add new extractors
   - Storage strategy can be modified
   - Caption generation can be added
   - Section detection can be enhanced

## Core Components

### 1. Base Interfaces

#### 1.1 Extraction Results
```python
from typing import Protocol, List, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

class ExtractedImage(BaseModel):
    """Represents an extracted image with metadata"""
    image_data: bytes
    format: str
    size_bytes: int
    page_number: int
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2 coordinates
    confidence: float = 1.0

class ExtractedSection(BaseModel):
    """Represents a detected document section"""
    title: str
    content: str
    level: int
    page_start: int
    page_end: int
    confidence: float = 0.0  # Default low confidence for sections

class ExtractionResult(BaseModel):
    """Contains all extracted content from a document"""
    doc_id: str
    sections: List[ExtractedSection]
    images: List[ExtractedImage]
    extraction_date: datetime
    extractor_name: str
    error_messages: List[str] = []
```

#### 1.2 Error Handling Models
```python
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class ExtractionErrorType(Enum):
    PARSER_ERROR = "parser_error"
    IMAGE_EXTRACTION_ERROR = "image_extraction"
    SECTION_ERROR = "section_error"
    STORAGE_ERROR = "storage_error"

class ExtractionError(BaseModel):
    error_type: ExtractionErrorType
    message: str
    section_id: Optional[str] = None
    page_number: Optional[int] = None
    recoverable: bool = True
```


### 2. Document Extraction Interface

#### 2.1 Pluggable Extraction

```python
class DocumentExtractor(Protocol):
    """Base protocol for document extractors"""
    name: str
    
    def extract_document(self, file_path: Path) -> ExtractionResult:
        """Extract content from document"""
        ...
```

#### 2.2 Docling Implementation

```python
class DoclingExtractor:
    """Docling-based document extractor"""
    name: str = "docling"
    
    def extract_document(self, file_path: Path) -> ExtractionResult:
        # Implementation will be added later when we have docling context
        ...
```

### 3. Extraction Workflow

#### 3.1 Extraction Manager

Triggers and runs the extraction

```python
class ExtractionManager:
    """Manages document extraction process"""
    def __init__(self, 
                 db_client: DatabaseClient,
                 extractor: DocumentExtractor,
                 image_size_limit: int = 1_000_000):  # 1MB default
        self.db_client = db_client
        self.extractor = extractor
        self.image_size_limit = image_size_limit
    
    def process_document(self, doc_id: str) -> ExtractionResult:
        """Process a single document"""
        ...
    
    def _store_sections(self, doc_id: str, sections: List[ExtractedSection]) -> None:
        """Store extracted sections in database"""
        ...
    
    def _store_images(self, doc_id: str, images: List[ExtractedImage]) -> None:
        """Store extracted images in database or filesystem"""
        ...
```
#### 3.2 Extraction Progress Tracking

Logger for the process

```python
from contextlib import contextmanager
from time import time
from typing import Iterator

class ExtractionProgress:
    def __init__(self, total_pages: int):
        self.total_pages = total_pages
        self.current_page = 0
        self.start_time = time()
        self.section_count = 0
        self.image_count = 0
        
    @property
    def progress(self) -> float:
        return self.current_page / self.total_pages
        
    @property
    def elapsed_time(self) -> float:
        return time() - self.start_time

    def update(self, page: int, sections: int = 0, images: int = 0):
        self.current_page = page
        self.section_count += sections
        self.image_count += images
        
        # Log progress every 10% or every 5 minutes
        if self.progress % 0.1 < 0.01 or self.elapsed_time % 300 < 1:
            logging.info(
                f"Progress: {self.progress:.1%} | "
                f"Page {self.current_page}/{self.total_pages} | "
                f"Found {self.section_count} sections, {self.image_count} images | "
                f"Time: {self.elapsed_time:.1f}s"
            )

@contextmanager
def track_extraction(doc_id: str, total_pages=100) -> Iterator[ExtractionProgress]:
    tracker = ExtractionProgress(total_pages=total_pages)  # Get from doc metadata
    try:
        yield tracker
    finally:
        logging.info(f"Extraction complete for {doc_id}")
        logging.info(f"Total time: {tracker.elapsed_time:.1f}s")
        logging.info(f"Found: {tracker.section_count} sections, {tracker.image_count} images")
```


### 4. Database Updates

#### 4.1 Modified Image Table Schema

We want to add a confidence score to the database for sections

```sql
CREATE TABLE document_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    image_data TEXT NOT NULL,           -- Base64 encoded if small
    file_path TEXT,                     -- Path if stored on filesystem
    caption TEXT,
    image_format TEXT NOT NULL,         -- e.g., 'png', 'jpg'
    image_size INTEGER NOT NULL,        -- Size in bytes
    bbox TEXT NOT NULL,                 -- JSON encoded coordinates
    confidence FLOAT NOT NULL DEFAULT 1.0,
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    FOREIGN KEY (section_id) REFERENCES document_sections(section_id)
);
```

#### 4.2 Section Schema confidence

Modified Section Schema

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
    extraction_confidence FLOAT NOT NULL DEFAULT 0.0;
    extraction_method TEXT;  -- Store which extractor found this section
    FOREIGN KEY (doc_id) REFERENCES documents(id),
    FOREIGN KEY (parent_section_id) REFERENCES document_sections(section_id)
)
```

We can use confidence to help with subsequent semantic analysis. The system uses a 0.0-1.0 confidence scale for sections:

1. **Low Confidence (0.0-0.3)**
   - Basic header matching only
   - Potential false positives
   - Requires semantic verification
   - Example: Text size changes or basic formatting hints

2. **Medium Confidence (0.3-0.7)**
   - Clear header markers found
   - Logical structure present
   - May need refinement
   - Example: Consistent formatting with numbering

3. **High Confidence (0.7-1.0)**
   - Strong structural indicators
   - Clear hierarchical markers
   - PDF bookmarks present
   - Example: Document outline or ToC matches

Usage in semantic processing:

```python
def process_sections(sections: List[DocumentSection]):
    for section in sections:
        if section.extraction_confidence < 0.3:
            # Apply aggressive semantic analysis
            # Consider merging with nearby sections
        elif section.extraction_confidence < 0.7:
            # Validate against document structure
            # Check for logical breaks
        else:
            # Trust section boundaries
            # Focus on content analysis
```

### 5. Image Processing and Storage

#### 5.1 Image Handler Component

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

@dataclass
class ImageMetadata:
    """Metadata for extracted image"""
    format: str
    width: int
    height: int
    size_bytes: int
    dpi: Optional[tuple[int, int]] = None
    color_space: Optional[str] = None

class ImageCaptioner(Protocol):
    """Protocol for image captioning services"""
    def generate_caption(self, image_data: bytes, context: str) -> str:
        """Generate caption for image using surrounding context"""
        ...

class ImageHandler:
    """Handles image processing, storage, and captioning"""
    def __init__(
        self,
        db_client: DatabaseClient,
        storage_dir: Path,
        captioner: Optional[ImageCaptioner] = None,
        size_limit: int = 1_000_000,  # 1MB
    ):
        self.db_client = db_client
        self.storage_dir = storage_dir
        self.captioner = captioner
        self.size_limit = size_limit
        
    def process_image(
        self,
        image_data: bytes,
        doc_id: str,
        section_id: str,
        context: str
    ) -> DocumentImage:
        """Process and store a single image"""
        metadata = self._extract_metadata(image_data)
        
        # Determine storage method
        if metadata.size_bytes <= self.size_limit:
            stored_image = self._store_in_db(image_data, metadata)
        else:
            stored_image = self._store_in_fs(image_data, metadata, doc_id)
            
        # Generate caption if captioner available
        caption = None
        if self.captioner:
            try:
                caption = self.captioner.generate_caption(image_data, context)
            except Exception as e:
                logging.error(f"Caption generation failed: {e}")
                
        return self._create_db_record(
            doc_id=doc_id,
            section_id=section_id,
            stored_image=stored_image,
            metadata=metadata,
            caption=caption
        )
        
    def _extract_metadata(self, image_data: bytes) -> ImageMetadata:
        """Extract image metadata using Pillow"""
        ...
        
    def _store_in_db(
        self, 
        image_data: bytes, 
        metadata: ImageMetadata
    ) -> StoredImage:
        """Store image as base64 in database"""
        ...
        
    def _store_in_fs(
        self, 
        image_data: bytes, 
        metadata: ImageMetadata,
        doc_id: str
    ) -> StoredImage:
        """Store image in filesystem"""
        ...
```

#### 5.2 Storage Strategy

The system uses a hybrid storage approach based on image size:

1. **Database Storage (≤ 1MB)**
   - Convert to base64
   - Store directly in SQLite
   - Faster retrieval for small images
   - Simpler backup/restore

2. **Filesystem Storage (> 1MB)**
   - Save to organized directory structure
   - Store path reference in database
   - Better performance for large images
   - Reduced database bloat

Directory Structure:
```
storage_dir/
└── images/
    └── {doc_id}/
        └── {image_id}.{format}
```

#### 5.3 Image Captioning

The system supports pluggable captioning services:

```python
class LLMImageCaptioner:
    """LLM-based image captioning implementation"""
    def __init__(self, llm_client: Any):
        self.llm_client = llm_client
        
    def generate_caption(self, image_data: bytes, context: str) -> str:
        """Generate caption using LLM"""
        # Convert image for LLM if needed
        # Combine with context
        # Generate caption
        # Return formatted result
        ...

class MockCaptioner:
    """Simple captioner for testing"""
    def generate_caption(self, image_data: bytes, context: str) -> str:
        return "Test caption for image"
```

Caption Generation Process:
1. Extract surrounding text context
2. Process image if needed (resize, format)
3. Generate caption with LLM
4. Validate and store result

#### 5.4 Image Processing Utilities

```python
class ImageProcessor:
    """Utilities for image processing"""
    @staticmethod
    def validate_image(image_data: bytes) -> bool:
        """Validate image data is correct and not corrupted"""
        ...
        
    @staticmethod
    def standardize_format(
        image_data: bytes,
        target_format: str = 'PNG'
    ) -> tuple[bytes, str]:
        """Convert image to standard format"""
        ...
        
    @staticmethod
    def optimize_image(
        image_data: bytes,
        max_size: int
    ) -> tuple[bytes, ImageMetadata]:
        """Optimize image while maintaining quality"""
        ...
```



```
</content>
</file_6>

<file_7>
<path>2b.2_DocumentExtraction_Sectioning_Design.md</path>
<content>
```markdown
# Document Section Analysis Technical Specification

## Overview

This document outlines the technical approach for analyzing and extracting document sections from full-text content, combining hierarchical structure analysis, semantic understanding, and flexible section numbering across different document types.

## 1. Document Structure Analysis

### 1.1 Example Document Structure

Using Chapter 7: Aerobic Fermentation from a bioprocess engineering textbook as an example:

```text
Chapter 7: Aerobic Fermentation
[Chapter intro text about aerobic fermentation basics...]

7.1 Principles of Aerobic Fermentation
[Level 1 intro text about core concepts...]

    7.1.1 Oxygen Transfer Fundamentals
    [Level 2 text about oxygen transfer...]
    
        7.1.1.1 Gas-Liquid Mass Transfer
        [Level 3 text about mass transfer coefficients...]
```

### 1.2 Key Structural Properties

1. **Hierarchical Nesting**
   - Parent sections contain their intro text plus all subsection content
   - Clear parent-child relationships through numbering
   - Each level adds one number in the hierarchy
   - Sequence matters within each level

2. **Text Organization**
   - Sections may have intro text before subsections begin
   - Intro text belongs to the parent section
   - Content is hierarchically nested
   - Images and tables may appear within sections

## 2. Schema Design

### 2.1 Core Tables

```sql
-- Track section analysis attempts
CREATE TABLE section_analyses (
    analysis_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    doc_type TEXT NOT NULL DEFAULT 'unknown'
        CHECK (doc_type IN ('journal_article', 'trade_article', 'textbook', 'unknown')),
    method TEXT NOT NULL,
    parameters TEXT,              -- JSON of analysis parameters
    source_text TEXT NOT NULL,    -- Text used for analysis
    created_at DATETIME NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

-- Track section hierarchy
CREATE TABLE document_sections (
    section_id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    section_number TEXT NOT NULL,     -- e.g., "7.1.1.2"
    section_type TEXT,                -- e.g., 'abstract', 'methods'
    level INTEGER NOT NULL,           -- 1, 2, 3, etc.
    title TEXT NOT NULL,
    intro_text TEXT,                  -- Text before subsections
    start_offset INTEGER NOT NULL,    -- Start in source_text
    end_offset INTEGER NOT NULL,      -- End in source_text
    sequence_order INTEGER NOT NULL,  -- Order within level
    FOREIGN KEY (analysis_id) REFERENCES section_analyses(analysis_id),
    CHECK (section_type IN (
        'abstract', 'introduction', 'methods', 'results', 
        'discussion', 'conclusions', 'references', NULL
    ))
);

-- Track section relationships explicitly
CREATE TABLE section_relationships (
    parent_section_id TEXT NOT NULL,
    child_section_id TEXT NOT NULL,
    PRIMARY KEY (parent_section_id, child_section_id),
    FOREIGN KEY (parent_section_id) REFERENCES document_sections(section_id),
    FOREIGN KEY (child_section_id) REFERENCES document_sections(section_id)
);
```

### 2.2 Key Column Analysis

#### intro_text
- Self-contained content before subsections
- Natural summary-level content
- Good candidate for section-level embeddings
- May be empty for leaf sections

#### sequence_order
- Integer-based for easy sorting
- Restarts at 1 for each parent section
- Independent of section numbering
- Preserves original document flow

#### section_number
- Encodes full hierarchical path
- Text format for flexibility
- Natural sort ordering
- Human readable

## 3. Section Numbering Implementation

### 3.1 Section Number Generator

```python
from enum import Enum
from typing import Optional

class DocumentType(str, Enum):
    """Types of documents supported by the system."""
    JOURNAL_ARTICLE = "journal_article"
    TRADE_ARTICLE = "trade_article"
    TEXTBOOK = "textbook"
    UNKNOWN = "unknown"

class SectionNumberGenerator:
    """Generates section numbers based on document type and structure."""
    
    def __init__(self, doc_type: DocumentType = DocumentType.UNKNOWN):
        self.doc_type = doc_type
        self.current_level = {0: 0, 1: 0, 2: 0}  # Track numbers at each level
        
    def get_next_number(self, 
                       level: int, 
                       title: str,
                       parent_number: Optional[str] = None) -> str:
        """Generate next section number based on context."""
        if self.doc_type == DocumentType.JOURNAL_ARTICLE:
            return self._get_journal_number(level, title)
        elif self.doc_type == DocumentType.TRADE_ARTICLE:
            return self._get_trade_number(level, title)
        else:  # TEXTBOOK or UNKNOWN
            return self._get_generic_number(level, parent_number)

    def _get_generic_number(self, 
                          level: int, 
                          parent_number: Optional[str] = None) -> str:
        """Generate generic hierarchical number."""
        # Reset lower levels
        for l in range(level + 1, max(self.current_level.keys()) + 1):
            self.current_level[l] = 0
            
        # Increment current level
        self.current_level[level] += 1
        
        if parent_number:
            return f"{parent_number}.{self.current_level[level]}"
        elif level == 0:
            return str(self.current_level[level])
        else:
            return f"{self.current_level[level]}"
```

## 4. Content Processing Functions

### 4.1 Section Content Extraction

```python
def get_section_content(section_id: str, include_subsections: bool = True) -> str:
    """Get section content with optional subsections."""
    section = db.get_section(section_id)
    analysis = db.get_analysis(section.analysis_id)
    
    if not include_subsections:
        # Return just this section's intro text
        return analysis.source_text[section.start_offset:section.end_offset]
    
    # Get all subsection content
    subsections = db.get_subsections(section_id)
    return _combine_section_content(section, subsections, analysis.source_text)

def get_content_by_level(analysis_id: str, max_level: int) -> str:
    """Get document content split to specified level."""
    analysis = db.get_analysis(analysis_id)
    sections = db.get_sections_by_level(analysis_id, max_level)
    return _render_sections_by_level(sections, analysis.source_text)
```

### 4.2 Hierarchical Embeddings

```python
def create_hierarchical_embeddings(section_id: str) -> dict:
    """Create embeddings at multiple levels."""
    section = db.get_section(section_id)
    
    embeddings = {
        # Level 1: Just intro text
        "intro": embed_text(section.intro_text),
        
        # Level 2: Intro + immediate subsection intros
        "summary": embed_text(_combine_with_subsection_intros(section)),
        
        # Level 3: Full content including subsections
        "full": embed_text(_get_full_content(section))
    }
    
    return embeddings
```

## 5. Search and Query Support

### 5.1 Hierarchical Section Queries

```sql
-- Get full section hierarchy
WITH RECURSIVE section_tree AS (
    -- Base case: start with top-level section
    SELECT 
        s.*, 
        0 as depth
    FROM document_sections s
    WHERE s.section_id = ?
    
    UNION ALL
    
    -- Recursive case: add children
    SELECT 
        c.*,
        st.depth + 1
    FROM section_tree st
    JOIN section_relationships r ON st.section_id = r.parent_section_id
    JOIN document_sections c ON r.child_section_id = c.section_id
)
SELECT * FROM section_tree
ORDER BY section_number;
```

### 5.2 Multi-Level Search Strategy

```python
async def search_sections(query: str) -> List[SearchResult]:
    """Multi-level section search."""
    # Level 1: Search section intros only
    intro_matches = await search_intros(query)
    if intro_matches:
        return intro_matches
        
    # Level 2: Search with subsection context
    subsection_matches = await search_with_context(query)
    if subsection_matches:
        return subsection_matches
        
    # Level 3: Full content search
    return await search_full_content(query)
```

## 6. Design Benefits

1. **Natural Summarization Levels**
   - intro_text provides ready-made summaries
   - section_number enables hierarchical rollup
   - sequence_order maintains document flow

2. **Flexible Document Support**
   - Adapts to different document types
   - Handles standard academic sections
   - Supports less formal structures

3. **Rich Context Management**
   - Full path available for each section
   - Order preserved within levels
   - Clear parent-child relationships

4. **Future Extensibility**
   - Easy to add new document types
   - Can enhance section type recognition
   - Supports custom numbering schemes
```
</content>
</file_7>

<file_8>
<path>2b_Document_Extraction.md</path>
<content>
```markdown
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
```
</content>
</file_8>

<file_9>
<path>2c_Document_Semantics.md</path>
<content>
```markdown
# Semantic Extraction Technical Specification

## Overview

### Purpose
This document specifies the semantic extraction system implementation, which transforms processed documents into searchable, semantically-meaningful content within the RAGnostic architecture.

### Scope
The system is responsible for:
- Creating logical section groupings within documents
- Captioning images and tables with contextual information
- Generating section and document summaries
- Chunking sections for efficient retrieval
- Managing relationships between documents, sections, and chunks
- Storing extracted semantic information
- Generating and managing embeddings in vector store

### System Context
- Input: Processed documents, images, and tables from Document Processing pipeline
- Output: Indexed, searchable content in ChromaDB
- Dependencies: Document Processing, Vector Storage systems

## System Architecture

```mermaid
flowchart LR
    %% Define subgraphs with clear left-to-right flow
    subgraph input[Input]
        direction TB
        docText[Document Text]
        docImg[Document Images]
        docTable[Document Tables]
    end

    subgraph stage1[Extraction]
        direction TB
        struct[Structure Analysis]
        caption[Media Captioning]
    end

    subgraph stage2[Chunking]
        direction TB
        chunks[Section Chunks]
        summaries[Section Summaries]
    end

    subgraph stage3[Embedding]
        direction TB
        chunkEmbed[Chunk Vectors]
        sumEmbed[Summary Vectors]
    end

    subgraph storage[Storage]
        direction TB
        docDB[(Document DB)]
        vecDB[(Vector DB)]
    end

    %% Define connections with minimal crossing
    docText --> struct
    docImg & docTable --> caption
    
    struct --> chunks
    struct --> summaries
    caption --> summaries
    
    chunks --> chunkEmbed
    summaries --> sumEmbed
    
    struct & caption & chunks & summaries --> docDB
    chunkEmbed & sumEmbed --> vecDB

    %% Styling
    classDef default fill:#f9f9f9,color:#000000,stroke-width:1px
    classDef input fill:#e1f5fe,color:#000000
    classDef stage fill:#f3e5f5,color:#000000
    classDef storage fill:#fff3e0,color:#000000
    
    class docText,docImg,docTable input
    class struct,caption,chunks,summaries,chunkEmbed,sumEmbed stage
    class docDB,vecDB storage
```


## 1. Input Processing
### 1.1 Document Text
- Source: Output from Document Processing system
- Format: Clean text with preserved structure markers
- Metadata requirements:
  * Line/location tracking
  * Original formatting indicators
  * Section markers

### 1.2 Document Images
- Source: Extracted during document processing
- Format requirements:
  * Standardized resolution/size for LLM processing
  * Location markers in original document
  * Associated nearby text

### 1.3 Document Tables
- Source: Extracted during document processing 
- Format options:
  * CSV for structured data
  * Image format for complex tables
- Required metadata:
  * Original location
  * Column/row headers
  * Table caption if present

## 2. Extraction Stage
### 2.1 Structure Analysis
- Input: Document text with metadata
- Process:
  * Section boundary detection
  * Hierarchy identification
  * Parent-child relationship mapping
- Output:
  * Structured document outline
  * Section metadata
  * Location mappings
  * `semantic_group` and `semantic_group_section` database entries

### 2.2 Media Captioning
- Input: Images and tables with document text context
- Process:
  * Context assembly (nearby text + document metadata)
  * LLM caption generation
  * Quality validation
- Output:
  * Descriptive captions
  * Content categorization
  * Context relationships
  * updated `document_image` database entries

### 2.3. Semantic Grouping
- Input: semantic_groups and semantic_group_sections
- Process:
  * Render full text recursively for the semantic group
  * pulls from document_sections
  * replaces table and image pklaceholder with llm caption/image description
- Output: full text renderings of semantic group
  * full text
  * markdown with emphasis and standard headers based on document_section level, etc


## 3. Chunking Stage
### 3.1 Section Chunks
- Input: Structured document sections
- Process:
  * Chunk boundary determination
  * Overlap calculation
  * Media reference preservation
- Output:
  * Manageable text chunks
  * Chunk metadata
  * Section relationships
  
### 3.2 Section Summaries
- Input: Complete sections with media
- Process:
  * Context assembly
  * Summary generation
  * Metadata extraction
- Output:
  * Section summaries
  * Topic labels
  * Key concepts


## 4. Embedding Stage
### 4.1 Chunk Vectors
- Input: Processed chunks
- Model: opensource embedding (sentence transformers)
- Output:
  * Vector embeddings
  * Metadata mapping
  * Relationship preservation

### 4.2 Summary Vectors
- Input: Section and document summaries
- Model: opensource embedding (sentence transformers)
- Output:
- Output:
  * Summary embeddings
  * Hierarchy mapping
  * Cross-references


## 5. Storage Systems
### 5.1 Vector Database (ChromaDB)
- Collections:
  * Semantic summaries
  * Semantic chunks
- Metadata mapping of document features to the database for filtering


#### semantic_summaries
- Collection name: `semantic_summaries`
- Purpose: First-stage retrieval for document/bulk section filtering
  * conceptually like topic / chapter based filtering

#### semantic_chunks
- Collection name: `semantic_chunks`
- Purpose: Second-stage retrieval within filtered documents
  * raw bits of text within a semantic group
  * used to bvetter rank the semantic group
  * better alignment of chunks within a sectionm / coverage == better semantic group


## 5.2. Document Database (SQLite)
A full view of the document schem to this stage

```sql
------------------------------------------------------------------
-- Core Document Management
------------------------------------------------------------------

-- Primary document tracking
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    raw_file_path TEXT NOT NULL,            -- Path to original file
    file_hash TEXT NOT NULL,                -- For deduplication
    file_size_bytes INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    ingestion_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Basic document metadata
CREATE TABLE document_metadata (
    doc_id TEXT PRIMARY KEY,
    title TEXT,
    authors TEXT,                           -- JSON array
    description TEXT,
    creation_date DATETIME,
    page_count INTEGER,
    language TEXT,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

------------------------------------------------------------------
-- Document Content & Structure
------------------------------------------------------------------
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

------------------------------------------------------------------
-- Semantic Groups
------------------------------------------------------------------

-- Groups of sections for semantic processing
CREATE TABLE semantic_groups (
    group_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,                           -- Generated summary
    extraction_method TEXT NOT NULL,        -- How group was derived
    embedding_id TEXT,                      -- Vector store reference
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

-- Maps sections to semantic groups
CREATE TABLE semantic_group_sections (
    group_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    sequence_order INTEGER NOT NULL,
    PRIMARY KEY (group_id, section_id),
    FOREIGN KEY (group_id) REFERENCES semantic_groups(group_id),
    FOREIGN KEY (section_id) REFERENCES document_sections(section_id)
);

------------------------------------------------------------------
-- Processing Status
------------------------------------------------------------------

-- Track document processing state
CREATE TABLE processing_status (
    doc_id TEXT PRIMARY KEY,
    status TEXT NOT NULL CHECK (
        status IN ('ingested', 'processed', 'analyzed', 'failed')
    ),
    error_message TEXT,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

------------------------------------------------------------------
-- Indexes
------------------------------------------------------------------

-- Document lookup
CREATE INDEX idx_documents_hash ON documents(file_hash);

-- Section navigation
CREATE INDEX idx_sections_doc ON document_sections(doc_id);
CREATE INDEX idx_sections_parent ON document_sections(parent_section_id);
CREATE INDEX idx_sections_sequence ON document_sections(doc_id, sequence_order);

-- Semantic group access
CREATE INDEX idx_semantic_groups_doc ON semantic_groups(doc_id);
CREATE INDEX idx_group_sections_group ON semantic_group_sections(group_id);

```

```mermaid
classDiagram
    class documents {
        +text id
        +text raw_file_path
        +text file_hash
        +integer file_size_bytes
        +text mime_type
        +datetime ingestion_date
    }

    class document_metadata {
        +text doc_id
        +text title
        +text authors
        +text description
        +datetime creation_date
        +integer page_count
        +text language
    }

    class document_sections {
        +text section_id
        +text doc_id
        +text parent_section_id
        +integer level
        +text title
        +text content
        +integer sequence_order
        +integer page_start
        +integer page_end
    }

    class semantic_groups {
        +text group_id
        +text doc_id
        +text title
        +text summary
        +text extraction_method
        +text embedding_id
    }

    class semantic_group_sections {
        +text group_id
        +text section_id
        +integer sequence_order
    }

    class document_images {
        +integer id
        +text doc_id
        +text section_id
        +text image_data
        +text caption
        +text embedding_id
        +integer page_number
    }

    class document_tables {
        +integer id
        +text doc_id
        +text section_id
        +text caption
        +text table_data
        +integer page_number
    }

    class processing_status {
        +text doc_id
        +text status
        +text error_message
        +datetime last_updated
    }

    documents "1" -- "1" document_metadata
    documents "1" -- "1" processing_status
    documents "1" -- "*" document_sections
    documents "1" -- "*" semantic_groups
    document_sections "1" -- "*" document_sections : parent
    document_sections "1" -- "*" document_images
    document_sections "1" -- "*" document_tables
    semantic_groups "1" -- "*" semantic_group_sections
    document_sections "1" -- "*" semantic_group_sections
```






# WORKING ------------------------

## Monitoring and Metrics

### Key Metrics
1. Processing Statistics:
   - Documents processed per minute
   - Average processing time per document
   - Success/failure rates

2. Quality Metrics:
   - Summary coherence scores
   - Section detection accuracy
   - Chunk size distribution
   - Relationship mapping completeness

3. Storage Metrics:
   - Database size growth
   - Index performance
   - Query response times

### Implementation

- store logs in a event table for now
- parse the logs at a later date for stats
```
</content>
</file_9>
