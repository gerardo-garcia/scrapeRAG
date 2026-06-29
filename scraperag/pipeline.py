from pathlib import Path
import typer
from tqdm import tqdm

from .crawler import find_source_files, is_pdf, read_html
from .extractor import extract, word_count
from .pdf import extract_pdf
from .dedup import remove_boilerplate, deduplicate
from .writer import write_pages


def run(
    input_dir: Path,
    output_dir: Path,
    min_words: int = 50,
    sim_threshold: float = 0.9,
    boilerplate_ratio: float = 0.4,
    verbose: bool = False,
) -> None:
    source_files = find_source_files(input_dir)
    typer.echo(f"Found {len(source_files)} source files (HTML/PDF) in {input_dir}")

    pages: list[dict] = []
    skipped_short = 0

    for f in tqdm(source_files, desc="Extracting", unit="file"):
        if is_pdf(f):
            title, content = extract_pdf(f)
        else:
            title, content = extract(read_html(f))
        if word_count(content) < min_words:
            skipped_short += 1
            if verbose:
                typer.echo(f"  skip (too short): {f.relative_to(input_dir)}")
            continue
        pages.append({"path": str(f), "title": title, "content": content})

    typer.echo(
        f"Extracted {len(pages)} pages  |  skipped {skipped_short} with < {min_words} words"
    )

    # Dedup before boilerplate so identical pages don't inflate block counts
    before_dedup = len(pages)
    pages = deduplicate(pages, sim_threshold)
    typer.echo(
        f"Dedup: removed {before_dedup - len(pages)} duplicates  |  {len(pages)} unique pages"
    )

    pages = remove_boilerplate(pages, boilerplate_ratio)
    # Re-filter: boilerplate removal can leave pages nearly empty
    before_refilter = len(pages)
    pages = [p for p in pages if word_count(p["content"]) >= min_words]
    emptied = before_refilter - len(pages)
    typer.echo(
        f"Boilerplate removed  |  {emptied} pages became too short and were dropped"
        if emptied
        else "Boilerplate removed"
    )

    written = write_pages(pages, input_dir, output_dir)
    typer.echo(f"\nDone — wrote {written} Markdown files to {output_dir}")
