#!/usr/bin/env python3
"""
Repair script: find every card whose PRIMARY image is /img/placeholder.svg
(not just the onerror fallback) and try to replace it with a real, unique
photo found by searching the story's headline via Bing News, resolving to
the real publisher URL, and pulling its og:image through the same
ImageGuard dedup pipeline the daily publisher uses.

Leaves the card untouched (still placeholder) if no real unique image can
be found — this script never fabricates an image.
"""
import sys, os, re, html as html_lib, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from image_guard import ImageGuard
from utils import search_news

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_PAGES = ["section-business.html", "section-politics.html", "heroes.html"]

# Matches a primary placeholder <img ...> tag and captures its full text,
# the alt attribute (headline/approx title), and whatever onerror tail follows.
IMG_RE = re.compile(
    r'<img src="/img/placeholder\.svg" alt="([^"]*)"([^>]*)>'
)


def find_real_image(title, used_on):
    """Search Bing News for the real article, try its og:image via ImageGuard."""
    query = html_lib.unescape(title).strip()
    if not query:
        return None
    try:
        results = search_news(query, limit=5)
    except Exception as e:
        print(f"    search_news error: {e}")
        return None
    guard = ImageGuard()
    for r in results:
        url = r.get("url", "")
        if not url or "bing.com" in url:
            continue
        img = guard.fetch_from_article(url, story_title=title, used_on=used_on)
        if img:
            guard.save_registry()
            return img, url
    guard.save_registry()
    return None


def repair_page(path):
    page_name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        html = f.read()

    matches = list(IMG_RE.finditer(html))
    print(f"\n{page_name}: {len(matches)} placeholder cards")
    if not matches:
        return 0, 0

    fixed = 0
    # Process from the end so earlier match spans stay valid as we splice.
    for m in reversed(matches):
        alt_text, rest_attrs = m.group(1), m.group(2)
        print(f"  -> {alt_text[:70]}")
        result = find_real_image(alt_text, page_name)
        if not result:
            print(f"     no real unique image found, leaving placeholder")
            continue
        local_img, source_url = result
        print(f"     FOUND: {local_img}  (from {source_url[:70]})")
        # Rebuild the <img> tag: real photo => cover style, keep other attrs,
        # and point the onerror fallback's style tweak at cover too.
        new_rest = re.sub(
            r"object-fit:contain;padding:\d+px;background:#111",
            "object-fit:cover;object-position:top center",
            rest_attrs,
        )
        new_tag = f'<img src="{local_img}" alt="{alt_text}"{new_rest}>'
        html = html[: m.start()] + new_tag + html[m.end():]
        fixed += 1
        time.sleep(0.3)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return len(matches), fixed


def main():
    total_cards, total_fixed = 0, 0
    for page in TARGET_PAGES:
        path = os.path.join(SITE_DIR, page)
        if not os.path.exists(path):
            continue
        n, fixed = repair_page(path)
        total_cards += n
        total_fixed += fixed
    print(f"\n=== SUMMARY: {total_fixed}/{total_cards} placeholder cards repaired with real images ===")


if __name__ == "__main__":
    main()
