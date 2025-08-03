"""Data models for Notion pages and exports."""

from pathlib import Path

from pydantic import BaseModel, computed_field


class NotionPage(BaseModel):
    """Represents a single Notion page from export."""

    title: str
    page_id: str
    file_path: Path
    category: str
    size_bytes: int
    content_snippet: str

    def notion_url(self) -> str:
        """Generate Notion URL for this page."""
        return f"https://notion.so/{self.page_id}"

    @computed_field
    @property
    def priority_score(self) -> int:
        """Calculate priority score (higher = more important)."""
        return self.size_bytes


class NotionExport(BaseModel):
    """Represents the entire Notion export structure."""

    pages: list[NotionPage]
    categories: list[str]

    def get_pages_by_category(self, category: str) -> list[NotionPage]:
        """Get all pages in a specific category, sorted by priority."""
        category_pages = [p for p in self.pages if p.category == category]
        return sorted(category_pages, key=lambda p: p.priority_score, reverse=True)

    def get_top_pages(self, limit: int = 100) -> list[NotionPage]:
        """Get top N pages across all categories by priority."""
        return sorted(self.pages, key=lambda p: p.priority_score, reverse=True)[:limit]
