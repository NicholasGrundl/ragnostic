"""Embedding provider interface."""
from typing import List, Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for embedding backends.

    Implementations must return L2-comparable vectors of a fixed dimension;
    the vector store uses cosine distance.
    """

    name: str

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of documents/chunks for storage."""
        ...

    def embed_query(self, text: str) -> List[float]:
        """Embed a query for search."""
        ...
