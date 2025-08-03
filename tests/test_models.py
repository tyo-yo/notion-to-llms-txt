"""Test data models."""

from pathlib import Path

import pytest

from notion_to_llms_txt.models import NotionExport, NotionPage


class TestNotionPage:
    """Test NotionPage model."""
    
    def test_notion_url_generation(self):
        """Test URL generation without workspace parameter."""
        page = NotionPage(
            title="Test Page",
            page_id="abc123def456789012345678901234",
            file_path=Path("/test/path.md"),
            category="Test Category",
            size_bytes=1000
        )
        
        expected_url = "https://notion.so/abc123def456789012345678901234"
        assert page.notion_url() == expected_url
    
    def test_priority_score(self):
        """Test priority score calculation based on file size."""
        page = NotionPage(
            title="Test Page",
            page_id="abc123def456789012345678901234", 
            file_path=Path("/test/path.md"),
            category="Test Category",
            size_bytes=2500
        )
        
        assert page.priority_score == 2500


class TestNotionExport:
    """Test NotionExport model."""
    
    def test_get_pages_by_category(self):
        """Test filtering pages by category."""
        pages = [
            NotionPage(
                title="Page 1",
                page_id="abc123def456789012345678901234",
                file_path=Path("/test/page1.md"), 
                category="Projects",
                size_bytes=1000
            ),
            NotionPage(
                title="Page 2", 
                page_id="def456789012345678901234567890",
                file_path=Path("/test/page2.md"),
                category="Documentation", 
                size_bytes=2000
            ),
            NotionPage(
                title="Page 3",
                page_id="ghi789012345678901234567890ab", 
                file_path=Path("/test/page3.md"),
                category="Projects",
                size_bytes=1500
            ),
        ]
        
        export = NotionExport(pages=pages, categories=["Projects", "Documentation"])
        
        projects_pages = export.get_pages_by_category("Projects")
        assert len(projects_pages) == 2
        
        # Should be sorted by priority (file size) descending
        assert projects_pages[0].title == "Page 3"  # 1500 bytes
        assert projects_pages[1].title == "Page 1"  # 1000 bytes
    
    def test_get_top_pages(self):
        """Test getting top pages across all categories."""
        pages = [
            NotionPage(
                title="Small Page",
                page_id="abc123def456789012345678901234",
                file_path=Path("/test/small.md"),
                category="Test",
                size_bytes=500
            ),
            NotionPage(
                title="Large Page", 
                page_id="def456789012345678901234567890",
                file_path=Path("/test/large.md"),
                category="Test",
                size_bytes=3000
            ),
            NotionPage(
                title="Medium Page",
                page_id="ghi789012345678901234567890ab",
                file_path=Path("/test/medium.md"), 
                category="Test",
                size_bytes=1500
            ),
        ]
        
        export = NotionExport(pages=pages, categories=["Test"])
        
        top_pages = export.get_top_pages(limit=2)
        assert len(top_pages) == 2
        assert top_pages[0].title == "Large Page"   # 3000 bytes
        assert top_pages[1].title == "Medium Page"  # 1500 bytes