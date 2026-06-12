"""Tests for markdown section splitting."""
import pytest

from ragnostic.extraction.markdown_sections import split_markdown_sections


@pytest.mark.unit
def test_no_headers_yields_single_section():
    sections = split_markdown_sections([("just some body text", 1)], default_title="Body")
    assert len(sections) == 1
    assert sections[0].title == "Body"
    assert "body text" in sections[0].text


@pytest.mark.unit
def test_headers_create_sections_with_levels():
    md = "# Intro\nintro text\n## Methods\nmethod text\n# Results\nresult text"
    sections = split_markdown_sections([(md, 1)])
    titles = [(s.title, s.level) for s in sections]
    assert titles == [("Intro", 1), ("Methods", 2), ("Results", 1)]
    assert "intro text" in sections[0].text


@pytest.mark.unit
def test_leading_content_before_first_header():
    md = "preamble line\n# Real Header\nbody"
    sections = split_markdown_sections([(md, 1)], default_title="Preamble")
    assert sections[0].title == "Preamble"
    assert "preamble line" in sections[0].text
    assert sections[1].title == "Real Header"


@pytest.mark.unit
def test_page_numbers_tracked_across_pages():
    sections = split_markdown_sections(
        [("# A\ncontent a", 1), ("# B\ncontent b", 2)]
    )
    assert sections[0].page_start == 1
    assert sections[1].page_start == 2
