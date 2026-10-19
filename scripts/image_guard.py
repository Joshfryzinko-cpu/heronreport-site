"""
image_guard.py — Enforced image deduplication for heronreport.com

USAGE:
    from image_guard import ImageGuard
    guard = ImageGuard()
    local_path = guard.fetch_unique(url)   # returns /img/stories/xxx.jpg or None if duplicate
    guard.save_registry()                  # always call at the end

This module ENFORCES deduplication in code. The AI cron jobs call this
and cannot bypass it — if the image hash already exists, fetch_unique returns None.
"""

import hashlib, json, requests
from datetime import date
from pathlib import Path

SITE_DIR     = Path(__file__).parent.parent          # heronreport-site/
REGISTRY     = SITE_DIR / "scripts" / "image_registry.json"
IMG_STORE    = SITE_DIR / "img" / "stories"
PLACEHOLDER  = "/img/placeholder.svg"
HEADERS      = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
EXT_MAP      = {
    "image/jpeg": ".jpg", "image/png": ".png",
    "image/webp": ".webp", "image/gif": ".gif",
    "image/svg+xml": ".svg",
}


class ImageGuard:
    def __init__(self):
        IMG_STORE.mkdir(parents=True, exist_ok=True)
        self._load_registry()
        # Rebuild known hashes from every image currently on the site
        self._sync_from_disk()

    # ── Registry I/O ─────────────────────────────────────────────────────

    def _load_registry(self):
        if REGISTRY.exists():
            data = json.loads(REGISTRY.read_text(encoding="utf-8"))
            self._entries = data.get("entries", [])
        else:
            self._entries = []
        self._known_hashes = {e["md5"] for e in self._entries if e.get("md5")}
        self._known_urls   = {e.get("source_url","") for e in self._entries}

    def _sync_from_disk(self):
        """Hash every image file currently on disk and add to known set."""
        for f in IMG_STORE.iterdir():
            if f.is_file() and f.stat().st_size > 200:
                h = hashlib.md5(f.read_bytes()).hexdigest()
                self._known_hashes.add(h)

    def save_registry(self):
        data = {
            "entries": self._entries,
            "last_updated": str(date.today()),
            "total": len(self._entries),
        }
        REGISTRY.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # ── Core: fetch a unique image ────────────────────────────────────────

    def fetch_unique(self, img_url: str, story_title: str = "", used_on: str = "") -> str | None:
        """
        Download img_url, check its md5 against ALL known images.
        Returns local path (/img/stories/xxx.jpg) if unique, None if duplicate.
        """
        if not img_url or not img_url.startswith("http"):
            return None
        try:
            r = requests.get(img_url, headers=HEADERS, timeout=12, stream=True)
            if r.status_code != 200:
                return None
            ct = r.headers.get("Content-Type", "").split(";")[0].strip()
            ext = EXT_MAP.get(ct, ".jpg")
            raw = b"".join(r.iter_content(65536))
            if len(raw) < 2000:
                return None
            h = hashlib.md5(raw).hexdigest()
            if h in self._known_hashes:
                return None   # DUPLICATE — reject
            # Unique — save it
            key = hashlib.md5(img_url.encode()).hexdigest()[:16]
            dest = IMG_STORE / f"{key}{ext}"
            dest.write_bytes(raw)
            local = f"/img/stories/{dest.name}"
            self._known_hashes.add(h)
            self._entries.append({
                "local_path": local,
                "source_url": img_url,
                "md5": h,
                "used_on": [used_on] if used_on else [],
                "story_context": story_title[:80],
                "added": str(date.today()),
            })
            return local
        except Exception:
            return None

    def get_og_image(self, article_url: str) -> str | None:
        """Extract og:image URL from an article page."""
        import re
        try:
            r = requests.get(article_url, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                return None
            og = re.search(
                r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text)
            if not og:
                og = re.search(
                    r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', r.text)
            return og.group(1) if og else None
        except Exception:
            return None

    def fetch_from_article(self, article_url: str, story_title: str = "",
                           used_on: str = "") -> str | None:
        """
        Get og:image from article_url, then fetch_unique it.
        Returns local path or None.
        """
        og = self.get_og_image(article_url)
        if not og:
            return None
        return self.fetch_unique(og, story_title=story_title, used_on=used_on)

    def is_duplicate_url(self, img_url: str) -> bool:
        """Quick check: has this exact URL been stored before?"""
        return img_url in self._known_urls
