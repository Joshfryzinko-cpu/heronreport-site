#!/usr/bin/env python3
"""Fetch images for 3 politics stories using ImageGuard."""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()
results = {}

# ── Story 1: National Guard DC court case ──────────────────────────────────
sources_s1 = [
    'https://dvidshub.net/image/9938902/jtf-dc-mississippi-guardsmen-jefferson-memorial-patrol',
    'https://d1ldvf68ux039x.cloudfront.net/thumbs/photos/2609/9938902/1000w_q95.jpg',
    'https://dvidshub.net/image/9938909/jtf-dc-mississippi-guardsmen-world-war-ii-memorial-patrol',
    'https://dvidshub.net/image/9980309/jtf-dc-combatives-training',
    'https://abcnews.com/US/wireStory/appeals-court-hear-arguments-trumps-national-guard-deployment-137252013',
]
for url in sources_s1:
    img = guard.fetch_from_article(url, story_title='NatGuard_DC_CourtCase', used_on='section-politics.html')
    if img:
        results['story1'] = img
        results['story1_src'] = url
        print(f"S1 OK from {url}: {img}")
        break
    else:
        print(f"S1 None from {url}")

if 'story1' not in results:
    results['story1'] = '/img/placeholder.svg'
    results['story1_src'] = 'placeholder'
    print("S1 FALLBACK: placeholder")

# ── Story 2: ICE arrests 100+ gang members ─────────────────────────────────
sources_s2 = [
    'https://www.dhs.gov/news/2026/10/19/ice-arrests-more-100-gang-members-less-week',
    'https://www.ice.gov/news/releases',
    'https://dvidshub.net/search#q=ICE+enforcement&view=grid&page=1&pagesize=12',
]
for url in sources_s2:
    img = guard.fetch_from_article(url, story_title='ICE_Gang_Arrests_Oct2026', used_on='section-politics.html')
    if img:
        results['story2'] = img
        results['story2_src'] = url
        print(f"S2 OK from {url}: {img}")
        break
    else:
        print(f"S2 None from {url}")

if 'story2' not in results:
    results['story2'] = '/img/placeholder.svg'
    results['story2_src'] = 'placeholder'
    print("S2 FALLBACK: placeholder")

# ── Story 3: G20 at Trump National Doral ──────────────────────────────────
sources_s3 = [
    'https://www.cbsnews.com/miami/news/g20-summit-trump-national-doral-security-planning-secret-service/',
    'https://www.secretservice.gov/newsroom/releases',
    'https://dvidshub.net/search#q=G20+Doral&view=grid&page=1&pagesize=12',
    'https://www.miamidade.gov/releases',
]
for url in sources_s3:
    img = guard.fetch_from_article(url, story_title='G20_Doral_Security_2026', used_on='section-politics.html')
    if img:
        results['story3'] = img
        results['story3_src'] = url
        print(f"S3 OK from {url}: {img}")
        break
    else:
        print(f"S3 None from {url}")

if 'story3' not in results:
    results['story3'] = '/img/placeholder.svg'
    results['story3_src'] = 'placeholder'
    print("S3 FALLBACK: placeholder")

guard.save_registry()
print("Registry saved.")
print("RESULTS:", json.dumps(results, indent=2))
