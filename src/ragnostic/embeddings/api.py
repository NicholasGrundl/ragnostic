"""API-backed embedding providers (key-gated, lazy imports).

These are the production-quality backends. They require API keys:
- GeminiEmbedder: GEMINI_API_KEY, `pip install ragnostic[gemini]`
- CohereEmbedder: CO_API_KEY,     `pip install ragnostic[cohere]`
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


class GeminiEmbedder:
    """Google Gemini embeddings via google-genai."""

    name = "gemini"

    def __init__(self, model: str = "gemini-embedding-001", batch_size: int = 100, client=None):
        self.model = model
        self.batch_size = batch_size
        if client is None:
            try:
                from google import genai
            except ImportError as e:
                raise ImportError(
                    "google-genai is not installed. Install with: pip install ragnostic[gemini]"
                ) from e
            client = genai.Client()
        self.client = client

    def _embed(self, texts: List[str], task_type: str) -> List[List[float]]:
        vectors: List[List[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            response = self.client.models.embed_content(
                model=self.model,
                contents=batch,
                config={"task_type": task_type},
            )
            vectors.extend(e.values for e in response.embeddings)
        return vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts, task_type="RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text], task_type="RETRIEVAL_QUERY")[0]


class CohereEmbedder:
    """Cohere embeddings via the cohere SDK."""

    name = "cohere"

    def __init__(self, model: str = "embed-english-v3.0", batch_size: int = 96, client=None):
        self.model = model
        self.batch_size = batch_size
        if client is None:
            try:
                import cohere
            except ImportError as e:
                raise ImportError(
                    "cohere is not installed. Install with: pip install ragnostic[cohere]"
                ) from e
            client = cohere.Client()
        self.client = client

    def _embed(self, texts: List[str], input_type: str) -> List[List[float]]:
        vectors: List[List[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            response = self.client.embed(
                texts=batch, model=self.model, input_type=input_type
            )
            vectors.extend(response.embeddings)
        return vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts, input_type="search_document")

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text], input_type="search_query")[0]


class FastEmbedEmbedder:
    """Local ONNX embeddings via fastembed (no torch, but downloads model
    weights from HuggingFace on first use).

    Install with: pip install ragnostic[local-embed]
    """

    name = "fastembed"

    def __init__(self, model: str = "BAAI/bge-small-en-v1.5"):
        try:
            from fastembed import TextEmbedding
        except ImportError as e:
            raise ImportError(
                "fastembed is not installed. Install with: pip install ragnostic[local-embed]"
            ) from e
        self.model_name = model
        self.model = TextEmbedding(model)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [v.tolist() for v in self.model.embed(texts)]

    def embed_query(self, text: str) -> List[float]:
        return next(iter(self.model.query_embed(text))).tolist()
