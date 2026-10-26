#!/usr/bin/env python3
"""Run ImageGuard for story 2 (Broward) - retry with more sources + fallback"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()
results = {}

# Story 2 retry: Broward Business Boom
title2 = "Broward Business Boom: Greater Fort Lauderdale Alliance Reports $318M Investment and 1,116 New Jobs"
urls_to_try = [
    "https://www.sun-sentinel.com/2026/10/15/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says/",
    "https://www.gflalliance.org/",
    "https://www.facebook.com/TravelhostFTL/posts/business-is-booming-in-greater-fort-lauderdale",
]
img2 = None
for u in urls_to_try:
    img2 = guard.fetch_from_article(u, story_title=title2, used_on='section-business.html')
    print(f"  {u[:70]}: {img2}")
    if img2:
        break

# Fallback: Florida minimum wage $15/hr story
if img2 is None:
    print("Switching to FL minimum wage story...")
    title2 = "Florida Minimum Wage Hits $15 an Hour, Completing Six-Year Phase-In"
    for u in [
        "https://thefalconswire.usatoday.com/story/news/state/2026/10/01/floridas-minimum-wage-rose-15-dollars-hour-cost-consumers/91696185007",
        "https://wusf.org/the-florida-roundup/2026-10-05/how-florida-minimum-wage-increase-affect-workers-businesses",
        "https://pulseofmanatee.com/p/florida-minimum-wage-reaches-15-an",
        "https://theconservativerecord.com/florida-minimum-wage-hits-15-an-hour-what-workers-and-businesses-pay",
    ]:
        img2 = guard.fetch_from_article(u, story_title=title2, used_on='section-business.html')
        print(f"  minwage {u[:70]}: {img2}")
        if img2:
            break

results['story2'] = img2 or '/img/placeholder.svg'
results['title2'] = title2

guard.save_registry()
print("\n=== STORY 2 RESULT ===")
print(json.dumps(results, indent=2))
