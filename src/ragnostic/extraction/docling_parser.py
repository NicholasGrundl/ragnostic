"""Full-document parser backed by docling (richer layout, heavy dependencies).

Requires the `docling` extra: `pip install ragnostic[docling]`. Docling
downloads layout models from HuggingFace on first use, so it needs network
access (or pre-cached models).
"""
import logging
from pathlib import Path

from .markdown_sections import split_markdown_sections
from .schema import ParsedDocument

logger = logging.getLogger(__name__)


class DoclingParser:
    """Parse a PDF into markdown sections using docling."""

    name = "docling"

    def parse(self, filepath: Path, doc_id: str) -> ParsedDocument:
        try:
            from docling.document_converter import DocumentConverter
        except ImportError as e:
            raise ImportError(
                "docling is not installed. Install with: pip install ragnostic[docling]"
            ) from e

        converter = DocumentConverter()
        result = converter.convert(str(filepath))
        markdown = result.document.export_to_markdown()
        page_count = getattr(result.document, "num_pages", None)
        if callable(page_count):
            page_count = page_count()

        sections = split_markdown_sections([(markdown, None)], default_title=filepath.stem)
        return ParsedDocument(
            doc_id=doc_id,
            sections=sections,
            page_count=page_count,
            parser_name=self.name,
        )
