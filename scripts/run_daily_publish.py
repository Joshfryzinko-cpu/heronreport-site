#!/usr/bin/env python3
"""
run_daily_publish.py — Unified daily news publisher for heronreport.com

Usage:
    python run_daily_publish.py --section politics
    python run_daily_publish.py --section business
    python run_daily_publish.py --section investigations

Each run:
  1. Searches for 3 real news stories relevant to the section
  2. Finds a UNIQUE image for each (enforced by ImageGuard — no duplicates possible)
  3. Builds the card HTML
  4. Prepends a new date row to the section page
  5. Trims rows older than 21 days
  6. Pushes to GitHub
"""

import argparse, subprocess, re, sys, os
from datetime import date, datetime, timedelta
from pathlib import Path

SITE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SITE_DIR / "scripts"))
from image_guard import ImageGuard

# ── Section config ────────────────────────────────────────────────────────────
SECTIONS = {
    "politics": {
        "file": "section-politics.html",
        "search_queries": [
            "Trump administration policy news today",
            "US Congress national security news today",
            "Florida law enforcement news today",
            "US energy economy news today",
        ],
        "badge_color": "#b91c1c",
        "badge_label": "Politics",
        "banner_color": "rgba(185,28,28,.15)",
        "row_class": "pol-card",
    },
    "business": {
        "file": "section-business.html",
        "search_queries": [
            "Florida small business entrepreneur news today",
            "Florida startup company news today",
            "Florida economy business award news today",
        ],
        "badge_color": "#166534",
        "badge_label": "Business",
        "banner_color": "rgba(22,101,52,.12)",
        "row_class": "biz-card",
    },
    "investigations": {
        "file": "section-investigations.html",
        "search_queries": [
            "government corruption fraud arrest indicted news today",
            "Florida corruption fraud misconduct news today",
            "federal waste fraud inspector general news today",
        ],
        "badge_color": "#7c2d12",
        "badge_label": "Investigations",
        "banner_color": "rgba(124,45,18,.2)",
        "row_class": "inv-card",
    },
}

ONERROR = "this.onerror=null;this.src='/img/placeholder.svg';this.style='object-fit:contain;padding:20px;background:#111'"


def web_search_stories(section_cfg: dict, n: int = 3) -> list[dict]:
    """Search for n real news stories. Returns list of {title, url, summary, source}."""
    from hermes_tools import web_search
    stories = []
    seen_urls = set()
    for query in section_cfg["search_queries"]:
        if len(stories) >= n:
            break
        results = web_search(query, limit=5)
        for r in results.get("data", {}).get("web", []):
            url = r.get("url", "")
            if url in seen_urls:
                continue
            # Skip paywalls, aggregators, and non-news
            if any(bad in url for bad in ["google.com/rss", "news.google", "msn.com",
                                           "bing.com/news", "yahoo.com/news",
                                           "deeplinks", "aclu.org", "eff.org"]):
                continue
            seen_urls.add(url)
            title = r.get("title", "").strip()
            desc  = r.get("description", "").strip()
            source = url.split("/")[2].replace("www.", "")
            stories.append({"title": title, "url": url, "summary": desc, "source": source})
            if len(stories) >= n:
                break
    return stories[:n]


def build_card(story: dict, img_path: str, section_cfg: dict) -> str:
    """Build a single news card HTML block."""
    title   = story["title"][:90]
    summary = story["summary"][:200]
    url     = story["url"]
    source  = story["source"]
    today   = date.today().strftime("%b %-d, %Y") if sys.platform != "win32" else date.today().strftime("%b %d, %Y").lstrip("0")
    badge   = section_cfg["badge_label"]
    color   = section_cfg["badge_color"]
    row_cls = section_cfg["row_class"]
    # Use source domain as credit
    credit  = source

    return f"""    <article class="{row_cls}">
      <a href="{url}" target="_blank" rel="noopener" class="card-link">
        <div class="card-img-wrap">
          <img src="{img_path}" alt="{title[:60]}" class="card-img"
               style="object-fit:cover;object-position:top center" loading="lazy"
               onerror="{ONERROR}">
          <span class="card-badge" style="background:{color}">{badge}</span>
          <span class="card-credit">{credit}</span>
        </div>
        <div class="card-body">
          <h2 class="card-title">{title}</h2>
          <p class="card-summary">{summary}</p>
          <div class="card-foot">
            <span class="card-source">{source}</span>
            <span class="card-date">{today}</span>
          </div>
        </div>
      </a>
    </article>"""


