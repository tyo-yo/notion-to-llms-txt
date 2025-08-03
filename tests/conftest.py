"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_export_path() -> Path:
    """Return path to sample Notion export for testing."""
    return Path(__file__).parent / "fixtures" / "sample_export"


@pytest.fixture
def sample_pages_info() -> list[dict]:
    """Return expected information about sample pages.

    should_include flag is based on filtering settings:
    min_content_chars=50, min_content_lines=2, exclude_untitled=True, exclude_link_only=True
    """
    return [
        {
            "filename": "AI Development Guidelines abc123def456789012345678901234ab.md",
            "page_id": "abc123def456789012345678901234ab",
            "title": "AI Development Guidelines",
            "category": "Projects",
            "should_include": True,
        },
        {
            "filename": "Empty Page def456789012345678901234567890ab.md",
            "page_id": "def456789012345678901234567890ab",
            "title": "Empty Page",
            "category": "Projects",
            "should_include": False,
        },
        {
            "filename": "Untitled fed789012345678901234567890abcde.md",
            "page_id": "fed789012345678901234567890abcde",
            "title": "Untitled",
            "category": "Projects",
            "should_include": False,
        },
        {
            "filename": "Links Collection abc012345678901234567890abcdef12.md",
            "page_id": "abc012345678901234567890abcdef12",
            "title": "Links Collection",
            "category": "Projects",
            "should_include": False,
        },
        {
            "filename": "Setup Guide def345678901234567890abcdef12345.md",
            "page_id": "def345678901234567890abcdef12345",
            "title": "Setup Guide",
            "category": "Documentation",
            "should_include": True,
        },
        {
            "filename": "Meeting Notes abc56789012345678901234567890abc.md",
            "page_id": "abc56789012345678901234567890abc",
            "title": "Meeting Notes",
            "category": "Team",
            "should_include": True,
        },
        {
            "filename": "Database Page 7d79223f342f9124d0ca375d71f877a7.md",
            "page_id": "7d79223f342f9124d0ca375d71f877a7",
            "title": "Database Page",
            "category": "Projects",
            "should_include": True,
        },
    ]
