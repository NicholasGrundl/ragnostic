"""Tests for the ingestion monitor functionality."""
from pathlib import Path
import pytest

from ragnostic.ingestion import utils

@pytest.mark.parametrize("prefix", ["DOC", "ID", "PREFIX"])
def test_create_doc_id(prefix):
    """Test that the create_doc_id function returns a string with the correct prefix."""
    doc_id = utils.create_doc_id(prefix=prefix)
    assert doc_id.startswith(prefix)

