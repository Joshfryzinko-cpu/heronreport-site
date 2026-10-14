#!/usr/bin/env python3
"""
Heron Report — Image Migration
Scans all existing HTML pages, downloads every external img src,
stores it in /img/stories/, rewrites the src to the local path.
Adds onerror fallback to every img tag.
Run once to fix all existing thumbnails permanently.
"""
import sys, os, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from image_store import download_and_store, PLACEHOLDER, STORE_DIR, already_stored

SITE = Path(__file__).parent.parent
PAGES = [
    "index.html",
    "section-politics.html",
    "section-business.html",
    "section-investigations.html",
    "heroes.html",
    "about.html",
    "privacy.html",
]

ONERROR = "this.onerror=null;this.src='/img/placeholder.svg';this.style='object-fit:contain;padding:20px;background:#111'"

def fix_page(page_name):
    path = SITE / page_name
    if not path.exists():
        print(f"  SKIP (not found): {page_name}")
        return 0

    html = path.read_text(encoding="utf-8")
    original = html

    # Pattern: <img ...src="http://..." ... >
    img_pattern = re.compile(
        r'(<img\b(?:[^>]*?\s)?)src="((?!data:)(?!/)https?://[^"]+)"([^>]*?>)',
        re.IGNORECASE | re.DOTALL
    )

    downloaded = 0
    skipped   = 0

    def replace_img(m):
        nonlocal downloaded, skipped
        before, url, after = m.group(1), m.group(2), m.group(3)

        # Already stored?
        local = already_stored(url)
        if not local:
            local = download_and_store(url)

        if local == PLACEHOLDER:
            skipped += 1
            new_src = f'src="{PLACEHOLDER}"'
        else:
            downloaded += 1
            new_src = f'src="{local}"'

        # Ensure onerror is present
        tag = before + new_src + after
        if "onerror" not in tag:
            tag = tag[:-1] + f' onerror="{ONERROR}">'

        return tag

    html = img_pattern.sub(replace_img, html)

    if html != original:
        path.write_text(html, encoding="utf-8")

    print(f"  {page_name}: {downloaded} stored, {skipped} used placeholder")
    return downloaded

def main():
    print(f"\n{'='*60}")
    print("Heron Report — Image Migration to Local Storage")
    print(f"{'='*60}\n")

    total = 0
    for page in PAGES:
        total += fix_page(page)

    print(f"\n{'='*60}")
    print(f"Migration complete: {total} images stored in /img/stories/")
    print(f"Stored images directory: {STORE_DIR}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
