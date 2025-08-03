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
        parser = NotionExportParser(export_path)
        
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
        
        progress.remove_task(task)
    
    console.print("✅ [bold green]Successfully generated LLMS.txt!")
    console.print(f"📁 Output saved to: {output}")


if __name__ == "__main__":
    app()