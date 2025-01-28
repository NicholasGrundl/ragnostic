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