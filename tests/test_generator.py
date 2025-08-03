"""Test LLMS.txt generator."""

from pathlib import Path

import pytest

from notion_to_llms_txt.generator import LLMSTxtGenerator
from notion_to_llms_txt.models import NotionExport, NotionPage


class TestLLMSTxtGenerator:
    
    @pytest.fixture(autouse=True)
    def setup_generator(self):
        self.generator = LLMSTxtGenerator()
        
        # Create test pages with different characteristics
        self.test_pages = [
            NotionPage(
                title="Large Project",
                page_id="abc123def456789012345678901234",
                file_path=Path("/test/large.md"),
                category="Projects",
                size_bytes=3000
            ),
            NotionPage(
                title="Small Task",
                page_id="def456789012345678901234567890",
                file_path=Path("/test/small.md"),
                category="Projects", 
                size_bytes=500
            ),
            NotionPage(
                title="Documentation",
                page_id="ghi789012345678901234567890ab",
                file_path=Path("/test/docs.md"),
                category="Documentation",
                size_bytes=2000
            )
        ]
        
        self.test_export = NotionExport(
            pages=self.test_pages,
            categories=["Projects", "Documentation"]
        )
    
    def test_generate_basic_structure(self):
        content = self.generator.generate(self.test_export)
        
        assert "# Notion Workspace" in content
        assert "> Notion page structure and links overview" in content
        assert "## Projects" in content
        assert "## Documentation" in content
    
    def test_page_ordering_by_priority(self):
        content = self.generator.generate(self.test_export)
        
        # Within Projects category, Large Project (3000 bytes) should come before Small Task (500 bytes)
        projects_section = content.split("## Projects")[1].split("## Documentation")[0]
        large_pos = projects_section.find("Large Project")
        small_pos = projects_section.find("Small Task")
        
        assert large_pos < small_pos
    
    def test_url_generation(self):
        content = self.generator.generate(self.test_export)
        
        assert "https://notion.so/abc123def456789012345678901234" in content
        assert "https://notion.so/def456789012345678901234567890" in content
        assert "https://notion.so/ghi789012345678901234567890ab" in content
    
    def test_save_to_file(self, tmp_path):
        output_file = tmp_path / "test_output.txt"
        
        self.generator.save_to_file(self.test_export, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "# Notion Workspace" in content
        assert "Large Project" in content
    
    def test_get_summary_stats(self):
        stats = self.generator.get_summary_stats(self.test_export)
        
        assert stats["total_pages"] == 3
        assert stats["total_categories"] == 2
        assert stats["largest_page_size"] == 3000
        assert set(stats["categories"]) == {"Projects", "Documentation"}