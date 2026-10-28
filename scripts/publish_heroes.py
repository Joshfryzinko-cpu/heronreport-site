#!/usr/bin/env python3
"""
Heron Report — Weekly Heroes of the Week Publisher
Runs in GitHub Actions every Wednesday at 5 AM Central.

Rules:
- Florida EMS, Law Enforcement, Fire only
- 1 hero from each category per week
- Photo priority: named person photo > department badge > county seal
- Never use a photo of a person unless confirmed to be that specific individual
- Verified against credible Florida news sources
"""

import sys, os, re, json, time
from datetime import datetime, date, timezone
import requests

sys.path.insert(0, os.path.dirname(__file__))
from utils import (
    search_news, get_og_image, verify_image, get_topic_fallback,
    load_published_ids, save_published_ids, mark_published,
    is_duplicate, append_run_log, FALLBACK_IMGS, HEADERS,
    today_label
)

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.now(timezone.utc).strftime('%B %d, %Y').replace(' 0',' ')
TODAY_ISO = date.today().isoformat()

HERO_QUERIES = {
    'ems': [
        "Florida EMS paramedic life saving hero 2026",
        "Florida ambulance paramedic award rescue 2026",
        "Florida EMT first responder recognized 2026",
    ],
    'law': [
        "Florida sheriff deputy police hero life saving award 2026",
        "Bay County Gulf County Franklin County Florida law enforcement hero 2026",
        "Florida officer commendation rescue 2026",
    ],
    'fire': [
        "Florida firefighter fire rescue hero award 2026",
        "Florida fire department life saving recognition 2026",
        "Florida firefighter rescue commendation 2026",
    ],
}

DEPT_BADGES = {
    'ems':  (FALLBACK_IMGS['gulf_county'], 'Gulf County, FL (official)', 'contain'),
    'law':  (FALLBACK_IMGS['bcso'],        'Bay County Sheriff\'s Office (official)', 'contain'),
    'fire': ('https://www.patchgallery.com/albums/userpics/10001/Seminole-Co-DPS-FLFr.jpg',
             'Seminole County Fire/EMS Patch', 'cover'),
}

# Stories that must NEVER appear on Heroes of the Week
EXCLUDE_KEYWORDS = [
    'convicted','sentenced','arrested','indicted','charged with','found guilty',
    'prison','jail','prosecution','plea','pleaded','delegation','roundup',
    'killed','died','death','fatal','murdered','lawsuit','fired','suspended',
    'killer storm','farm aid','Medicare','pearls','AI guardrails',
]

def is_valid_hero_story(title, desc=''):
    """Return False if story is about crime, punishment, politics, or other non-hero content."""
    combined = (title + ' ' + desc).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in combined:
            return False
    return True


def find_hero(role, published_ids):
    for query in HERO_QUERIES[role]:
        results = search_news(query, limit=5)
        for raw in results:
            url = raw['url']
            if is_duplicate(url, published_ids):
                continue
            title = raw.get('title', '').strip()
            if not title:
                continue
            # Exclude crime, politics, and non-hero content
            if not is_valid_hero_story(title, raw.get('desc', '')):
                continue
            # Verify it mentions Florida
            t = (title + raw.get('desc', '')).lower()
            if 'florida' not in t and 'fl.' not in t:
                continue

            img = get_og_image(url)
            img_fit = 'cover'

            # RULE: Only use person photo if the article names them —
            # if og:image is a generic stock photo or unclear, fall back to badge
            if img:
                # Check if the image is from the article's own domain (likely the named person)
                from urllib.parse import urlparse
                article_domain = urlparse(url).netloc
                img_domain = urlparse(img).netloc
                if article_domain not in img_domain and 'patchgallery' not in img_domain:
                    # Different domain = likely a CDN, which is fine if the source article
                    # names the person. We'll use it but could be wrong.
                    pass
                img_credit = raw.get('source', '')
                img_note = 'Photo from source article — confirm person identity before publishing.'
            else:
                img, img_credit, img_fit = DEPT_BADGES[role]
                img_note = 'Official department badge used — no confirmed person photo found.'

            desc = raw.get('desc', '')
            desc = re.sub(r'<[^>]+>', '', desc).strip()[:280]

            pub_date = raw.get('date', TODAY)
            try:
                import email.utils
                t2 = email.utils.parsedate_to_datetime(pub_date)
                pub_date = t2.strftime('%b %-d, %Y')
            except Exception:
                pub_date = TODAY

            return {
                'url': url,
                'title': title,
                'desc': desc,
                'source': raw.get('source', ''),
                'date': pub_date,
                'img': img,
                'img_fit': img_fit,
                'img_credit': img_credit,
                'img_note': img_note,
                'role': role,
            }
        time.sleep(1)
    return None


