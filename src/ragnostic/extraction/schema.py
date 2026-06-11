"""Schemas for full-document text extraction."""
from typing import List, Optional

from pydantic import BaseModel, Field


class ParsedSection(BaseModel):
    """A logical section parsed from a document body."""
    title: str
    text: str
    level: int = Field(default=1, description="Header level (1=H1, etc)")
    page_start: Optional[int] = None
    page_end: Optional[int] = None


class ParsedDocument(BaseModel):
    """Full-document parse result."""
    doc_id: str
    sections: List[ParsedSection] = Field(default_factory=list)
    page_count: Optional[int] = None
    parser_name: str = "unknown"

    @property
    def full_text(self) -> str:
        return "\n\n".join(s.text for s in self.sections)
