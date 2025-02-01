"""Tests for PDF extraction functionality."""
from datetime import datetime
from unittest.mock import patch, Mock
import pytest

from ragnostic.ingestion.indexing.extraction import PDFExtractor


def test_successful_metadata_extraction(tmp_path, sample_page_chunks):
    """Test successful metadata extraction from PDF."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert metadata is not None
        assert metadata.title == "Test Document"
        assert len(metadata.authors) == 2
        assert "John Doe" in metadata.authors
        assert metadata.language == "en"
        assert metadata.page_count == 10
        assert metadata.text_preview.startswith("First page")


def test_metadata_extraction_with_text(tmp_path, sample_page_chunks):
    """Test metadata extraction with text preview."""
    extractor = PDFExtractor(text_preview_chars=20)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    # TODO: make expected preview based on fixture, test against it truncated to the length
    chunk_texts = [page_chunk.get('text','') for page_chunk in sample_page_chunks]
    expected_text_preview = "\n".join(chunk_texts)
    preview_chars = 20

    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert len(metadata.text_preview) <= preview_chars
        assert metadata.text_preview == expected_text_preview[:preview_chars]


def test_metadata_extraction_without_text(tmp_path, partial_page_chunks):
    """Test metadata extraction without text preview."""
    extractor = PDFExtractor(text_preview_chars=0)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', return_value=partial_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert metadata.title == "Test Document"
        assert metadata.authors is None
        assert metadata.language is None
        assert metadata.text_preview is not None


def test_failed_metadata_extraction(tmp_path):
    """Test handling of failed metadata extraction."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', side_effect=Exception("PDF Error")):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert metadata is None
        assert error is not None
        assert "PDF Error" in error


@pytest.mark.parametrize("author_str,expected", [
    ("John Doe; Jane Smith", ["John Doe", "Jane Smith"]),
    ("John Doe, Jane Smith", ["John Doe", "Jane Smith"]),
    ("Single Author", ["Single Author"]),
    ("", None),
    (None, None),
])
def test_author_parsing(author_str, expected):
    """Test different author string formats."""
    extractor = PDFExtractor()
    result = extractor._parse_authors(author_str)
    assert result == expected


def test_custom_preview_length(tmp_path, sample_page_chunks):
    """Test custom text preview length."""
    extractor = PDFExtractor(text_preview_chars=10)
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    with patch('pymupdf4llm.to_markdown', return_value=sample_page_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert len(metadata.text_preview) <= 10
        assert metadata.text_preview == "First page"


def test_empty_metadata_handling(tmp_path):
    """Test handling of empty metadata fields."""
    extractor = PDFExtractor()
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    empty_chunks = [{'metadata': {}, 'text': 'content'}]
    with patch('pymupdf4llm.to_markdown', return_value=empty_chunks):
        metadata, error = extractor.extract_metadata(pdf_path)
        
        assert error is None
        assert metadata is not None
        assert metadata.title is None
        assert metadata.authors is None
        assert metadata.creation_date is None
        assert metadata.language is None
        assert metadata.page_count is None
        assert metadata.text_preview is not None


@pytest.mark.parametrize("chunks,expected_preview", [
    ([{'text': 'page1'}, {'text': 'page2'}], "page1\npage2"),
    ([{}], ""),
    ([], ""),
])
def test_page_chunks_text_concatenation(chunks, expected_preview):
    """Test text concatenation from multiple page chunks."""
    extractor = PDFExtractor()
    metadata = extractor._parse_page_chunks(chunks)
    assert metadata.text_preview.strip() == expected_preview.strip()