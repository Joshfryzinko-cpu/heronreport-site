"""
Heron Report — Shared Publishing Utilities
Runs in GitHub Actions (Ubuntu) — no Hermes dependencies.
"""

import requests
import feedparser
import re
import json
import os
import hashlib
from datetime import datetime, date
from urllib.parse import quote_plus, urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

RUN_LOG_PATH = "scripts/run_log.json"
PUBLISHED_IDS_PATH = "scripts/published_ids.json"

# Import image store so every publish call downloads + stores images permanently
try:
    from image_store import download_and_store as _store_img, PLACEHOLDER
    _USE_IMAGE_STORE = True
except ImportError:
    _USE_IMAGE_STORE = False
    PLACEHOLDER = "/img/placeholder.svg"


# ─── Deduplication ───────────────────────────────────────────────────────────

def url_id(url):
    """Stable ID for a story based on its URL."""
    return hashlib.md5(url.strip().lower().encode()).hexdigest()[:12]

def load_published_ids():
    if os.path.exists(PUBLISHED_IDS_PATH):
        with open(PUBLISHED_IDS_PATH) as f:
            return set(json.load(f))
    return set()

def save_published_ids(ids):
    with open(PUBLISHED_IDS_PATH, 'w') as f:
        json.dump(sorted(ids), f, indent=2)

def is_duplicate(url, published_ids):
    return url_id(url) in published_ids

def mark_published(url, published_ids):
    published_ids.add(url_id(url))


# ─── Run Logging ─────────────────────────────────────────────────────────────

def load_run_log():
    if os.path.exists(RUN_LOG_PATH):
        with open(RUN_LOG_PATH) as f:
            return json.load(f)
    return []

def append_run_log(entry):
    log = load_run_log()
    log.append(entry)
    log = log[-90:]  # keep 90 most recent runs
    with open(RUN_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)


# ─── News Search via Google News RSS ─────────────────────────────────────────

def search_news(query, limit=8):
    """
    Search Bing News RSS — gives real article URLs (no Google redirect encoding).
    Follows Bing's own redirect to get the final publisher URL.
    Falls back to Google News RSS if Bing returns no results.
    """
    results = _search_bing_news(query, limit)
    if not results:
        results = _search_google_news(query, limit)
    return results


def _follow_redirect(url, timeout=6):
    """Follow a redirect URL and return the final URL."""
    try:
        r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r.url if r.url != url else url
    except Exception:
        return url


def _search_bing_news(query, limit=8):
    """Bing News RSS — entries use redirect URLs that resolve to real article URLs."""
    url = f"https://www.bing.com/news/search?q={quote_plus(query)}&format=rss"
    try:
        import feedparser as _fp
        feed = _fp.parse(url)
        results = []
        for entry in feed.entries[:limit * 2]:  # fetch extra, some will fail
            bing_url = entry.get('link', '')
            if not bing_url:
                continue
            real_url = _follow_redirect(bing_url)
            # Skip if still on Bing
            if 'bing.com' in real_url:
                continue
            title = entry.get('title', '')
            if not title:
                continue
            src_raw = entry.get('source', '')
            src = src_raw.get('title', '') if isinstance(src_raw, dict) else entry.get('author', '')
            results.append({
                'title':  title,
                'url':    real_url,
                'date':   entry.get('published', ''),
                'source': src,
                'desc':   re.sub('<[^>]+>', '', entry.get('summary', '')),
            })
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        print(f"  _search_bing_news error: {e}")
        return []


def _search_google_news(query, limit=8):
    """
    Google News RSS fallback — WARNING: article links are Google redirect URLs.
    og:image from these redirects returns the Google News logo for every story.
    This fallback is only used when Bing fails; caller MUST check image quality.
    """
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        import feedparser as _fp
        feed = _fp.parse(url)
        results = []
        for entry in feed.entries[:limit]:
            src_raw = entry.get('source', {})
            src = src_raw.get('title', '') if isinstance(src_raw, dict) else ''
            src_href = src_raw.get('href', '') if isinstance(src_raw, dict) else ''
            results.append({
                'title':    entry.get('title', ''),
                'url':      entry.get('link', ''),    # ← Google redirect, needs resolution
                'date':     entry.get('published', ''),
                'source':   src,
                'src_href': src_href,   # actual publisher domain
                'desc':     re.sub('<[^>]+>', '', entry.get('summary', '')),
                '_from_gnews': True,
            })
        return results
    except Exception as e:
        print(f"  _search_google_news error: {e}")
        return []


