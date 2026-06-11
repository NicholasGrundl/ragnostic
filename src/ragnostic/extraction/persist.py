"""Persist parsed documents into the document database."""
import logging
from typing import List

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import DocumentSection, DocumentSectionCreate, SectionContentCreate
from ragnostic.utils import create_doc_id

from .schema import ParsedDocument

logger = logging.getLogger(__name__)


def persist_parsed_document(
    db_client: DatabaseClient,
    parsed: ParsedDocument,
) -> List[DocumentSection]:
    """Store a parsed document's sections and content in the database.

    Parent/child links are derived from header levels: a section's parent is
    the most recent preceding section with a lower level.

    Returns:
        The created DocumentSection records in document order.
    """
    created: List[DocumentSection] = []
    parent_stack: List[tuple] = []  # (level, section_id)

    for sequence, section in enumerate(parsed.sections):
        section_id = create_doc_id(prefix="SEC")

        while parent_stack and parent_stack[-1][0] >= section.level:
            parent_stack.pop()
        parent_section_id = parent_stack[-1][1] if parent_stack else None

        record = db_client.create_section(
            section=DocumentSectionCreate(
                section_id=section_id,
                doc_id=parsed.doc_id,
                parent_section_id=parent_section_id,
                level=section.level,
                sequence_order=sequence,
                word_count=len(section.text.split()),
            ),
            content=SectionContentCreate(
                section_id=section_id,
                title=section.title or "Untitled",
                content=section.text,
                page_start=section.page_start,
                page_end=section.page_end,
            ),
        )
        created.append(record)
        parent_stack.append((section.level, section_id))

    logger.info("Persisted %d sections for %s", len(created), parsed.doc_id)
    return created
