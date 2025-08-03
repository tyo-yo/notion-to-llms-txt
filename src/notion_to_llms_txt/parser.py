"""Parser for Notion export directories."""

import re
from pathlib import Path
from typing import List

from .models import NotionExport, NotionPage


class NotionExportParser:
    """Parses Notion export directory structure."""
    
    # Regex pattern for extracting 32-character hex page IDs
    PAGE_ID_PATTERN = re.compile(r'[a-f0-9]{32}')
    
    def __init__(self, export_path: Path):
        """Initialize parser with export directory path."""
        self.export_path = export_path
    
    def parse(self) -> NotionExport:
        """Parse the entire export and return structured data."""
        pages = self._scan_pages()
        categories = self._extract_categories(pages)
        
        return NotionExport(
            pages=pages,
            categories=categories
        )
    
    def _scan_pages(self) -> List[NotionPage]:
        """Scan export directory for all .md files and extract page info."""
        pages = []
        
        # Find all .md files recursively
        for md_file in self.export_path.rglob("*.md"):
            page = self._parse_page_file(md_file)
            pages.append(page)
        
        return pages
    
    def _parse_page_file(self, file_path: Path) -> NotionPage:
        """Parse a single .md file and extract page information."""
        # Extract page ID from filename
        page_id = self._extract_page_id(file_path.stem)
        
        # Extract title (remove page ID from filename)
        title = self._extract_title(file_path.stem, page_id)
        
        # Get file size
        size_bytes = file_path.stat().st_size
        
        # Determine category from directory structure
        category = self._determine_category(file_path)
        
        return NotionPage(
            title=title,
            page_id=page_id,
            file_path=file_path,
            category=category,
            size_bytes=size_bytes
        )
    
    def _extract_page_id(self, filename: str) -> str:
        """Extract 32-character page ID from filename."""
        match = self.PAGE_ID_PATTERN.search(filename)
        if not match:
            raise ValueError(f"No page ID found in filename: {filename}")
        return match.group(0)
    
    def _extract_title(self, filename: str, page_id: str) -> str:
        """Extract clean title by removing page ID from filename."""
        # Remove page ID and clean up the title
        title = filename.replace(page_id, "").strip()
        
        # Remove trailing/leading spaces and common separators
        title = re.sub(r'^[\s\-_]+|[\s\-_]+$', '', title)
        
        # If title is empty after cleaning, use filename without extension
        if not title:
            title = filename
        
        return title
    
    def _determine_category(self, file_path: Path) -> str:
        """Determine hierarchical category based on directory structure."""
        # Get relative path from export root
        relative_path = file_path.relative_to(self.export_path)
        
        # Get all directory parts (excluding the file itself)
        dir_parts = relative_path.parts[:-1]
        
        if not dir_parts:
            return "Root"
        
        # Clean each directory part by removing page IDs
        clean_parts = []
        for part in dir_parts:
            clean_part = part
            page_id_match = self.PAGE_ID_PATTERN.search(part)
            if page_id_match:
                clean_part = part.replace(page_id_match.group(0), "").strip()
                clean_part = re.sub(r'^[\s\-_]+|[\s\-_]+$', '', clean_part)
            
            if clean_part:
                clean_parts.append(clean_part)
        
        # Join with " - " to create hierarchical category
        return " - ".join(clean_parts) if clean_parts else "Uncategorized"
    
    def _extract_categories(self, pages: List[NotionPage]) -> List[str]:
        """Extract unique categories from pages."""
        categories = set(page.category for page in pages)
        return sorted(list(categories))