"""
Heron Report — Permanent Image Store
Downloads story images at publish time and stores them in /img/stories/.
Each image is named by the URL's MD5 hash so it is stable and deduplicated.
Replaces expiring CDN URLs with self-hosted paths that work forever.
"""

import os
import hashlib
import requests
import mimetypes
from pathlib import Path

SITE_DIR = Path(__file__).parent.parent
STORE_DIR = SITE_DIR / "img" / "stories"
PLACEHOLDER = "/img/placeholder.svg"
STORE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/png,image/jpeg,*/*",
}

EXT_MAP = {
    "image/jpeg":    ".jpg",
    "image/png":     ".png",
    "image/webp":    ".webp",
    "image/svg+xml": ".svg",
    "image/gif":     ".gif",
}


def url_key(url: str) -> str:
    """Stable 16-char key for any URL."""
    return hashlib.md5(url.strip().encode()).hexdigest()[:16]


def local_path_for(url: str, ext: str = ".jpg") -> Path:
    return STORE_DIR / f"{url_key(url)}{ext}"


def already_stored(url: str) -> str | None:
    """Return local web path if this URL was already downloaded, else None."""
    key = url_key(url)
    for ext in (".jpg", ".png", ".webp", ".svg", ".gif"):
        p = STORE_DIR / f"{key}{ext}"
        if p.exists() and p.stat().st_size > 1000:
            return f"/img/stories/{key}{ext}"
    return None


def download_and_store(url: str, timeout: int = 12) -> str:
    """
    Download the image at `url`, save it to /img/stories/, and return its
    web-root-relative path (/img/stories/<key>.<ext>).
    Returns PLACEHOLDER on any failure.
    Never overwrites an existing stored image (dedup by URL hash).
    """
    if not url or not url.startswith("http"):
        return PLACEHOLDER

    # Already have it — return immediately
    cached = already_stored(url)
    if cached:
        return cached

    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        if r.status_code != 200:
            return PLACEHOLDER

        ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        ext = EXT_MAP.get(ct, ".jpg")

        dest = local_path_for(url, ext)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(65536):
                f.write(chunk)

        # Sanity: must be at least 8 KB to be a real image (Google logo is ~2KB)
        if dest.stat().st_size < 8192:
            dest.unlink(missing_ok=True)
            return PLACEHOLDER

        web_path = f"/img/stories/{dest.name}"
        print(f"    ✓ stored {url[:60]} → {web_path}")
        return web_path

    except Exception as e:
        print(f"    ✗ failed to download {url[:60]}: {e}")
        return PLACEHOLDER


def migrate_existing_pages(page_files: list[str]) -> dict[str, int]:
    """
    Scan existing HTML pages for <img src="http…"> tags,
    download each external image once, and rewrite the src to the local path.
    Returns {filename: count_replaced}.
    """
    import re
    results = {}

    for path_str in page_files:
        p = Path(path_str)
        if not p.exists():
            continue

        html = p.read_text(encoding="utf-8")
        pattern = re.compile(r'(<img\b[^>]*?\bsrc=")(?!data:)(?!/)([^"]+)(")', re.IGNORECASE)
        count = 0

        def replace_src(m):
            nonlocal count
            prefix, url, suffix = m.group(1), m.group(2), m.group(3)
            if not url.startswith("http"):
                return m.group(0)
            local = download_and_store(url)
            if local and local != PLACEHOLDER:
                count += 1
                return prefix + local + suffix
            return m.group(0)

        new_html = pattern.sub(replace_src, html)
        if count:
            p.write_text(new_html, encoding="utf-8")
            print(f"  {p.name}: {count} images stored locally")

        results[p.name] = count

    return results
