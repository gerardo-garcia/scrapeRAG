import re
from bs4 import BeautifulSoup, Comment
import markdownify as md_lib

_REMOVE_TAGS = {
    "script", "style", "noscript", "iframe", "svg",
    "link", "meta", "button", "form", "input", "select", "textarea",
}

# Ordered from most to least specific — first match wins
_CONTENT_SELECTORS = [
    # MkDocs / Material
    "[class*='md-content']",
    # Sphinx
    ".rst-content", ".document", ".body",
    # ReadTheDocs
    "[role='main']",
    # Generic
    "main", "article",
    "#content", "#main", "#doc-content",
    ".content", ".main-content", ".doc-content", ".documentation",
    "[class*='content-body']", "[class*='page-content']",
]

_NAV_SELECTORS = [
    "nav", "header", "footer", "aside",
    "[class*='nav']", "[class*='sidebar']", "[class*='menu']",
    "[class*='toc']", "[class*='breadcrumb']", "[class*='pagination']",
    "[class*='search']", "[class*='toolbar']", "[class*='header']",
    "[class*='footer']", "[class*='announce']", "[class*='skip']",
    "[id*='nav']", "[id*='sidebar']", "[id*='menu']", "[id*='toc']",
    "[id*='search']", "[id*='header']", "[id*='footer']",
]


def extract(html: str) -> tuple[str, str]:
    """Return (title, markdown) from raw HTML."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(_REMOVE_TAGS):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    title = ""
    if soup.title:
        title = soup.title.get_text(strip=True)
    if not title and (h1 := soup.find("h1")):
        title = h1.get_text(strip=True)

    for selector in _NAV_SELECTORS:
        for el in soup.select(selector):
            el.decompose()

    content = None
    for selector in _CONTENT_SELECTORS:
        candidate = soup.select_one(selector)
        if candidate and len(candidate.get_text(strip=True)) > 100:
            content = candidate
            break
    if content is None:
        content = soup.body or soup

    raw_md = md_lib.markdownify(str(content), heading_style="ATX", bullets="-", strip=["img"])

    return title, tidy_markdown(raw_md)


def tidy_markdown(raw_md: str) -> str:
    """Collapse 3+ consecutive blank lines → 2 and strip trailing whitespace."""
    lines = [ln.rstrip() for ln in raw_md.splitlines()]
    cleaned: list[str] = []
    blank_run = 0
    for ln in lines:
        if not ln:
            blank_run += 1
            if blank_run <= 2:
                cleaned.append(ln)
        else:
            blank_run = 0
            cleaned.append(ln)

    return "\n".join(cleaned).strip()


def word_count(text: str) -> int:
    return len(text.split())
