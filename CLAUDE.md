# CLAUDE.md - Development Context

## Project Overview

**notion-to-llms-txt** is a CLI tool that converts Notion workspace exports into LLMS.txt format for AI agent consumption.

### Problem Statement
AI agents (Claude, ChatGPT, coding assistants) struggle to efficiently navigate large Notion workspaces without understanding the documentation structure. This leads to ineffective searches and missed relevant information.

### Solution
Generate a structured "table of contents" in LLMS.txt format that gives AI agents instant workspace overview with proper prioritization and direct links.

## Technical Architecture

### Core Components

```
src/notion_to_llms_txt/
├── main.py          # Typer CLI entry point
├── parser.py        # Notion export parsing logic
├── generator.py     # LLMS.txt generation
└── models.py        # Data structures
```

### Key Algorithms

1. **Page ID Extraction**: Regex `[a-f0-9]{32}` from filenames
2. **Priority Scoring**: File size (bytes) determines importance
3. **URL Construction**: `https://notion.so/{page_id}`
4. **Categorization**: Group by top-level directory structure

### Data Flow

```
Notion Export (ZIP) → Parser → Page Models → Generator → LLMS.txt
```

## Implementation Details

### Page Model
```python
@dataclass
class NotionPage:
    title: str
    page_id: str
    file_path: Path
    category: str
    size_bytes: int

    @property
    def notion_url(self) -> str:
        return f"https://notion.so/{self.page_id}"
```

### Priority Algorithm
- **Primary**: File size (larger = more important content)
- **Future**: Could add backlink counting, child page count

### Output Format
```markdown
# Notion Workspace

> Notion page structure and links overview

## {Category}
- [{Title}]({URL}): {Title}
```

## Development Workflow

### Setup
```bash
git clone https://github.com/tyo-yo/notion-to-llms-txt
cd notion-to-llms-txt
uv sync
```

### Testing
```bash
uv run pytest
uv run ruff check
uv run ruff format
```

### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create GitHub release
4. GitHub Actions automatically publishes to PyPI

## Technical Decisions

### Why UV?
- Modern Python package management
- Fast dependency resolution
- Built-in tool installation (`uv tool install`)

### Why Typer?
- Rich CLI experience with minimal code
- Automatic help generation
- Type-safe argument parsing

### Why File Size Priority?
- Simple and effective heuristic
- Available without complex analysis
- Larger pages typically contain more important content

## Future Enhancements

### Planned Features
- Backlink analysis for better prioritization
- Multiple workspace support
- Custom categorization rules
- LLM-powered page summarization (via LiteLLM)

### Potential Improvements
- Incremental updates (only process changed files)
- Configuration file support
- Multiple output formats (JSON, YAML)
- Integration with Notion API for live updates

## Testing Strategy

### Test Data
- `tests/fixtures/` contains sample Notion exports
- Cover edge cases: empty pages, special characters, deep hierarchies

### Test Coverage
- Page ID extraction accuracy
- URL construction correctness
- LLMS.txt format compliance
- CLI argument handling

## Deployment

### PyPI Publication
- Automated via GitHub Actions on release
- Semantic versioning
- Wheel + source distribution

### Installation Methods
```bash
# Recommended
uv tool install notion-to-llms-txt

# Alternative
pip install notion-to-llms-txt
```

## Contributing

### Code Style
- Ruff for formatting and linting
- Type hints required
- Docstrings for public functions

### Pull Request Process
1. Create feature branch from `main`
2. Add tests for new functionality
3. Ensure CI passes (tests + formatting)
4. Submit PR with clear description

## Usage Context

This tool is designed for:
- **Knowledge workers** with large Notion workspaces
- **AI agent users** who want efficient documentation access
- **Teams** sharing workspace structure with AI assistants
- **Developers** building AI-powered workflow tools

Generated LLMS.txt files should be:
- Shared with AI agents before workspace-related conversations
- Embedded in Notion pages for easy access
- Updated regularly as workspace structure evolves

## Current Development Tasks

### 🚨 High Priority (Immediate)

1. **Add Test Framework**
   - pytest configuration and test directory structure
   - Core functionality test cases (parser, generator, models)
   - Test fixtures (sample Notion exports)

2. **GitHub Actions CI/CD**
   - Automated testing and linting
   - Automated PyPI publishing on release
   - Python 3.11-3.13 support

3. **Create CHANGELOG.md**
   - Version tracking and release notes
   - Semantic versioning

4. **Fix README Issues**
   - Accurate Notion export instructions
   - Improved UV installation guide
   - Add Notion MCP usage recommendations

### 🔧 Core Algorithm Improvements

5. **Implement Filtering Algorithm**
   - Filter empty pages (1-2 lines only)
   - Filter "Untitled" pages (Notion defaults)
   - Filter link-only pages (no substantial content)
   - Analyze actual markdown files for better filtering

6. **Improve Descriptions**
   - Remove redundant title duplication
   - Display actual page content snippets (Google search result style)
   - Extract meaningful text from first few lines

### 🎯 Current Issues

7. **Main Problem Analysis**
   - Current notion-llms.txt is too long (50k lines)
   - Need Notion-specific page structure understanding
   - Proper handling of Notion database/table features

## User Requirements Summary

- **Main Issue**: Generated LLMS.txt is too long (50k lines)
- **Solution Needed**: Filtering algorithm to exclude low-value pages
- **Specific Exclusion Targets**:
  - Near-empty pages (1-2 lines only)
  - Untitled pages (Notion defaults)
  - Link-only pages (no substantial content)
- **Improvements Wanted**: Remove title duplication, show actual page content snippets
- **Future Consideration**: Proper handling of Notion database/table features

## Working Session Notes

**Last Updated**: 2025-08-04
**Current Status**: MVP completed, filtering and quality improvement phase
**Test Environment**: 49,410 pages, 3,997 categories (actual export)