def build_date_row(cards_html: list[str]) -> str:
    today_label = date.today().strftime("%B %d, %Y")
    cards = "\n".join(cards_html)
    return f"""
<!-- DATE ROW: {today_label} -->
<div class="date-row">
  <div class="date-label">{today_label}</div>
  <div class="card-grid">
{cards}
  </div>
</div>"""


def trim_old_rows(html: str, keep_days: int = 21) -> str:
    """Remove date rows older than keep_days from the HTML."""
    cutoff = date.today() - timedelta(days=keep_days)
    def row_is_old(m):
        label = m.group(1)
        try:
            d = datetime.strptime(label, "%B %d, %Y").date()
            return d < cutoff
        except ValueError:
            return False
    # Find and remove old rows
    pattern = re.compile(
        r'\n<!-- DATE ROW: ([^-]+?) -->\n<div class="date-row">.*?</div>\n',
        re.DOTALL
    )
    result = []
    pos = 0
    for m in pattern.finditer(html):
        result.append(html[pos:m.start()])
        if not row_is_old(m):
            result.append(m.group(0))
        pos = m.end()
    result.append(html[pos:])
    return "".join(result)


def insert_after_marker(html: str, new_row: str, section: str) -> str:
    """Insert new_row after the section's opening content marker."""
    # Look for the first date-row or the card grid container
    markers = [
        '<!-- DATE ROW:',
        '<div class="card-grid">',
        '<div class="date-row">',
        f'class="{SECTIONS[section]["row_class"]}"',
        '<main',
    ]
    for marker in markers:
        idx = html.find(marker)
        if idx > 0:
            return html[:idx] + new_row + "\n" + html[idx:]
    # Fallback: append before </main>
    idx = html.rfind("</main>")
    if idx > 0:
        return html[:idx] + new_row + "\n" + html[idx:]
    return html + new_row


def run(section: str):
    cfg = SECTIONS[section]
    page_file = SITE_DIR / cfg["file"]

    if not page_file.exists():
        print(f"ERROR: {page_file} not found")
        sys.exit(1)

    print(f"\n=== Publishing {section} ({date.today()}) ===")

    # 1. Find stories
    print("Finding stories...")
    stories = web_search_stories(cfg, n=3)
    if not stories:
        print("No stories found — aborting")
        sys.exit(1)
    print(f"  Found {len(stories)} stories")

    # 2. Get unique images (enforced — no duplicates possible)
    guard = ImageGuard()
    cards = []
    for story in stories:
        print(f"  Story: {story['title'][:60]}")
        img = guard.fetch_from_article(story["url"], story_title=story["title"], used_on=cfg["file"])
        if img is None:
            # Try a direct web search for a relevant image
            from hermes_tools import web_search as ws
            alt_results = ws(story["title"] + " photo", limit=4)
            for alt in alt_results.get("data", {}).get("web", []):
                img = guard.fetch_from_article(alt["url"], story_title=story["title"], used_on=cfg["file"])
                if img:
                    break
        if img is None:
            img = "/img/placeholder.svg"
            print(f"    → No unique image found, using placeholder")
        else:
            print(f"    → {img.split('/')[-1]}")
        cards.append(build_card(story, img, cfg))

    # 3. Build new date row
    new_row = build_date_row(cards)

    # 4. Update page
    html = page_file.read_text(encoding="utf-8")
    html = insert_after_marker(html, new_row, section)
    html = trim_old_rows(html, keep_days=21)
    page_file.write_text(html, encoding="utf-8")
    print(f"  Updated {cfg['file']}")

    # 5. Save registry
    guard.save_registry()

    # 6. Push to GitHub
    print("  Pushing to GitHub...")
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", f"{section.capitalize()}: {date.today()}"],
        ["git", "push", "origin", "main"],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=str(SITE_DIR), capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" not in r.stdout:
            print(f"  Git error: {r.stderr[:200]}")

    print(f"  Done — {len(cards)} stories published\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--section", required=True, choices=["politics","business","investigations"])
    args = parser.parse_args()
    run(args.section)
