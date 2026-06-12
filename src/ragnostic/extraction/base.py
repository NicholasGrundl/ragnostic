"""Parser interface for full-document text extraction."""
from pathlib import Path
from typing import Protocol, runtime_checkable

from .schema import ParsedDocument


@runtime_checkable
class DocumentParser(Protocol):
    """Protocol for full-document parsers.

    Implementations turn a raw document file into an ordered list of
    sections with text and page ranges.
    """

    name: str

    def parse(self, filepath: Path, doc_id: str) -> ParsedDocument:
        """Parse a document into sections."""
        ...
