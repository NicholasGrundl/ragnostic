# Issue 12: Implement Semantic Extraction (Phase 2)

**Priority:** Medium (Future)
**Estimated Effort:** 4-6 weeks
**Labels:** `feature`, `ml`, `phase-2`, `epic`
**Phase:** 2 - Semantic Extraction

## Problem Statement

From project plan (docs/2b_Semantic_Extraction.md):
- Documents are ingested but not semantically analyzed
- No section hierarchy extraction
- No image/table captioning
- No document summarization
- No chunking for RAG retrieval

Phase 2 is fully documented but not yet implemented.

## Scope

This is an **EPIC** issue covering the entire Phase 2 implementation:

1. **Section Grouping** - Detect document structure and hierarchy
2. **Image Captioning** - Generate descriptions for figures/images
3. **Table Understanding** - Extract and describe tabular data
4. **Document Summarization** - Create document-level summaries
5. **Chunking Strategy** - Split documents for vector search
6. **Entity Extraction** - Identify key concepts and entities

## Current State

**Implemented:**
- Document ingestion (Phase 1)
- Basic metadata extraction
- PDF text extraction
- Database storage

**Not Implemented:**
- Section detection
- Image/table processing
- LLM-based analysis
- Chunking algorithms
- Summary generation

## Reference Documentation

Complete specification exists in:
- `docs/2b_Semantic_Extraction.md` (12,769 bytes)
- Database schema defined
- Processing flow documented
- LLM integration planned

## Proposed Approach

Break down into sub-issues:

### Sub-Issue 12.1: Section Hierarchy Detection
- Use docling's layout analysis
- Build section tree structure
- Store in `document_sections` table
- Estimated: 1-2 weeks

### Sub-Issue 12.2: Image and Table Captioning
- Extract images/tables from PDFs
- Use multimodal LLM (GPT-4V, Claude, Gemini) for captioning
- Store captions in database
- Estimated: 1-2 weeks

### Sub-Issue 12.3: Document Summarization
- Generate document-level summaries
- Generate section-level summaries
- Use structured output with Instructor
- Estimated: 1 week

### Sub-Issue 12.4: Chunking Implementation
- Implement multiple chunking strategies
  - Fixed size with overlap
  - Semantic chunking (by section)
  - Recursive chunking
- Store chunks in database
- Estimated: 1-2 weeks

### Sub-Issue 12.5: Entity and Concept Extraction
- Extract key terms, concepts, entities
- Build knowledge graph connections
- Tag documents with extracted entities
- Estimated: 1-2 weeks

## Acceptance Criteria

- [ ] All sub-issues completed
- [ ] Section hierarchy extracted and stored
- [ ] Images and tables captioned
- [ ] Document summaries generated
- [ ] Documents chunked for retrieval
- [ ] Entities and concepts extracted
- [ ] Integration tests pass
- [ ] Performance acceptable (<5 min per document)

## Implementation Steps

See `docs/2b_Semantic_Extraction.md` for detailed specification.

High-level steps:
1. Create sub-issues for each component
2. Implement docling-based section extraction
3. Integrate LLM providers (OpenAI, Anthropic, Gemini)
4. Implement image/table captioning pipeline
5. Add summarization workflow
6. Implement chunking strategies
7. Add entity extraction
8. Create semantic extraction workflow (Burr)
9. Integration testing
10. Performance optimization

## Dependencies

**Required before:**
- Issue #03 (package installation)
- Phase 1 complete (document ingestion working)
- LLM API keys configured

**Enhanced by:**
- Issue #05 (logging)
- Issue #07 (database architecture)

## Testing Strategy

- Unit tests for each extraction component
- Integration tests for full semantic extraction
- Test with various document types (article, journal, report, textbook)
- Performance testing with large documents
- LLM output validation

## Parallel Work Opportunities

This is a large epic that should be broken down into parallel sub-issues:

**Can work in parallel:**
- Sub-issue 12.1 (section detection) and 12.4 (chunking)
- Sub-issue 12.2 (image/table) and 12.3 (summarization)

**Must be sequential:**
- Section detection before semantic chunking
- Chunking before vector storage (Phase 3)

## Cost Considerations

**LLM API costs:**
- Image captioning: ~$0.01-0.05 per image (GPT-4V)
- Summarization: ~$0.001-0.01 per page
- Estimate $0.10-0.50 per document

**Mitigation:**
- Cache LLM responses
- Batch API requests
- Use cheaper models where possible (Gemini Flash, Claude Haiku)
- Implement rate limiting

## Performance Targets

- Section extraction: <30s per document
- Image captioning: <5s per image
- Summarization: <1 min per document
- Total semantic extraction: <5 min per document
- Support batch processing of multiple documents

## Future Enhancements

- Multimodal embeddings for images
- Table understanding with specialized models
- Citation extraction and linking
- Cross-document relationship detection
- Incremental extraction (update only changed sections)

## Notes

- This is the most complex phase of the project
- Requires careful LLM prompt engineering
- Should implement caching to reduce costs
- Consider rate limiting for API calls
- May want to make LLM provider configurable
- Document extraction quality varies by PDF type
