"""TF-IDF embedding provider.

Fully offline and deterministic: no API keys, no model downloads. Lexical
rather than semantic, so treat it as the prototype backend — the vector-store
and query layers don't care which provider produced the vectors.

The vectorizer must be fitted on the corpus before embedding and the fitted
state persisted alongside the vector store, since queries must be projected
into the same vector space.
"""
import logging
import pickle
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

DEFAULT_DIM = 512
VECTORIZER_FILENAME = "tfidf_vectorizer.pkl"


class TfidfEmbedder:
    """Corpus-fitted TF-IDF embeddings via scikit-learn."""

    name = "tfidf"

    def __init__(self, max_features: int = DEFAULT_DIM):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words="english",
            sublinear_tf=True,
        )
        self._fitted = False

    def fit(self, corpus: List[str]) -> "TfidfEmbedder":
        """Fit the vectorizer on the full corpus (chunks + summaries)."""
        self.vectorizer.fit(corpus)
        self._fitted = True
        return self

    def _transform(self, texts: List[str]) -> List[List[float]]:
        if not self._fitted:
            raise RuntimeError("TfidfEmbedder must be fitted (or loaded) before embedding")
        matrix = self.vectorizer.transform(texts).toarray()
        # Pad to a fixed dimension: small corpora can yield fewer features
        # than max_features, but the vector store requires consistent dims.
        if matrix.shape[1] < self.max_features:
            import numpy as np

            matrix = np.pad(matrix, ((0, 0), (0, self.max_features - matrix.shape[1])))
        return matrix.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._transform(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._transform([text])[0]

    def save(self, directory: Path) -> Path:
        """Persist the fitted vectorizer next to the vector store."""
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / VECTORIZER_FILENAME
        with open(path, "wb") as f:
            pickle.dump({"vectorizer": self.vectorizer, "max_features": self.max_features}, f)
        return path

    @classmethod
    def load(cls, directory: Path) -> "TfidfEmbedder":
        """Load a previously fitted vectorizer."""
        path = Path(directory) / VECTORIZER_FILENAME
        with open(path, "rb") as f:
            payload = pickle.load(f)
        embedder = cls(max_features=payload["max_features"])
        embedder.vectorizer = payload["vectorizer"]
        embedder._fitted = True
        return embedder
