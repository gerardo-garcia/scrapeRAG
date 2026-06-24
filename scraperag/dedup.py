import hashlib
import re


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _shingles(words: list[str], n: int = 3) -> list[str]:
    if len(words) < n:
        return words
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def _simhash(text: str, bits: int = 64) -> int:
    words = _normalize(text).split()
    tokens = _shingles(words)
    mask = (1 << bits) - 1
    v = [0] * bits
    for token in tokens:
        h = int(hashlib.sha1(token.encode()).hexdigest(), 16) & mask
        for i in range(bits):
            v[i] += 1 if (h >> i) & 1 else -1
    return sum(1 << i for i in range(bits) if v[i] > 0)


def _similarity(h1: int, h2: int, bits: int = 64) -> float:
    return 1.0 - bin(h1 ^ h2).count("1") / bits


def _content_hash(text: str) -> str:
    return hashlib.md5(_normalize(text).encode()).hexdigest()


_MIN_BOILERPLATE_CHARS = 40  # ignore very short blocks (headings, single words)


def remove_boilerplate(pages: list[dict], ratio: float = 0.4) -> list[dict]:
    """Remove paragraph-level blocks that appear in > ratio of pages.

    Only considers blocks with at least _MIN_BOILERPLATE_CHARS characters to
    avoid marking structural headings as boilerplate.
    """
    if not pages:
        return pages

    freq: dict[str, int] = {}
    for page in pages:
        seen = set()
        for para in page["content"].split("\n\n"):
            key = _normalize(para)
            if key and len(key) >= _MIN_BOILERPLATE_CHARS and key not in seen:
                seen.add(key)
                freq[key] = freq.get(key, 0) + 1

    threshold = ratio * len(pages)
    boilerplate = {k for k, count in freq.items() if count >= threshold}

    result = []
    for page in pages:
        paras = page["content"].split("\n\n")
        kept = [
            p for p in paras
            if len(_normalize(p)) < _MIN_BOILERPLATE_CHARS or _normalize(p) not in boilerplate
        ]
        result.append({**page, "content": "\n\n".join(kept).strip()})
    return result


def deduplicate(pages: list[dict], threshold: float = 0.9) -> list[dict]:
    """Remove exact and near-duplicate pages (keeps first occurrence)."""
    seen_hashes: set[str] = set()
    seen_simhashes: list[int] = []
    kept: list[dict] = []

    for page in pages:
        h = _content_hash(page["content"])
        if h in seen_hashes:
            continue

        sh = _simhash(page["content"])
        if any(_similarity(sh, s) >= threshold for s in seen_simhashes):
            continue

        seen_hashes.add(h)
        seen_simhashes.append(sh)
        kept.append(page)

    return kept
