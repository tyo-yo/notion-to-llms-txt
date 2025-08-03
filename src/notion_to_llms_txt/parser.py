"""Parser for Notion export directories."""

import fnmatch
import re
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from .models import NotionExport, NotionPage


@lru_cache(maxsize=1000)
def _read_file_content_cached(file_path_str: str) -> str | None:
    """Read file content with LRU cache to avoid duplicate reads."""
    try:
        return Path(file_path_str).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


class NotionExportParser:
    """Parses Notion export directory structure."""

    # Regex pattern for extracting 32-character hex page IDs
    PAGE_ID_PATTERN = re.compile(r"[a-f0-9]{32}")

    def __init__(
        self,
        export_path: Path,
        min_file_size: int = 200,
        min_content_lines: int = 3,
        exclude_untitled: bool = True,
        exclude_link_only: bool = True,
        link_only_threshold: float = 0.8,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        content_snippet_length: int = 32,
    ):
        """Initialize parser with export directory path and filtering options."""
        self.export_path = export_path
        self.min_file_size = min_file_size
        self.min_content_lines = min_content_lines
        self.exclude_untitled = exclude_untitled
        self.exclude_link_only = exclude_link_only
        self.link_only_threshold = link_only_threshold
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.content_snippet_length = content_snippet_length

    def parse(self) -> NotionExport:
        """Parse the entire export and return structured data."""
        pages = self._scan_pages()
        categories = self._extract_categories(pages)

        return NotionExport(pages=pages, categories=categories)

    def _scan_pages(self) -> List[NotionPage]:
        """Scan export directory for all .md files and extract page info."""
        pages = []

        # Find all .md files recursively
        for md_file in self.export_path.rglob("*.md"):
            if self._should_include_page(md_file):
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

        # Extract content snippet using cached file reading
        content_snippet = self._extract_content_snippet(file_path)

        return NotionPage(
            title=title,
            page_id=page_id,
            file_path=file_path,
            category=category,
            size_bytes=size_bytes,
            content_snippet=content_snippet,
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
        title = re.sub(r"^[\s\-_]+|[\s\-_]+$", "", title)

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
                clean_part = re.sub(r"^[\s\-_]+|[\s\-_]+$", "", clean_part)

            if clean_part:
                clean_parts.append(clean_part)

        # Join with " - " to create hierarchical category
        return " - ".join(clean_parts) if clean_parts else "Uncategorized"

    def _extract_categories(self, pages: List[NotionPage]) -> List[str]:
        """Extract unique categories from pages."""
        categories = set(page.category for page in pages)
        return sorted(list(categories))

    def _should_include_page(self, file_path: Path) -> bool:
        """Check if page should be included based on filtering criteria."""
        # Check file size
        if file_path.stat().st_size < self.min_file_size:
            return False

        # Check title for "Untitled"
        if self.exclude_untitled and "Untitled" in file_path.stem:
            return False

        # Check path-based patterns
        if not self._matches_path_patterns(file_path):
            return False

        # Check if page has enough content after cleaning
        content = _read_file_content_cached(str(file_path))
        if content is None:
            return False

        cleaned_lines = self._clean_content_lines(content)
        return len(cleaned_lines) >= self.min_content_lines

    def _clean_content_lines(self, content: str) -> List[str]:
        """Clean content by filtering out unwanted lines."""
        lines = content.strip().split("\n")
        cleaned_lines = []

        for line in lines:
            if self._should_keep_line(line):
                cleaned_lines.append(line.strip())

        return cleaned_lines

    def _should_keep_line(self, line: str) -> bool:
        """Check if line should be kept based on filtering criteria."""
        line = line.strip()

        # Skip empty lines
        if not line:
            return False

        # Skip headers (markdown titles)
        if line.startswith("#"):
            return False


        # Skip link-only lines if exclude_link_only is enabled
        if self.exclude_link_only and self._is_link_only_line(line):
            return False

        return True

    def _is_link_only_line(self, line: str) -> bool:
        """Check if line contains only links."""
        line = line.strip()

        # Patterns for link-only lines
        patterns = [
            r"^\s*[-*]\s*\[.*?\]\(.*?\)\s*$",  # - [text](url)
            r"^\s*\[.*?\]\(.*?\)\s*$",  # [text](url)
            r"^\s*https?://\S+\s*$",  # bare URL
        ]

        return any(re.match(pattern, line) for pattern in patterns)

    def _extract_content_snippet(self, file_path: Path) -> str:
        """Extract content snippet from file using cached reading."""
        content = _read_file_content_cached(str(file_path))
        if not content:
            return ""

        # Get cleaned content lines and filter out Notion properties for snippet
        cleaned_lines = self._clean_content_lines(content)
        # Additional filtering for snippet: remove Notion database properties
        snippet_lines = [line for line in cleaned_lines if ': ' not in line]
        if not snippet_lines:
            return ""

        # Join lines with spaces and truncate to desired length
        full_text = " ".join(snippet_lines).strip()

        if len(full_text) <= self.content_snippet_length:
            return full_text
        else:
            return full_text[: self.content_snippet_length].strip() + "..."

    def _get_full_path(self, file_path: Path) -> str:
        """Generate full path string: category/page_title"""
        category = self._determine_category(file_path)

        # Extract page title from filename
        page_id = self._extract_page_id(file_path.stem)
        title = self._extract_title(file_path.stem, page_id)

        # If category is "Root", just use the title
        if category == "Root":
            return title

        # Otherwise combine category and title
        return f"{category}/{title}"

    def _matches_path_patterns(self, file_path: Path) -> bool:
        """Check if file path matches include/exclude patterns."""
        full_path = self._get_full_path(file_path)

        # If include patterns are specified, path must match at least one
        if self.include_patterns:
            if not any(fnmatch.fnmatch(full_path, pattern) for pattern in self.include_patterns):
                return False

        # If exclude patterns are specified, path must not match any
        if self.exclude_patterns:
            if any(fnmatch.fnmatch(full_path, pattern) for pattern in self.exclude_patterns):
                return False

        return True
