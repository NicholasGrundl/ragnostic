# """Tests for document indexer functionality."""
# from pathlib import Path
# from unittest.mock import patch, Mock

# import pytest
# from ragnostic.ingestion.indexing import DocumentIndexer
# from ragnostic.ingestion.indexing.schema import IndexingStatus
# from ragnostic.db.schema import DocumentCreate, DocumentMetadataCreate


# def test_indexer_initialization(mock_db_client):
#     """Test DocumentIndexer initialization."""
#     indexer = DocumentIndexer(mock_db_client)
#     assert indexer.db_client == mock_db_client
#     assert indexer.extractor is not None


# def test_successful_indexing(mock_db_client, mock_pdf_processor, sample_pdf_path):
#     """Test successful document indexing with metadata."""
    


# def test_indexing_without_metadata(mock_db_client, mock_pdf_processor, sample_pdf_path):
#     """Test successful document indexing when metadata extraction fails."""
    


# def test_indexing_with_database_error(mock_db_client, mock_pdf_processor, sample_pdf_path):
#     """Test handling of database errors during indexing."""
    


# def test_batch_indexing_success(mock_db_client, mock_pdf_processor, multiple_pdf_paths):
#     """Test successful batch indexing of multiple documents."""
    


# def test_batch_indexing_with_failures(mock_db_client, mock_pdf_processor, multiple_pdf_paths):
#     """Test batch indexing with mixed success and failures."""


# def test_indexing_with_corrupted_file(mock_db_client, corrupted_pdf_path):
#     """Test handling of corrupted PDF files."""


# def test_metadata_creation_error(mock_db_client, mock_pdf_processor, sample_pdf_path):
#     """Test handling of metadata creation errors."""


# def test_text_extraction_options(mock_db_client, mock_pdf_processor, sample_pdf_path):
#     """Test different text extraction configurations."""


# def test_empty_batch_indexing(mock_db_client):
#     """Test batch indexing with empty list."""