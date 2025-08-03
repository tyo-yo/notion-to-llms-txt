# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Filtering algorithm for empty and low-value pages
- Improved page descriptions with content snippets
- Test framework with pytest
- GitHub Actions CI/CD pipeline

### Changed
- URL construction simplified (removed workspace parameter)

### Fixed
- Documentation updates in CLAUDE.md

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