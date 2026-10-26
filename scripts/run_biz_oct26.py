#!/usr/bin/env python3
"""Run ImageGuard for 3 business stories - Oct 26, 2026"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()
results = {}

# Story 1: Blue Origin $330M Florida expansion
title1 = "Blue Origin Announces $330 Million Florida Expansion to Boost New Glenn Production"
url1 = "https://cnbc.com/2026/10/16/blue-origin-new-glenn-florida-expansion.html"
img1 = guard.fetch_from_article(url1, story_title=title1, used_on='section-business.html')
print(f"Story 1 (Blue Origin CNBC): {img1}")
if img1 is None:
    for alt in [
        "https://webpronews.com/blue-origin-announces-330-million-florida-expansion-to-boost-new-glenn-production-and-launch-cadence",
        "https://satnews.com/2026/10/20/blue-origin-florida-infrastructure-investment-tops-3-billion-ahead-of-high-cadence-new-glenn-operations",
        "https://qz.com/blue-origin-330-million-florida-expansion-new-glenn-101626",
        "https://www.blueorigin.com/news/building-infrastructure-for-more-frequent-launches-in-florida"
    ]:
        img1 = guard.fetch_from_article(alt, story_title=title1, used_on='section-business.html')
        print(f"  alt {alt[:60]}: {img1}")
        if img1:
            break
results['story1'] = img1 or '/img/placeholder.svg'

# Story 2: Broward Business Boom - Greater Fort Lauderdale Alliance
title2 = "Broward Business Boom: Greater Fort Lauderdale Alliance Reports $318M Investment and 1,116 New Jobs"
url2 = "https://www.gflalliance.org/news/2026/10/20/in-the-news/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says/"
img2 = guard.fetch_from_article(url2, story_title=title2, used_on='section-business.html')
print(f"Story 2 (GFL Alliance): {img2}")
if img2 is None:
    for alt in [
        "https://www.bizjournals.com/southflorida/news/2026/10/20/greater-fort-lauderdale-alliance-annual-meeting.html",
        "https://www.sun-sentinel.com/2026/10/20/broward-business-boom-greater-fort-lauderdale-alliance",
        "https://www.bizjournals.com/southflorida/",
        "https://www.broward.org/economicdevelopment"
    ]:
        img2 = guard.fetch_from_article(alt, story_title=title2, used_on='section-business.html')
        print(f"  alt {alt[:60]}: {img2}")
        if img2:
            break
results['story2'] = img2 or '/img/placeholder.svg'

# Story 3: Dream Finders Homes completes Beazer acquisition
title3 = "Dream Finders Homes Completes $915 Million Beazer Acquisition, Becomes Sixth-Largest U.S. Homebuilder"
url3 = "https://investors.dreamfindershomes.com/news-events/press-releases/detail/70/dream-finders-homes-completes-acquisition-of-beazer-homes"
img3 = guard.fetch_from_article(url3, story_title=title3, used_on='section-business.html')
print(f"Story 3 (Dream Finders): {img3}")
if img3 is None:
    for alt in [
        "https://ir.beazer.com/news-releases/news-release-details/dream-finders-homes-acquire-beazer-homes-creating-sixth-largest",
        "https://www.bizjournals.com/jacksonville/news/2026/10/20/dream-finders-beazer-acquisition-complete.html",
        "https://www.jaxdailyrecord.com/news/2026/oct/21/dream-finders-completes-beazer-acquisition/",
        "https://www.businesswire.com/news/home/20261020/dream-finders-homes-completes-beazer-acquisition"
    ]:
        img3 = guard.fetch_from_article(alt, story_title=title3, used_on='section-business.html')
        print(f"  alt {alt[:60]}: {img3}")
        if img3:
            break
results['story3'] = img3 or '/img/placeholder.svg'

guard.save_registry()
print("\n=== FINAL RESULTS ===")
print(json.dumps(results, indent=2))
