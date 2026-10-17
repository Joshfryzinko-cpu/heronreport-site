#!/usr/bin/env python3
"""
Heron Report — Daily Publishing Script
Runs in GitHub Actions. Publishes 3 new stories to each of:
  - section-politics.html
  - section-business.html
  - section-investigations.html

Rules per page follow the editorial guidelines set for The Heron Report.
No stories are deleted. New sections are prepended (newest-first).
Deduplication prevents republishing the same article URL.
"""

import sys, os, re, json, time
from datetime import datetime, date, timezone
import requests

sys.path.insert(0, os.path.dirname(__file__))
from utils import (
    search_news, get_og_image, verify_image, get_topic_fallback,
    build_day_section, inject_section_before, today_label,
    load_published_ids, save_published_ids, mark_published,
    is_duplicate, append_run_log, FALLBACK_IMGS, HEADERS
)

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.now(timezone.utc).strftime('%B %d, %Y').replace(' 0',' ')
TODAY_ISO = date.today().isoformat()

# ─── Story Queries ────────────────────────────────────────────────────────────

POLITICS_QUERIES = [
    # Top 10 administration figures — one query each
    "JD Vance vice president news 2026",
    "Marco Rubio secretary of state foreign policy news 2026",
    "Pete Hegseth secretary defense Pentagon news 2026",
    "Pam Bondi attorney general DOJ news 2026",
    "Kristi Noem DHS homeland security border news 2026",
    "Scott Bessent treasury secretary economy tariffs 2026",
    "Robert F Kennedy RFK HHS health department news 2026",
    "Doug Burgum interior energy department news 2026",
    "Elon Musk DOGE government efficiency news 2026",
    "Brooke Rollins USDA agriculture secretary news 2026",
    # National security / military
    "US military national security war news 2026",
    "Ukraine Russia war ceasefire news 2026",
    "Israel Iran Middle East conflict 2026",
    # Economy / energy
    "oil gas energy prices economy news October 2026",
    "federal spending budget deficit Congress 2026",
    # Immigration
    "border immigration enforcement deportation news 2026",
    # Florida local heroes
    "Bay County Gulf County Franklin County Florida sheriff fire rescue 2026",
    # Trump — limited (only 2 per day max, enforced in publish logic)
    "Trump executive order White House policy news 2026",
]

# Max Trump-specific articles per daily publish run
MAX_TRUMP_PER_RUN = 2
# Max total articles shown on Politics page at one time
MAX_POLITICS_ARTICLES = 18

BUSINESS_QUERIES = [
    "Florida entrepreneur small business success story 2026",
    "Florida startup founder growth 2026",
    "Florida Hispanic woman veteran owned business 2026",
    "Florida business award recognition 2026",
    "Florida restaurant shop opens expands 2026",
    "Florida local business community story 2026",
]

INVESTIGATIONS_QUERIES = [
    "Florida government corruption fraud investigation 2026",
    "federal official indicted charged fraud 2026",
    "taxpayer waste government accountability 2026",
    "Florida public official misconduct arrested 2026",
    "DOJ FBI investigation corruption 2026",
    "government contractor fraud abuse 2026",
]

# ─── Category Config ─────────────────────────────────────────────────────────

def categorize_politics(title, url):
    t = title.lower()
    # Cabinet / administration officials
    if any(k in t for k in ['hegseth','pentagon','defense department','secretary of defense']):
        return 'Pentagon / Defense', '#7c2d12'
    if any(k in t for k in ['rubio','secretary of state','state department','diplomacy','foreign policy']):
        return 'Foreign Policy', '#374151'
    if any(k in t for k in ['bondi','attorney general','doj','department of justice']):
        return 'DOJ', '#7c2d12'
    if any(k in t for k in ['noem','dhs','homeland security','ice','border patrol']):
        return 'Border / DHS', '#b91c1c'
    if any(k in t for k in ['bessent','treasury','tariff','trade','federal reserve']):
        return 'Economy / Treasury', '#1e3a8a'
    if any(k in t for k in ['kennedy','rfk','hhs','health','fda','cdc','vaccines']):
        return 'Health / HHS', '#166534'
    if any(k in t for k in ['burgum','interior','energy department','epa','natural resources']):
        return 'Energy / Interior', '#166534'
    if any(k in t for k in ['rollins','usda','agriculture','farm','food supply']):
        return 'Agriculture', '#166534'
    if any(k in t for k in ['vance','white house','administration','cabinet','executive']):
        return 'Administration', '#b91c1c'
    # Trump directly
    if any(k in t for k in ['trump','executive order','president']):
        return 'Trump / Policy', '#b91c1c'
    if any(k in t for k in ['war','military','ukraine','russia','nato','israel','iran','defense']):
        return 'War / Security', '#7c2d12'
    if any(k in t for k in ['oil','gas','energy','fuel','diesel']):
        return 'Energy', '#166534'
    if any(k in t for k in ['economy','inflation','fed','spending','budget','debt']):
        return 'Economy', '#1e3a8a'
    if any(k in t for k in ['sheriff','fire','ems','rescue','bay county','gulf county','franklin']):
        return 'Local Hero — FL Panhandle', '#0f766e'
    if any(k in t for k in ['border','immigration','deportation']):
        return 'Border / Immigration', '#b91c1c'
    return 'Politics', '#374151'