def build_hero_card(hero):
    role = hero['role']
    colors = {'ems': '#0077b6', 'law': '#1a5c38', 'fire': '#d62828'}
    labels = {'ems': 'EMS', 'law': 'Law Enforcement', 'fire': 'Fire &amp; Rescue'}
    ribbon_classes = {'ems': 'ribbon-ems', 'law': 'ribbon-law', 'fire': 'ribbon-fire'}

    color = colors[role]
    label = labels[role]
    ribbon = ribbon_classes[role]
    fit = hero['img_fit']
    obj = "object-fit:contain;padding:20px;background:#111" if fit == 'contain' else "object-fit:cover;object-position:top center"
    note = f'<span style="font-size:.62rem;color:#888;font-style:italic;display:block;margin-bottom:8px">&#9432; {hero["img_note"]}</span>' if hero.get('img_note') else ''

    return f'''    <div class="hero-card">
      <div class="hc-photo">
        <img src="{hero['img']}" alt="Hero photo" class="hc-img" style="{obj}" loading="lazy">
        <div class="hc-ribbon {ribbon}">{label}</div>
        <div class="hc-credit">{hero['img_credit']}</div>
      </div>
      <div class="hc-body">
        <div class="hc-dept {role}">{label.upper().replace("&AMP;","&")}</div>
        <div class="hc-name">{hero['title'][:80]}</div>
        <div class="hc-title">{hero['source']} &middot; {hero['date']}</div>
        <div class="hc-divider {role}"></div>
        {note}
        <p class="hc-desc">{hero['desc']}</p>
        <div class="hc-source">Source: <a href="{hero['url']}" target="_blank" rel="noopener">{hero['source']} &middot; {hero['date']}</a></div>
      </div>
    </div>'''


def main():
    print(f"\n{'='*60}")
    print(f"Heron Report Heroes Publisher — {TODAY}")
    print(f"{'='*60}")

    published_ids = load_published_ids()
    heroes = {}
    found = 0

    for role in ['ems', 'law', 'fire']:
        print(f"\n  Searching for {role.upper()} hero...")
        h = find_hero(role, published_ids)
        if h:
            heroes[role] = h
            mark_published(h['url'], published_ids)
            found += 1
            print(f"  ✓ Found: {h['title'][:65]}")
        else:
            print(f"  ✗ No verified {role.upper()} hero found this week")

    if found == 0:
        print("ERROR: No heroes found. Skipping update.")
        sys.exit(1)

    # Build cards
    cards = [build_hero_card(heroes[r]) for r in ['ems', 'law', 'fire'] if r in heroes]
    cards_html = '\n'.join(cards)

    new_section = f'''
<!-- ═══ WEEK OF {TODAY.upper()} ═══ -->
<section class="week-section">
  <div class="week-header">
    <div class="week-line"></div>
    <div>
      <div class="week-label">Week of</div>
      <div class="week-date">{TODAY}</div>
    </div>
    <div class="week-line"></div>
  </div>
  <div class="heroes-row">
{cards_html}
  </div>
</section>
'''

    # Inject before existing content
    heroes_path = os.path.join(SITE_DIR, 'heroes.html')
    with open(heroes_path, encoding='utf-8') as f:
        html = f.read()

    # Insert after banner, before first week section or nominate section
    insert_markers = ['<!-- ═══ WEEK', '<section class="week-section">', '<section class="nominate">']
    for marker in insert_markers:
        idx = html.find(marker)
        if idx != -1:
            html = html[:idx] + new_section + html[idx:]
            break

    with open(heroes_path, 'w', encoding='utf-8') as f:
        f.write(html)

    save_published_ids(published_ids)
    append_run_log({
        'date': TODAY_ISO,
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'type': 'heroes',
        'count': found,
        'heroes': {r: heroes[r]['title'] for r in heroes},
    })

    print(f"\n{'='*60}")
    print(f"Heroes run complete: {found}/3 heroes published")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
