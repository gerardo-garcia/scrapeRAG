from pathlib import Path
from typing import Annotated
import typer

from .pipeline import run

app = typer.Typer(
    help="Transform HTML doc dumps into clean Markdown for RAG systems.",
    add_completion=False,
)


@app.command()
def main(
    input_dir: Annotated[
        Path,
        typer.Argument(help="Directory containing HTML files to process", exists=True, file_okay=False),
    ],
    output_dir: Annotated[
        Path,
        typer.Argument(help="Output directory where Markdown files will be written"),
    ],
    min_words: Annotated[
        int,
        typer.Option("--min-words", help="Drop pages with fewer than this many words after extraction"),
    ] = 50,
    sim_threshold: Annotated[
        float,
        typer.Option("--sim-threshold", help="SimHash similarity threshold for near-duplicate detection (0–1)"),
    ] = 0.9,
    boilerplate_ratio: Annotated[
        float,
        typer.Option("--boilerplate-ratio", help="Fraction of pages a text block must appear in to be treated as boilerplate"),
    ] = 0.4,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Log each skipped file")] = False,
) -> None:
    run(input_dir, output_dir, min_words, sim_threshold, boilerplate_ratio, verbose)
