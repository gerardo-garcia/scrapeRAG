from pathlib import Path


def _yaml_str(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_pages(pages: list[dict], input_dir: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for page in pages:
        src = Path(page["path"])
        rel = src.relative_to(input_dir)
        dest = output_dir / rel.with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)

        frontmatter = (
            "---\n"
            f"title: {_yaml_str(page['title'])}\n"
            f"source: {_yaml_str(str(rel))}\n"
            "---\n\n"
        )
        dest.write_text(frontmatter + page["content"] + "\n", encoding="utf-8")
        written += 1
    return written
