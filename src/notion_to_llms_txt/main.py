"""Main CLI entry point for notion-to-llms-txt."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(
    name="notion-to-llms-txt",
    help="Convert Notion exports to LLMS.txt format for AI agents",
    no_args_is_help=True,
)
console = Console()


@app.command()
def main(
    export_path: Path = typer.Argument(
        ...,
        help="Path to extracted Notion export directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: notion-llms.txt)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    min_content_chars: int = typer.Option(
        100,
        "--min-chars",
        help="Minimum content characters to include after cleaning (default: 100)",
    ),
    min_content_lines: int = typer.Option(
        3,
        "--min-lines", 
        help="Minimum content lines to include (default: 3)",
    ),
    exclude_untitled: bool = typer.Option(
        True,
        "--exclude-untitled/--include-untitled",
        help="Exclude pages with 'Untitled' in title (default: True)",
    ),
    exclude_link_only: bool = typer.Option(
        True,
        "--exclude-link-only/--include-link-only",
        help="Exclude pages containing only links (default: True)",
    ),
    include_patterns: Optional[str] = typer.Option(
        None,
        "--include",
        help="Include only paths matching these glob patterns (comma-separated, e.g., 'Projects/*,Team/Meeting*')",
    ),
    exclude_patterns: Optional[str] = typer.Option(
        None,
        "--exclude",
        help="Exclude paths matching these glob patterns (comma-separated, e.g., 'Archive/*,Draft*')",
    ),
    content_snippet_length: int = typer.Option(
        32,
        "--snippet-length",
        help="Length of content snippet to extract (default: 32)",
    ),
) -> None:
    """Convert Notion export to LLMS.txt format."""
    if output is None:
        output = Path("notion-llms.txt")
    
    if verbose:
        console.print(f"🔍 Processing Notion export: {export_path}")
        console.print(f"📄 Output: {output}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        from .generator import LLMSTxtGenerator
        from .parser import NotionExportParser
        
        task = progress.add_task("Processing export...", total=None)
        
        # Parse Notion export
        progress.update(task, description="Scanning pages...")
        
        # Parse patterns from comma-separated strings
        include_patterns_list = [p.strip() for p in include_patterns.split(",")] if include_patterns else None
        exclude_patterns_list = [p.strip() for p in exclude_patterns.split(",")] if exclude_patterns else None
        
        parser = NotionExportParser(
            export_path,
            min_content_chars=min_content_chars,
            min_content_lines=min_content_lines,
            exclude_untitled=exclude_untitled,
            exclude_link_only=exclude_link_only,
            include_patterns=include_patterns_list,
            exclude_patterns=exclude_patterns_list,
            content_snippet_length=content_snippet_length,
        )
        
        progress.update(task, description="Analyzing structure...")
        export_data = parser.parse()
        
        # Generate LLMS.txt
        progress.update(task, description="Generating LLMS.txt...")
        generator = LLMSTxtGenerator()
        generator.save_to_file(export_data, output)
        
        # Show summary
        if verbose:
            stats = generator.get_summary_stats(export_data)
            console.print(f"📊 Processed {stats['total_pages']} pages")
            console.print(f"📁 Found {stats['total_categories']} categories")
            console.print(f"📝 Generated {stats['output_chars']:,} characters ({stats['output_lines']:,} lines)")
        
        progress.remove_task(task)
    
    console.print("✅ [bold green]Successfully generated LLMS.txt!")
    console.print(f"📁 Output saved to: {output}")


if __name__ == "__main__":
    app()