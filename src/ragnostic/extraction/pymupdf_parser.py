"""Full-document parser backed by pymupdf4llm (lightweight, no model weights)."""
import logging
from pathlib import Path

from .markdown_sections import split_markdown_sections
from .schema import ParsedDocument

logger = logging.getLogger(__name__)


class PyMuPDFParser:
    """Parse a PDF into markdown sections using pymupdf4llm."""

    name = "pymupdf4llm"

    def parse(self, filepath: Path, doc_id: str) -> ParsedDocument:
        import pymupdf4llm

        page_chunks = pymupdf4llm.to_markdown(str(filepath), page_chunks=True)
        pages = []
        for chunk in page_chunks:
            page_number = chunk.get("metadata", {}).get("page")
            pages.append((chunk.get("text", ""), page_number))

        sections = split_markdown_sections(pages, default_title=filepath.stem)
        return ParsedDocument(
            doc_id=doc_id,
            sections=sections,
            page_count=len(page_chunks),
            parser_name=self.name,
        )