def categorize_business(title):
    t = title.lower()
    if any(k in t for k in ['restaurant','coffee','food','cafe','bar']):
        return 'Restaurant', '#166534'
    if any(k in t for k in ['startup','tech','ai','software','app']):
        return 'Startup', '#1e3a8a'
    if any(k in t for k in ['franchise','expand','opens','growth','new location']):
        return 'Expansion', '#0f766e'
    if any(k in t for k in ['award','entrepreneur','honor','recogni']):
        return 'Entrepreneur', '#7c2d12'
    if any(k in t for k in ['veteran','military']):
        return 'Veteran-Owned', '#374151'
    return 'Small Business', '#166534'

def categorize_investigation(title):
    t = title.lower()
    if any(k in t for k in ['florida','orlando','miami','tampa','jacksonville','bay county','gulf county']):
        return 'Florida', '#c2410c'
    if any(k in t for k in ['fbi','doj','federal','cia']):
        return 'Federal', '#1e3a8a'
    if any(k in t for k in ['fraud','embezzle','steal','theft']):
        return 'Fraud / Theft', '#7c2d12'
    if any(k in t for k in ['corruption','misconduct','abuse']):
        return 'Misconduct', '#7c3aed'
    return 'Investigation', '#374151'


# ─── Story Processor ─────────────────────────────────────────────────────────

def process_story(raw, page_type, published_ids):
    url = raw['url']
    if is_duplicate(url, published_ids):
        return None

    title = raw.get('title', '').strip()
    if not title or len(title) < 15:
        return None

    # Get article image
    img = get_og_image(url)
    img_fit = 'cover'
    img_credit = raw.get('source', '')

    if not img:
        topic_hint = f"{page_type} {title}"
        img, img_credit = get_topic_fallback(topic_hint)
        img_fit = 'contain' if any(k in img for k in ['seal','badge','svg','logo']) else 'cover'

    # Build summary from RSS description
    desc = raw.get('desc', '')
    if desc:
        # Strip HTML tags from description
        desc = re.sub(r'<[^>]+>', '', desc).strip()
        if len(desc) > 300:
            desc = desc[:300].rsplit(' ', 1)[0] + '…'
    else:
        desc = f"Read the full story at {raw.get('source', 'the source')}."

    # Parse date
    pub_date = raw.get('date', '')
    try:
        import email.utils
        t = email.utils.parsedate_to_datetime(pub_date)
        pub_date = t.strftime('%b %-d, %Y')
    except Exception:
        pub_date = TODAY

    return {
        'url': url,
        'headline': title,
        'summary': desc,
        'source_name': raw.get('source', ''),
        'date': pub_date,
        'img': img,
        'img_fit': img_fit,
        'img_credit': img_credit,
        'location': detect_location(title),
    }

def detect_location(title):
    t = title.lower()
    locations = {
        'miami': 'Miami, FL', 'orlando': 'Orlando, FL', 'tampa': 'Tampa, FL',
        'jacksonville': 'Jacksonville, FL', 'tallahassee': 'Tallahassee, FL',
        'pensacola': 'Pensacola, FL', 'fort lauderdale': 'Fort Lauderdale, FL',
        'bay county': 'Bay County, FL', 'gulf county': 'Gulf County, FL',
        'franklin county': 'Franklin County, FL', 'panama city': 'Panama City, FL',
        'clearwater': 'Clearwater, FL', 'sarasota': 'Sarasota, FL',
        'washington': 'Washington, D.C.', 'white house': 'Washington, D.C.',
        'florida': 'Florida',
    }
    for key, val in locations.items():
        if key in t:
            return val
    return 'National'


# ─── Per-page publishers ──────────────────────────────────────────────────────

