from pathlib import Path

from .extractor import tidy_markdown

_MARKITDOWN_HINT = (
    "PDF support requires the 'markitdown' extra. Install it with:\n"
    "    pip install 'scraperag[pdf]'"
)


def _convert(path: Path) -> str:
    """Convert a PDF to raw Markdown via markitdown (imported lazily)."""
    try:
        from markitdown import MarkItDown
    except ImportError as exc:  # pragma: no cover - depends on install extras
        raise RuntimeError(_MARKITDOWN_HINT) from exc

    result = MarkItDown().convert(str(path))
    return (result.title or "").strip(), result.text_content or ""


def _title_from_text(text: str) -> str:
    """First non-empty line, if it reads like a heading rather than a paragraph."""
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped if len(stripped) <= 80 else ""
    return ""


def extract_pdf(path: Path) -> tuple[str, str]:
    """Return (title, markdown) from a PDF file.

    markitdown rarely exposes a PDF title, so fall back to the first heading-like
    line and finally the filename. A top-level heading is prepended when the
    converted text lacks one, mirroring the H1 that HTML pages carry.
    """
    md_title, raw_md = _convert(path)
    content = tidy_markdown(raw_md)

    title = md_title or _title_from_text(content) or path.stem
    if not content.startswith("#"):
        # If the first text line is the title itself, promote it to a heading
        # instead of prepending a duplicate line.
        first, _, rest = content.partition("\n\n")
        if first.strip() == title:
            content = f"# {title}\n\n{rest}".strip()
        else:
            content = f"# {title}\n\n{content}".strip()

    return title, content
