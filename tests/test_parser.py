"""Test Notion export parser."""

from pathlib import Path

import pytest

from notion_to_llms_txt.parser import NotionExportParser


class TestNotionExportParser:
    """Test NotionExportParser functionality."""

    @pytest.fixture(autouse=True)
    def setup_parser(self, sample_export_path: Path):
        # Use explicit parameters to avoid dependency on changing defaults
        self.parser = NotionExportParser(
            sample_export_path,
            min_file_size=50,
            min_content_lines=2,
            exclude_untitled=True,
            exclude_link_only=True,
            include_patterns=None,
            exclude_patterns=None,
        )
        self.export_path = sample_export_path

    def test_page_id_extraction(self):
        valid_id = self.parser._extract_page_id(
            "AI Development Guidelines abc123def456789012345678901234ab"
        )
        assert valid_id == "abc123def456789012345678901234ab"

        valid_id2 = self.parser._extract_page_id(
            "Setup Guide def345678901234567890abcdef12345"
        )
        assert valid_id2 == "def345678901234567890abcdef12345"

    def test_page_id_extraction_failure(self):
        with pytest.raises(ValueError, match="No page ID found"):
            self.parser._extract_page_id("No ID Here")

    def test_title_extraction(self):
        title = self.parser._extract_title(
            "AI Development Guidelines abc123def456789012345678901234ab",
            "abc123def456789012345678901234ab",
        )
        assert title == "AI Development Guidelines"

        title2 = self.parser._extract_title(
            "Meeting Notes - 2025-08-04 abc56789012345678901234567890abc",
            "abc56789012345678901234567890abc",
        )
        assert title2 == "Meeting Notes - 2025-08-04"

    def test_category_determination(self):
        projects_file = self.export_path / "Projects" / "test.md"
        category = self.parser._determine_category(projects_file)
        assert category == "Projects"

        root_file = self.export_path / "test.md"
        category = self.parser._determine_category(root_file)
        assert category == "Root"

    def test_full_parse(self, sample_pages_info: list[dict]):
        export = self.parser.parse()

        # Only pages with should_include=True should be included after filtering
        expected_included = [
            page for page in sample_pages_info if page["should_include"]
        ]
        assert len(export.pages) == len(expected_included)

        expected_categories = {"Projects", "Documentation", "Team"}
        assert set(export.categories) == expected_categories

        page_by_id = {page.page_id: page for page in export.pages}

        # Only check pages that should be included
        for expected_page in expected_included:
            page_id = expected_page["page_id"]
            assert page_id in page_by_id

            page = page_by_id[page_id]
            assert page.title == expected_page["title"]
            assert page.category == expected_page["category"]
            assert page.size_bytes > 0

    def test_scan_pages_file_discovery(self):
        pages = self.parser._scan_pages()

        # After filtering, only 3 pages should remain (excluding Empty, Untitled, Links-only)
        assert len(pages) == 3

        # Notion page IDs are always 32 character hex strings
        for page in pages:
            assert len(page.page_id) == 32
            assert page.size_bytes > 0

    def test_filtering_by_file_size(self):
        # Test with 1000 byte threshold - only Setup Guide (1260 bytes) should remain
        # Other files: AI Guidelines (680), Meeting Notes (669), Links Collection (150),
        # Untitled (38), Empty Page (12) are all under 1000 bytes
        parser_large_files = NotionExportParser(
            self.export_path,
            min_file_size=1000,
            exclude_untitled=False,
            exclude_link_only=False,
        )
        large_pages = parser_large_files._scan_pages()

        # Should only include 1 page: Setup Guide (1260 bytes)
        assert len(large_pages) == 1
        assert all(page.size_bytes >= 1000 for page in large_pages)
        assert large_pages[0].title == "Setup Guide"

    def test_filtering_untitled_pages(self):
        # Test with exclude_untitled=False - should include Untitled page
        parser_include_untitled = NotionExportParser(
            self.export_path, exclude_untitled=False, min_file_size=30
        )
        pages_with_untitled = parser_include_untitled._scan_pages()

        # Should include the Untitled page (38 bytes, above min_file_size=30)
        untitled_pages = [p for p in pages_with_untitled if "Untitled" in p.title]
        assert len(untitled_pages) == 1
        assert untitled_pages[0].title == "Untitled"

        # Test with exclude_untitled=True (default) - should exclude Untitled page
        parser_exclude_untitled = NotionExportParser(
            self.export_path, exclude_untitled=True, min_file_size=30
        )
        pages_without_untitled = parser_exclude_untitled._scan_pages()

        # Should not include any Untitled pages
        untitled_pages_excluded = [
            p for p in pages_without_untitled if "Untitled" in p.title
        ]
        assert len(untitled_pages_excluded) == 0

    def test_content_line_cleaning(self):
        # Test content cleaning functionality
        sample_content = """# Title

This is real content.
- [Link only](http://example.com)
Another real line.

"""
        cleaned_lines = self.parser._clean_content_lines(sample_content)

        # Should exclude header and empty lines, include real content
        assert "This is real content." in cleaned_lines
        assert "Another real line." in cleaned_lines
        # Link-only line should be excluded if exclude_link_only=True
        assert "- [Link only](http://example.com)" not in cleaned_lines

    def test_link_only_detection(self):
        test_cases = [
            ("- [Test](http://example.com)", True),  # Bullet point link
            ("[Test](http://example.com)", True),  # Plain link
            ("http://example.com", True),  # Bare URL
            ("This is text with [link](url)", False),  # Mixed content
            ("Regular text content", False),  # Plain text
        ]

        for line, expected in test_cases:
            result = self.parser._is_link_only_line(line)
            assert result == expected, f"Failed for line: {line}"

    def test_path_pattern_filtering(self):
        # Test include patterns
        parser_include = NotionExportParser(
            self.export_path,
            min_file_size=50,
            min_content_lines=2,
            exclude_untitled=False,
            exclude_link_only=False,
            include_patterns=["Projects/*"],
            exclude_patterns=None,
        )
        included_pages = parser_include._scan_pages()

        # Should only include pages from Projects category
        for page in included_pages:
            assert page.category == "Projects"

        # Test exclude patterns
        parser_exclude = NotionExportParser(
            self.export_path,
            min_file_size=50,
            min_content_lines=2,
            exclude_untitled=False,
            exclude_link_only=False,
            include_patterns=None,
            exclude_patterns=["Projects/Untitled*"],
        )
        excluded_pages = parser_exclude._scan_pages()

        # Should not include any Untitled pages from Projects
        untitled_projects = [
            p
            for p in excluded_pages
            if p.category == "Projects" and "Untitled" in p.title
        ]
        assert len(untitled_projects) == 0

    def test_full_path_generation(self):
        # Test full path generation
        projects_file = (
            self.export_path
            / "Projects"
            / "AI Development Guidelines abc123def456789012345678901234ab.md"
        )
        full_path = self.parser._get_full_path(projects_file)
        assert full_path == "Projects/AI Development Guidelines"

        # Test root file path
        root_file = self.export_path / "test.md"
        # Create a mock file path for testing
        from unittest.mock import patch

        with patch.object(
            self.parser,
            "_extract_page_id",
            return_value="abc123456789012345678901234567890",
        ):
            with patch.object(self.parser, "_extract_title", return_value="Test Page"):
                full_path = self.parser._get_full_path(root_file)
                assert full_path == "Test Page"
