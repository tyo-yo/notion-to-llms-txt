"""Generator for LLMS.txt format output."""

from pathlib import Path
from typing import List

from .models import NotionExport, NotionPage


class LLMSTxtGenerator:
    """Generates LLMS.txt format from Notion export data."""
    
    def generate(self, export: NotionExport) -> str:
        """Generate LLMS.txt content from export data."""
        lines = []
        
        # Header
        lines.append("# Notion Workspace")
        lines.append("")
        lines.append("> Notion page structure and links overview")
        lines.append("")
        
        # Group pages by category and generate sections
        for category in export.categories:
            category_pages = export.get_pages_by_category(category)
            if category_pages:
                lines.append(f"## {category}")
                
                # Add pages sorted by priority (file size)
                for page in category_pages:
                    url = page.notion_url()
                    line = f"- [{page.title}]({url}): {page.content_snippet}"
                    lines.append(line)
                
                lines.append("")
        
        return "\n".join(lines)
    
    def save_to_file(self, export: NotionExport, output_path: Path) -> None:
        """Generate and save LLMS.txt to file."""
        content = self.generate(export)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def get_summary_stats(self, export: NotionExport) -> dict:
        """Get summary statistics about the export."""
        content = self.generate(export)
        return {
            "total_pages": len(export.pages),
            "total_categories": len(export.categories),
            "largest_page_size": max(page.size_bytes for page in export.pages) if export.pages else 0,
            "categories": export.categories,
            "output_chars": len(content),
            "output_lines": len(content.splitlines()),
        }