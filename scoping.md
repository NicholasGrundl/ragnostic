# TODO

- Redo installation instructions on Ubuntu/WSL
  - Include Tesseract/ffmpeg
  - use conda setup
  - pytorch with GPU and verify
- Combine scoping documents into one doc
  - review each
  - make a high level DAG workflow for the main logic
- Datamodel/Storage
  - Make raw storage heirarchy diagram
  - make document library SQL SCHEMA
  - make ChromaDB datamodel SCHEMA
- List proposed implementation of packages
  - docling
  - burr
  - chromadb
  - sqllite?
  - opensource embedding algorithm
  - summarize via claude?


# Overview

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

## High level workflow

flowchart TD
    %% Document Processing Pipeline
    docs[Raw Documents] --> ingest[Document Ingestion]
    ingest --> sql[(Document SQL DB)]
    ingest --> store[Raw Storage]
    
    store --> parse[Document Parser]
    parse -->|Text| process[Document Processor]
    parse --> |Tables| tables[Table Extraction]
    parse --> |Images| images[Image Extraction]
    
    process --> |Document Text| sum[Summary Generator]
    process --> |Document Text| chunk[Chunk Generator]
    
    sum --> |Document Summaries| vec[(Vector DB)]
    chunk --> |Text Chunks| vec
    
    %% Query Processing Pipeline
    query[User Query] --> embed[Query Embedding]
    embed --> docsearch[Document Search]
    
    docsearch --> |Relevant Doc IDs| chunksearch[Chunk Search]
    vec --> docsearch
    vec --> chunksearch
    
    chunksearch --> post[Post Processing]
    post --> rank[Section Reranking]
    rank --> results[Search Results]
    
    %% Styling
    classDef storage fill:#f9f,stroke:#333,stroke-width:2px
    classDef process fill:#bbf,stroke:#333,stroke-width:2px
    classDef input fill:#bfb,stroke:#333,stroke-width:2px
    classDef output fill:#fbb,stroke:#333,stroke-width:2px
    
    class sql,store,vec storage
    class ingest,parse,process,sum,chunk,embed,docsearch,chunksearch,post,rank process
    class docs,query input
    class results output

