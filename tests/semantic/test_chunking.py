"""Tests for section-aware chunking."""
import pytest

from ragnostic.semantic.chunking import chunk_sections, chunk_text


@pytest.mark.unit
def test_chunk_text_short_returns_single_chunk():
    chunks = chunk_text("one two three", chunk_words=250, overlap_words=50)
    assert chunks == ["one two three"]


@pytest.mark.unit
def test_chunk_text_empty_returns_empty():
    assert chunk_text("", chunk_words=10, overlap_words=2) == []


@pytest.mark.unit
def test_chunk_text_windows_with_overlap():
    words = [f"w{i}" for i in range(100)]
    chunks = chunk_text(" ".join(words), chunk_words=40, overlap_words=10)
    # step = 30: windows start at 0, 30, 60; the 60:100 window reaches the end
    assert len(chunks) == 3
    assert chunks[0].split()[:1] == ["w0"]
    # overlap: last 10 words of chunk0 are first 10 of chunk1
    assert chunks[0].split()[-10:] == chunks[1].split()[:10]


@pytest.mark.unit
def test_chunk_text_rejects_overlap_ge_chunk():
    with pytest.raises(ValueError):
        chunk_text("a b c", chunk_words=10, overlap_words=10)


@pytest.mark.unit
def test_chunk_sections_prepends_title_and_orders(monkeypatch):
    from ragnostic.db.schema import DocumentSection, SectionContent

    section = DocumentSection(
        section_id="SEC_1",
        doc_id="DOC_1",
        level=1,
        sequence_order=0,
        content=SectionContent(
            section_id="SEC_1",
            title="Introduction",
            content="alpha beta gamma delta",
        ),
    )
    creates = chunk_sections("DOC_1", [section], chunk_words=250, overlap_words=50)
    assert len(creates) == 1
    assert creates[0].text.startswith("Introduction")
    assert creates[0].doc_id == "DOC_1"
    assert creates[0].section_id == "SEC_1"
    assert creates[0].sequence_order == 0


@pytest.mark.unit
def test_chunk_sections_skips_empty_content():
    from ragnostic.db.schema import DocumentSection, SectionContent

    section = DocumentSection(
        section_id="SEC_1",
        doc_id="DOC_1",
        level=1,
        sequence_order=0,
        content=SectionContent(section_id="SEC_1", title="Empty", content="   "),
    )
    assert chunk_sections("DOC_1", [section]) == []
