from pathlib import Path
import chardet

_HTML_EXTENSIONS = {".html", ".htm"}


def find_html_files(directory: Path) -> list[Path]:
    return sorted(
        f for f in directory.rglob("*")
        if f.suffix.lower() in _HTML_EXTENSIONS and f.is_file()
    )


def read_html(path: Path) -> str:
    raw = path.read_bytes()
    detected = chardet.detect(raw)
    encoding = detected.get("encoding") or "utf-8"
    try:
        return raw.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        return raw.decode("utf-8", errors="replace")
