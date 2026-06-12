"""Document summarization for first-tier (summary) retrieval.

The default ExtractiveSummarizer needs no API keys or model downloads, so the
two-tier pipeline always runs. LLMSummarizer is a drop-in upgrade when an API
key is available.
"""
import logging
import re
from typing import List, Optional, Protocol, runtime_checkable

from ragnostic.db.client import DatabaseClient
from ragnostic.db.schema import DocumentSummary, DocumentSummaryCreate

logger = logging.getLogger(__name__)

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


@runtime_checkable
class Summarizer(Protocol):
    """Protocol for document summarizers."""

    method: str

    def summarize(self, title: Optional[str], section_titles: List[str], text: str) -> str:
        """Produce a document-level summary."""
        ...


class ExtractiveSummarizer:
    """Keyless summarizer: title, section outline, and leading sentences.

    Crude but effective for lexical (TF-IDF) tier-1 search since it surfaces
    the document's own vocabulary.
    """

    method = "extractive"

    def __init__(self, max_sentences: int = 10, max_section_titles: int = 30):
        self.max_sentences = max_sentences
        self.max_section_titles = max_section_titles

    def summarize(self, title: Optional[str], section_titles: List[str], text: str) -> str:
        parts = []
        if title:
            parts.append(title)
        titles = [t for t in section_titles if t and t != "Untitled"]
        if titles:
            parts.append("Sections: " + "; ".join(titles[: self.max_section_titles]))
        sentences = SENTENCE_RE.split(text.strip())
        if sentences:
            parts.append(" ".join(sentences[: self.max_sentences]))
        return "\n".join(parts).strip()


class LLMSummarizer:
    """LLM-backed summarizer (requires an API key).

    Supports the google-genai client (`pip install ragnostic[gemini]`,
    GEMINI_API_KEY) by default; pass a different `client` for other providers.
    """

    def __init__(self, model: str = "gemini-2.0-flash", max_chars: int = 50_000, client=None):
        self.model = model
        self.max_chars = max_chars
        self.method = f"llm:{model}"
        if client is None:
            try:
                from google import genai
            except ImportError as e:
                raise ImportError(
                    "google-genai is not installed. Install with: pip install ragnostic[gemini]"
                ) from e
            client = genai.Client()
        self.client = client

    def summarize(self, title: Optional[str], section_titles: List[str], text: str) -> str:
        prompt = (
            "Summarize the following technical document in 5-10 sentences. "
            "Cover the main topics, methods, and conclusions so the summary can be "
            "used for retrieval. Include key domain terminology.\n\n"
            f"Title: {title or 'unknown'}\n"
            f"Section outline: {'; '.join(section_titles[:50])}\n\n"
            f"Document text (truncated):\n{text[: self.max_chars]}"
        )
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text.strip()


def summarize_document(
    db_client: DatabaseClient,
    doc_id: str,
    summarizer: Optional[Summarizer] = None,
) -> DocumentSummary:
    """Generate and persist a summary for a document's stored sections."""
    summarizer = summarizer or ExtractiveSummarizer()

    sections = db_client.get_document_sections(doc_id)
    metadata = db_client.get_metadata(doc_id)
    title = metadata.title if metadata else None
    section_titles = [s.content.title for s in sections if s.content]
    text = "\n\n".join(s.content.content for s in sections if s.content)

    summary_text = summarizer.summarize(title, section_titles, text)
    if not summary_text:
        summary_text = title or doc_id

    return db_client.upsert_summary(
        DocumentSummaryCreate(doc_id=doc_id, summary=summary_text, method=summarizer.method)
    )
