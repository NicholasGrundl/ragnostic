"""Split markdown text into logical sections by header.

Used by parsers that emit markdown (pymupdf4llm, docling) so section
detection behaves identically regardless of the parsing backend.
"""
import re
from typing import List, Optional, Tuple

from .schema import ParsedSection

HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def split_markdown_sections(
    pages: List[Tuple[str, Optional[int]]],
    default_title: str = "Body",
) -> List[ParsedSection]:
    """Split markdown pages into sections on headers.

    Args:
        pages: List of (markdown_text, page_number) tuples in document order.
            Page numbers are 1-based and may be None.
        default_title: Title for leading content that appears before any header.

    Returns:
        Ordered list of ParsedSection. Documents without headers yield a
        single section containing all text.
    """
    # Build one combined string while remembering which character offset
    # starts each page, so sections can be mapped back to page ranges.
    combined_parts: List[str] = []
    page_offsets: List[Tuple[int, Optional[int]]] = []  # (start_offset, page_number)
    offset = 0
    for text, page_number in pages:
        page_offsets.append((offset, page_number))
        combined_parts.append(text)
        offset += len(text) + 1  # +1 for joining newline
    combined = "\n".join(combined_parts)

    def page_at(char_offset: int) -> Optional[int]:
        page = None
        for start, number in page_offsets:
            if char_offset >= start:
                page = number
            else:
                break
        return page

    matches = list(HEADER_RE.finditer(combined))
    sections: List[ParsedSection] = []

    def add_section(title: str, level: int, start: int, end: int) -> None:
        text = combined[start:end].strip()
        if not text and not title:
            return
        sections.append(
            ParsedSection(
                title=title,
                text=text,
                level=level,
                page_start=page_at(start),
                page_end=page_at(max(start, end - 1)),
            )
        )

    if not matches:
        add_section(default_title, 1, 0, len(combined))
        return sections

    # Content before the first header
    if matches[0].start() > 0 and combined[: matches[0].start()].strip():
        add_section(default_title, 1, 0, matches[0].start())

    for i, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(combined)
        add_section(
            title=match.group(2).strip(),
            level=len(match.group(1)),
            start=body_start,
            end=body_end,
        )

    return sections