def prune_to_max_articles(html, max_articles, css_class):
    """Remove oldest day-sections to keep total article count at max_articles."""
    import re
    cards = re.findall(rf'<article\b[^>]*class="{css_class}"[^>]*>.*?</article>', html, re.DOTALL)
    if len(cards) <= max_articles:
        return html
    # Find and remove the oldest day-sections from the bottom
    sections = re.findall(r'<div class="day-sep">.*?</div>\s*<div class="card-grid">.*?</div>', html, re.DOTALL)
    excess = len(cards) - max_articles
    removed = 0
    for section in reversed(sections):
        section_cards = re.findall(rf'<article\b[^>]*class="{css_class}"', section)
        if removed >= excess:
            break
        html = html.replace(section, '', 1)
        removed += len(section_cards)
    return html

def find_stories(queries, page_type, published_ids, target=3, max_per_query=4):
    """Search queries until we have `target` new unique stories.
    For politics: caps Trump-named stories at MAX_TRUMP_PER_RUN.
    """
    collected = []
    trump_count = 0

    for query in queries:
        if len(collected) >= target:
            break
        results = search_news(query, limit=max_per_query)
        for raw in results:
            if len(collected) >= target:
                break
            # Cap Trump-specific articles
            if page_type == 'politics':
                title_l = raw.get('title','').lower()
                is_trump = 'trump' in title_l
                if is_trump and trump_count >= MAX_TRUMP_PER_RUN:
                    continue
                story = process_story(raw, page_type, published_ids)
                if story:
                    if is_trump:
                        trump_count += 1
                    collected.append(story)
            else:
                story = process_story(raw, page_type, published_ids)
                if story:
                    collected.append(story)
        time.sleep(1)
    return collected[:target]

def publish_page(filename, queries, page_type, css_class, categorizer, published_ids):
    path = os.path.join(SITE_DIR, filename)
    if not os.path.exists(path):
        print(f"  ERROR: {filename} not found")
        return 0, []

    print(f"\n  → {filename}")
    stories = find_stories(queries, page_type, published_ids)

    if len(stories) < 3:
        print(f"  ⚠ Only found {len(stories)}/3 new stories (shortage)")
        if not stories:
            return 0, []

    # Apply category colors
    for s in stories:
        cat, color = categorizer(s['headline'])
        s['category'] = cat
        s['cat_color'] = color

    with open(path, encoding='utf-8') as f:
        html = f.read()

    section = build_day_section(TODAY, stories, css_class)
    html = inject_section_before(html, section)

    # Prune to MAX_POLITICS_ARTICLES total if this is the politics page
    if page_type == 'politics':
        html = prune_to_max_articles(html, MAX_POLITICS_ARTICLES, css_class)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    urls = [s['url'] for s in stories]
    for s in stories:
        mark_published(s['url'], published_ids)

    print(f"  ✓ {len(stories)} stories added to {filename}")
    for s in stories:
        print(f"    • {s['headline'][:65]}")

    return len(stories), urls


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"Heron Report Daily Publisher — {TODAY}")
    print(f"{'='*60}")

    published_ids = load_published_ids()
    run_entry = {
        'date': TODAY_ISO,
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'pages': {},
        'errors': [],
    }

    # Politics
    n, urls = publish_page(
        'section-politics.html', POLITICS_QUERIES, 'politics',
        'pol-card', lambda t: categorize_politics(t, ''), published_ids
    )
    run_entry['pages']['politics'] = {'count': n, 'urls': urls}

    # Business
    n, urls = publish_page(
        'section-business.html', BUSINESS_QUERIES, 'business',
        'biz-card', lambda t: (categorize_business(t), '#166534'), published_ids
    )
    # Fix: categorize_business returns just the category string, not a tuple
    run_entry['pages']['business'] = {'count': n, 'urls': urls}

    # Investigations
    n, urls = publish_page(
        'section-investigations.html', INVESTIGATIONS_QUERIES, 'investigations',
        'inv-card', lambda t: categorize_investigation(t), published_ids
    )
    run_entry['pages']['investigations'] = {'count': n, 'urls': urls}

    # Save dedup state and log
    save_published_ids(published_ids)
    append_run_log(run_entry)

    total = sum(v.get('count', 0) for v in run_entry['pages'].values())
    print(f"\n{'='*60}")
    print(f"Run complete: {total} stories published across 3 pages")
    print(f"{'='*60}\n")

    if total == 0:
        print("ERROR: No stories published. Check search connectivity.")
        sys.exit(1)


if __name__ == '__main__':
    main()