# ─── Image Finding ───────────────────────────────────────────────────────────

def get_og_image(url, timeout=10):
    """Get og:image meta tag from a URL, download it locally, return local path."""
    # Reject Google News redirect URLs immediately — they return the Google News logo
    if 'news.google.com/rss/articles' in url:
        print(f"    skip Google News redirect URL: {url[:50]}")
        return None
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        og = re.search(r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text)
        if not og:
            og = re.search(r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', r.text)
        if og:
            img = og.group(1).strip()
            if img.startswith('//'):
                img = 'https:' + img
            # Reject Google logos, favicons, tracking pixels
            if _is_bad_image_url(img):
                print(f"    reject bad image: {img[:60]}")
                return None
            # Store locally for permanence
            if _USE_IMAGE_STORE:
                local = _store_img(img)
                if local and local != PLACEHOLDER:
                    return local
            elif verify_image(img):
                return img
    except Exception:
        pass
    return None


_BAD_URL_PATTERNS = [
    'lh3.googleusercontent.com',
    'news.google.com',
    'encrypted-tbn0.gstatic.com',
    '/favicon',
    'favicon.ico',
    'favicon.png',
    '1x1.',
    'doubleclick.net',
    'googletagmanager.com',
]

def _is_bad_image_url(url: str) -> bool:
    url_lower = url.lower()
    return any(pat.lower() in url_lower for pat in _BAD_URL_PATTERNS)

def verify_image(url, timeout=6):
    """Return True if URL is a valid, loadable image."""
    if not url or not url.startswith('http'):
        return False
    try:
        r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        return r.status_code == 200 and ('image' in ct or 'svg' in ct)
    except Exception:
        return False

# Official fallback images (verified working)
FALLBACK_IMGS = {
    'whitehouse':  'https://www.whitehouse.gov/wp-content/uploads/2025/03/WH47-Social-Share-Card.jpg',
    'dhs':         'https://www.dhs.gov/sites/default/files/2024-02/24_0206_opa_og-image-dhs.jpg',
    'fdle':        'https://upload.wikimedia.org/wikipedia/commons/a/a8/FL_-_Department_of_Law_Enforcement_Badge.png',
    'cia':         'https://upload.wikimedia.org/wikipedia/commons/2/25/Seal_of_the_Central_Intelligence_Agency.svg',
    'doj':         'https://upload.wikimedia.org/wikipedia/commons/5/54/Seal_of_the_United_States_Department_of_Justice.svg',
    'bcso':        'https://bayso.org/wp-content/uploads/2025/10/BCSO_Badge.png',
    'gulf_county': 'https://cdnsm5-hosted.civiclive.com/UserFiles/Servers/Server_6500990/Templates/design-file/logo200.png',
    'energy':      'https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=800&q=80',
    'economy':     'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
    'military':    'https://images.unsplash.com/photo-1562979314-bee7453e911c?w=800&q=80',
    'politics':    'https://www.whitehouse.gov/wp-content/uploads/2025/03/WH47-Social-Share-Card.jpg',
}

_USED_FALLBACKS = set()  # track which fallbacks were used this run

def get_topic_fallback(topic_hint):
    """Return a stored local path and credit for a topic.
    Cycles through alternates so the same fallback is never used twice on one page.
    """
    hint = topic_hint.lower()
    if any(k in hint for k in ['energy','oil','fuel','gas']):
        url, credit = FALLBACK_IMGS['energy'], 'CC0 / Unsplash (illustrative)'
    elif any(k in hint for k in ['military','war','defense','nato']):
        url, credit = FALLBACK_IMGS['military'], 'CC0 / Unsplash (illustrative)'
    elif any(k in hint for k in ['economy','fed','inflation','budget','spending']):
        url, credit = FALLBACK_IMGS['economy'], 'CC0 / Unsplash (illustrative)'
    elif any(k in hint for k in ['trump','white house','executive','president','biden']):
        url, credit = FALLBACK_IMGS['whitehouse'], 'The White House (official)'
    elif any(k in hint for k in ['dhs','homeland','border','immigration']):
        url, credit = FALLBACK_IMGS['dhs'], 'U.S. Dept. of Homeland Security (official)'
    elif any(k in hint for k in ['fdle','florida law enforcement']):
        url, credit = FALLBACK_IMGS['fdle'], 'Florida Dept. of Law Enforcement (public domain)'
    elif any(k in hint for k in ['sheriff','county','bay county','gulf county','franklin']):
        url, credit = FALLBACK_IMGS['bcso'], 'Bay County Sheriff\'s Office'
    else:
        url, credit = FALLBACK_IMGS['dhs'], 'Official agency image (illustrative)'

    # If this fallback was already used this run, rotate through alternate fallbacks
    if url in _USED_FALLBACKS:
        alternates = [
            (FALLBACK_IMGS['dhs'],       'U.S. Dept. of Homeland Security (official)'),
            (FALLBACK_IMGS['fdle'],      'Florida Dept. of Law Enforcement (public domain)'),
            (FALLBACK_IMGS['bcso'],      'Bay County Sheriff\'s Office'),
            (FALLBACK_IMGS['whitehouse'],'The White House (official)'),
            (FALLBACK_IMGS['military'],  'CC0 / Unsplash (illustrative)'),
            (FALLBACK_IMGS['energy'],    'CC0 / Unsplash (illustrative)'),
            (FALLBACK_IMGS['economy'],   'CC0 / Unsplash (illustrative)'),
        ]
        for alt_url, alt_credit in alternates:
            if alt_url not in _USED_FALLBACKS:
                url, credit = alt_url, alt_credit
                break

    _USED_FALLBACKS.add(url)
    # Store locally
    if _USE_IMAGE_STORE:
        local = _store_img(url)
        if local and local != PLACEHOLDER:
            return local, credit
    return url, credit


# ─── HTML card builder ────────────────────────────────────────────────────────

def build_card(story, css_class='biz-card'):
    """Build a single HTML story card matching the site design."""
    fit = story.get('img_fit', 'cover')
    obj = "object-fit:contain;padding:16px;background:#111" if fit == 'contain' else "object-fit:cover;object-position:top center"
    cat = story.get('category', 'News')
    cat_color = story.get('cat_color', '#374151')
    credit = story.get('img_credit', '')
    headline = story.get('headline', story.get('title', 'Story'))
    summary = story.get('summary', story.get('desc', ''))
    return f'''    <article class="{css_class}">
      <a href="{story['url']}" target="_blank" rel="noopener" class="card-link">
        <div class="card-img-wrap">
          <img src="{story['img']}" alt="{re.sub(r'&[a-z]+;', '', headline)[:55]}" class="card-img" style="{obj}" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg';this.style='object-fit:contain;padding:20px;background:#111'">
          <span class="card-badge" style="background:{cat_color}">{cat}</span>
          <span class="card-credit">{credit}</span>
        </div>
        <div class="card-body">
          <div class="card-location">&#x1F4CD; {story.get('location', 'Florida')}</div>
          <h2 class="card-title">{headline}</h2>
          <p class="card-summary">{summary}</p>
          <div class="card-foot">
            <span class="card-source">{story.get('source_name', story.get('source', ''))}</span>
            <span class="card-date">{story.get('date', '')}</span>
          </div>
        </div>
      </a>
    </article>'''


def build_day_section(date_label, stories, css_class='biz-card'):
    """Build a dated section with a divider and card grid."""
    cards = '\n'.join(build_card(s, css_class) for s in stories)
    return f'''  <div class="day-sep">
    <div class="day-line"></div>
    <div class="day-label">Published</div>
    <div class="day-date">{date_label}</div>
    <div class="day-line"></div>
  </div>
  <div class="card-grid">
{cards}
  </div>
'''


# ─── Page injection ───────────────────────────────────────────────────────────

def inject_section_before(html, new_section, marker='<div class="day-sep">'):
    """Insert new_section before the first existing section (newest-first order)."""
    idx = html.find(marker)
    if idx == -1:
        # Find grid-wrap div and insert after it
        idx = html.find('<div class="grid-wrap">')
        if idx != -1:
            close = html.find('>', idx) + 1
            return html[:close] + '\n' + new_section + html[close:]
    return html[:idx] + new_section + '\n' + html[idx:]


def today_label():
    return datetime.utcnow().strftime('%B %d, %Y').replace(' 0',' ')
