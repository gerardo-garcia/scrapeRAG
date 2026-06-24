# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**ScrapeRAG** converts a directory tree of HTML files (e.g., a product API manual) into clean Markdown files suitable for ingestion into RAG systems via SharePoint or similar connectors. It removes navigation/sidebar/footer boilerplate, deduplicates near-identical pages, and preserves tables and code blocks.

## Install and run

```bash
# Install in editable mode (creates the `scraperag` CLI)
pip install -e .

# Run the pipeline
scraperag <input-dir> <output-dir>

# Common options
scraperag <input-dir> <output-dir> \
  --min-words 50 \           # drop pages with fewer words after extraction
  --sim-threshold 0.9 \      # SimHash similarity for near-dup detection (0–1)
  --boilerplate-ratio 0.4 \  # fraction of pages a block must appear in to be stripped
  --verbose                  # log each skipped file
```

## Package structure

```
scraperag/
├── cli.py        # Typer CLI entry point → scraperag command
├── pipeline.py   # Orchestrates the full pipeline (order matters — see below)
├── crawler.py    # Discovers HTML files, handles encoding detection
├── extractor.py  # BS4 + markdownify: strips nav/header/footer, extracts main content
├── dedup.py      # Exact dedup (MD5) + near-dedup (SimHash on 3-shingles) + boilerplate removal
└── writer.py     # Writes .md files preserving input directory structure, adds YAML frontmatter
```

## Pipeline order

The order in `pipeline.py` is intentional and must be preserved:

1. **Extract** — BS4 removes nav/header/footer selectors, then markdownify converts to Markdown
2. **Filter** — drop pages below `--min-words`
3. **Deduplicate** — exact + near-dup removal (must happen **before** boilerplate, so duplicates don't inflate block counts)
4. **Boilerplate removal** — paragraph-level frequency analysis; blocks appearing in > `--boilerplate-ratio` of pages and longer than 40 chars are stripped
5. **Re-filter** — drop pages that became too short after boilerplate removal
6. **Write** — `.md` files with YAML frontmatter (`title`, `source`) mirroring the input directory tree

## Content selector strategy

`extractor.py` has two ordered lists that control what gets kept vs. removed:

- `_NAV_SELECTORS` — CSS selectors for elements to **remove** (nav, sidebar, header, footer, search, breadcrumbs). Extend this list when a doc theme uses non-standard class names.
- `_CONTENT_SELECTORS` — CSS selectors tried in order to find the **main content area**. Covers MkDocs, Sphinx, ReadTheDocs, and generic patterns. Falls back to `<body>` if nothing matches.

## Output format

Each output `.md` file has:
```markdown
---
title: "Page Title"
source: "relative/path/from/input/dir.html"
---

# Page Title

...clean Markdown content...
```
