"""
Basic utilities for document ingestion.

Kept for backward compatibility; canonical implementation lives in
ragnostic.utils so non-ingestion modules can use it without importing the
ingestion package.
"""
from ragnostic.utils import DEFAULT_ALPHABET, create_doc_id

__all__ = ["DEFAULT_ALPHABET", "create_doc_id"]
