"""Section-aware chunking for retrieval.

Chunks are built per section so every chunk maps to exactly one section,
which the query pipeline relies on for section-coverage reranking.
"""
import logging
from typing import List, Optional

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import DocumentChunk, DocumentChunkCreate, DocumentSection
from ragnostic.utils import create_doc_id

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_WORDS = 250
DEFAULT_OVERLAP_WORDS = 50


def chunk_text(
    text: str,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
) -> List[str]:
    """Split text into overlapping word-window chunks.

    Word-based windows keep the implementation dependency-free; swap in a
    token-based splitter later if retrieval quality demands it.
    """
    if overlap_words >= chunk_words:
        raise ValueError("overlap_words must be smaller than chunk_words")

    words = text.split()
    if not words:
        return []
    if len(words) <= chunk_words:
        return [" ".join(words)]

    chunks = []
    step = chunk_words - overlap_words
    for start in range(0, len(words), step):
        window = words[start : start + chunk_words]
        chunks.append(" ".join(window))
        if start + chunk_words >= len(words):
            break
    return chunks


def chunk_sections(
    doc_id: str,
    sections: List[DocumentSection],
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
) -> List[DocumentChunkCreate]:
    """Build chunk records for a document's sections.

    Section titles are prepended to each chunk so the embedded text carries
    its local context.
    """
    chunk_creates: List[DocumentChunkCreate] = []
    sequence = 0
    for section in sorted(sections, key=lambda s: s.sequence_order):
        if section.content is None or not section.content.content.strip():
            continue
        title = section.content.title
        for text in chunk_text(section.content.content, chunk_words, overlap_words):
            chunk_body = f"{title}\n\n{text}" if title and title != "Untitled" else text
            chunk_creates.append(
                DocumentChunkCreate(
                    chunk_id=create_doc_id(prefix="CHK"),
                    doc_id=doc_id,
                    section_id=section.section_id,
                    sequence_order=sequence,
                    text=chunk_body,
                    word_count=len(chunk_body.split()),
                )
            )
            sequence += 1
    return chunk_creates


def chunk_document(
    db_client: DatabaseClient,
    doc_id: str,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
    sections: Optional[List[DocumentSection]] = None,
) -> List[DocumentChunk]:
    """Chunk a document's stored sections and persist the chunks."""
    if sections is None:
        sections = db_client.get_document_sections(doc_id)
    chunk_creates = chunk_sections(doc_id, sections, chunk_words, overlap_words)
    if not chunk_creates:
        logger.warning("No chunkable content for document %s", doc_id)
        return []
    return db_client.create_chunks(chunk_creates)
