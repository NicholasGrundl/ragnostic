help me combine the following system design docs into one markdown artifact.

Section Hierarchy Examples and Analysis

Section Schema Column Analysis

Section Numbering Across Document Types

<context>

We are assessing how to obtain sections from a document analysis of a full document text representation.

</context>

<notes_on_docs>
<note1>
The key insights from `Section Hierarchy Examples and Analysis`:

1. **Source Text Placement**: You're right - storing the processed text with the analysis makes more sense. Each analysis might use slightly different text (different image descriptions, different preprocessing).

2. **Section Relationships**: The explicit relationship table makes queries much cleaner and supports complex hierarchies while maintaining order.

3. **Content Rendering**: Using offsets and a single source text makes it easy to extract content at any level while preserving the exact original text.

4. **Flexible Querying**: The schema supports both top-down and bottom-up traversal of the section hierarchy.
</note1>

<note2>
The key insight for `Section Schema Column Analysis` is that these columns work together to enable both structural organization and semantic analysis:

1. `intro_text` provides natural summary-level content for each section, perfect for hierarchical embeddings
2. `sequence_order` helps maintain document flow and context windows
3. `section_number` encodes the full hierarchical path, enabling relationship tracking

For semantic analysis, this structure allows us to:
1. Create embeddings at multiple granularities (intro, summary, full)
2. Generate chunks with rich hierarchical context
3. Implement sophisticated search strategies
</note2>

<note3>

The key insight for `Section Numbering Across Document Types
` is that we need a flexible numbering system that can:

Recognize and handle standard academic section patterns
Adapt to less structured documents
Fall back to simple sequential numbering when needed

The SectionNumberGenerator provides this flexibility while maintaining our ability to:

Track hierarchical relationships
Support semantic analysis
Enable section type recognition
</note3>
</notes_on_docs>