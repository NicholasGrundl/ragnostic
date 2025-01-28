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