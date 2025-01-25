
# Hierarchical RAG System Requirements

## System Overview
A hierarchical retrieval augmented generation system that searches document summaries first to filter the document list, then performs vector search on smaller chunks within filtered documents.

## Data Sources
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

## Technical Requirements

### Document Processing
- Parse Wikipedia articles via API
- Process PDFs using Doculing
- Organize files in structured storage system
- Generate and track document metadata
- Create hierarchical summaries and chunks
- Compute embeddings at multiple levels

### Storage Requirements
- Raw document storage with consistent structure
- Document metadata and relationship tracking
- Vector indices for summaries and chunks
- Support for binary/blob storage
- Efficient query patterns for hierarchical search

### Query Pipeline
1. Document summary search via embeddings
2. Filtered chunk search within matched documents
3. Basic reranking system (grouped by section/document)

### Performance Requirements
- Query response time: Up to 30 seconds acceptable
- Infrequent document updates (daily at most)
- Local deployment initially, cloud migration planned

### Evaluation System
- Accuracy and precision metrics
- Parameter tuning capability
- System performance tracking

## Technology Stack

### Core Libraries
- Doculing for PDF parsing
- Wikipedia API for article access
- Vector databases: ChromaDB or LanceDB

### Processing Pipeline
1. Ingest from monitored directory
2. Parse and extract content
3. Generate metadata
4. Create hierarchical structures
5. Compute embeddings
6. Store in vector database

### Future Considerations
- Cloud deployment
- API service development
- Enhanced reranking system
- Evaluation metrics implementation
- Parameter optimization






# ChromaDB Implementation Scope

## Pipeline Components

### Document Ingestion
Monitors input directory for new documents. Processes Wikipedia articles via API and PDFs via Doculing. Assigns unique IDs, extracts metadata and text, organizes into structured storage.

### Document Processing
Handles text extraction, structure parsing, and metadata generation. Manages raw file movement to organized storage. Creates document records in database.

### Hierarchical Processing
Generates document and section summaries. Creates semantic chunks. Computes embeddings for all levels. Maintains relationships between levels.

### Vector Storage
Manages ChromaDB collections for summaries and chunks. Handles metadata association and relationship tracking. Provides query interface.

### Query Pipeline
Processes user queries through hierarchical search. Performs document filtering and chunk retrieval. Implements basic reranking.

## System Flow

sequenceDiagram
    participant ID as Ingest Directory
    participant DP as Document Processor
    participant RS as Raw Storage
    participant HP as Hierarchical Processor
    participant CH as ChromaDB
    participant QE as Query Engine

    ID->>DP: New document
    DP->>RS: Store raw file
    DP->>HP: Document content
    HP->>HP: Generate summaries
    HP->>HP: Create chunks
    HP->>CH: Store vectors & metadata
    QE->>CH: Query embedding
    CH->>QE: Document matches
    QE->>CH: Filtered chunk query
    CH->>QE: Relevant chunks

## Project Plan

### Document Ingestion
- Create file monitor system
  * watchdog for directory monitoring
  * file type detection
- Implement Wikipedia API client
  * wikipediaapi package
  * error handling and rate limiting
- Build PDF processing pipeline
  * doculing integration
  * layout analysis configuration
- Design ID generation system
  * UUID generation
  * document type prefixes
- Implement metadata extraction
  * title and author extraction
  * date and source tracking

### Raw Storage
- Design directory structure
  * separate dirs by document type
  * consistent naming convention
- Implement file movement logic
  * atomic operations
  * duplicate handling
- Create backup system
  * periodic snapshots
  * verification checks

### Hierarchical Processing
- Implement summary generation
  * extractive summarization
  * configurable length control
- Design chunking system
  * semantic boundaries
  * context preservation
- Create embedding pipeline
  * model selection
  * batch processing
- Implement metadata tracking
  * parent-child relationships
  * position tracking

### ChromaDB Integration
- Design collection structure
  * separate collections per level
  * metadata schema
- Implement vector storage
  * batch insertion
  * update handling
- Create query interfaces
  * filtering functions
  * relationship tracking
- Build index maintenance
  * optimization routines
  * health checks

### Query Pipeline
- Implement query processing
  * embedding generation
  * query reformulation
- Create hierarchical search
  * document filtering
  * chunk retrieval
- Design reranking system
  * grouping logic
  * score combination
- Build result formatting
  * metadata inclusion
  * context assembly

Would you like me to continue with the LanceDB implementation?