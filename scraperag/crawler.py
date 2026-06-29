from pathlib import Path
import chardet

_HTML_EXTENSIONS = {".html", ".htm"}
_PDF_EXTENSIONS = {".pdf"}
_SOURCE_EXTENSIONS = _HTML_EXTENSIONS | _PDF_EXTENSIONS


def find_source_files(directory: Path) -> list[Path]:
    """Discover all supported source files (HTML and PDF) under directory."""
    return sorted(
        f for f in directory.rglob("*")
        if f.suffix.lower() in _SOURCE_EXTENSIONS and f.is_file()
    )


def is_pdf(path: Path) -> bool:
    return path.suffix.lower() in _PDF_EXTENSIONS


def read_html(path: Path) -> str:
    raw = path.read_bytes()
    detected = chardet.detect(raw)
    encoding = detected.get("encoding") or "utf-8"
    try:
        return raw.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        return raw.decode("utf-8", errors="replace")
