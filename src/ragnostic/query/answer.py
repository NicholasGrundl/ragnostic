"""Optional LLM answer generation (key-gated).

Build an answer_fn for QueryPipeline. Retrieval never requires this; it only
activates when an API key/client is available.
"""
import logging
from typing import Callable

logger = logging.getLogger(__name__)

ANSWER_PROMPT = """You are a technical assistant answering questions about engineering documents.
Answer the question using ONLY the numbered context passages below. Cite passage
numbers like [1] where used. If the context is insufficient, say so.

Question: {query}

Context:
{context}

Answer:"""


def make_gemini_answer_fn(model: str = "gemini-2.0-flash", client=None) -> Callable[[str, str], str]:
    """Answer generation via google-genai (GEMINI_API_KEY required)."""
    if client is None:
        try:
            from google import genai
        except ImportError as e:
            raise ImportError(
                "google-genai is not installed. Install with: pip install ragnostic[gemini]"
            ) from e
        client = genai.Client()

    def answer_fn(query: str, context: str) -> str:
        prompt = ANSWER_PROMPT.format(query=query, context=context)
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text.strip()

    return answer_fn


def make_anthropic_answer_fn(
    model: str = "claude-sonnet-4-6", max_tokens: int = 1024, client=None
) -> Callable[[str, str], str]:
    """Answer generation via the Anthropic SDK (ANTHROPIC_API_KEY required)."""
    if client is None:
        try:
            import anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic is not installed. Install with: pip install ragnostic[anthropic]"
            ) from e
        client = anthropic.Anthropic()

    def answer_fn(query: str, context: str) -> str:
        prompt = ANSWER_PROMPT.format(query=query, context=context)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    return answer_fn
