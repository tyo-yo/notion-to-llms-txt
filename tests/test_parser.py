"""Test Notion export parser."""

from pathlib import Path

import pytest

from notion_to_llms_txt.parser import NotionExportParser


class TestNotionExportParser:
    """Test NotionExportParser functionality."""

    @pytest.fixture(autouse=True)
    def setup_parser(self, sample_export_path: Path):
        self.parser = NotionExportParser(sample_export_path)
        self.export_path = sample_export_path

    def test_page_id_extraction(self):
        valid_id = self.parser._extract_page_id("AI Development Guidelines abc123def456789012345678901234ab")
        assert valid_id == "abc123def456789012345678901234ab"

        valid_id2 = self.parser._extract_page_id("Setup Guide def345678901234567890abcdef12345")
        assert valid_id2 == "def345678901234567890abcdef12345"

    def test_page_id_extraction_failure(self):
        with pytest.raises(ValueError, match="No page ID found"):
            self.parser._extract_page_id("No ID Here")

    def test_title_extraction(self):
        title = self.parser._extract_title(
            "AI Development Guidelines abc123def456789012345678901234ab", "abc123def456789012345678901234ab"
        )
        assert title == "AI Development Guidelines"

        title2 = self.parser._extract_title(
            "Meeting Notes - 2025-08-04 abc56789012345678901234567890abc", "abc56789012345678901234567890abc"
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

        assert len(export.pages) == len(sample_pages_info)

        expected_categories = {"Projects", "Documentation", "Team"}
        assert set(export.categories) == expected_categories

        page_by_id = {page.page_id: page for page in export.pages}

        for expected_page in sample_pages_info:
            page_id = expected_page["page_id"]
            assert page_id in page_by_id

            page = page_by_id[page_id]
            assert page.title == expected_page["title"]
            assert page.category == expected_page["category"]
            assert page.size_bytes > 0

    def test_scan_pages_file_discovery(self):
        pages = self.parser._scan_pages()

        # Based on our test fixtures - need to match actual fixture count
        assert len(pages) == 6

        # Notion page IDs are always 32 character hex strings
        for page in pages:
            assert len(page.page_id) == 32
            assert page.size_bytes > 0
