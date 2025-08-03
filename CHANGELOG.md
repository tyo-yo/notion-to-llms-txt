# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-08-03

### Added
- Smart filtering algorithm for empty and low-value pages
- Character-based filtering instead of file size for more accurate content assessment  
- Content snippets replacing redundant title duplication
- Multilingual support for Notion database properties (Japanese, Chinese, Korean, Arabic)
- Path-based include/exclude pattern filtering with glob support
- Comprehensive test suite with pytest and 95% coverage
- GitHub Actions CI/CD pipeline with automated PyPI publishing
- Improved README with accurate Notion export instructions
- Notion MCP integration recommendations

### Changed
- CLI parameter `--min-size` renamed to `--min-chars` for clarity
- Notion property filtering now uses smart regex pattern detection
- File size priority replaced with content-based filtering

### Fixed
- URL construction no longer requires non-existent workspace parameter
- Corrected Notion export instructions for both admin and user workflows

## [0.1.0] - 2025-08-03

### Added
- Initial CLI tool implementation
- Notion export parsing with regex-based page ID extraction
- LLMS.txt format generation
- Hierarchical categorization based on directory structure
- File size-based prioritization algorithm
- Rich console output with progress indicators
- Pydantic v2 data models
- UV package management support
- Typer CLI framework integration
- Apache 2.0 license
- Comprehensive README and documentation

### Technical Details
- Support for Python 3.11-3.13
- Processes large exports (tested with 49,410 pages, 3,997 categories)
- Preserves Notion workspace hierarchy
- Generates direct Notion page links