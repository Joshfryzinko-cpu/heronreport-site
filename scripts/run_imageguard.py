#!/usr/bin/env python3
"""Run ImageGuard for 3 politics stories - Oct 20, 2026"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()
results = {}

# Story 1: Trump waives Russia sanctions (NBC News / AP, Oct 17, 2026)
title1 = "Trump Waives Russia Sanctions Days Before Deadline, Drawing Bipartisan Backlash"
url1 = "https://www.nbcnews.com/politics/trump-administration/trump-suspends-new-russia-sanctions-deal-purchase-diesel-citing-nation-rcna603991"
img1 = guard.fetch_from_article(url1, story_title=title1, used_on='section-politics.html')
print(f"Story 1 (NBC Russia sanctions): {img1}")
if img1 is None:
    for alt in [
        "https://apnews.com/article/russia-sanctions-trump-ukraine-e50c561ab805883bb4e484c092d8fadd",
        "https://www.bbc.com/news/articles/cxr5yvzv7rp0o",
        "https://www.wsj.com/politics/policy/trump-waives-most-russia-sanctions-passed-by-congress-4c36bc93"
    ]:
        img1 = guard.fetch_from_article(alt, story_title=title1, used_on='section-politics.html')
        print(f"  alt {alt}: {img1}")
        if img1:
            break
results['story1'] = img1 or '/img/placeholder.svg'

# Story 2: Florida DFS/ICE immigration enforcement at Pensacola Beach (Oct 15, 2026)
title2 = "ICE Denies Role in Florida Beach Roofer Confrontation — but State Officers Hold Immigration Powers"
url2 = "https://pnj.com/story/news/local/pensacola/beaches/2026/10/15/ice-denies-role-in-grand-marlin-incident-advocate-alleges-lies/92267710007"
img2 = guard.fetch_from_article(url2, story_title=title2, used_on='section-politics.html')
print(f"Story 2 (Pensacola ICE): {img2}")
if img2 is None:
    for alt in [
        "https://floridaphoenix.com/2026/10/15/florida-immigrant-coalition-supports-resolution-pressing-congress-to-tackle-immigration-policy",
        "https://floridatrend.com/feature/2026/10/16/immigration-ripples",
        "https://www.dhs.gov/news/2026/10/15/dhs-ice-enforcement-operations"
    ]:
        img2 = guard.fetch_from_article(alt, story_title=title2, used_on='section-politics.html')
        print(f"  alt {alt}: {img2}")
        if img2:
            break
results['story2'] = img2 or '/img/placeholder.svg'

# Story 3: National Energy Dominance Month (Oct 7, 2026)
title3 = "Trump Proclaims October National Energy Dominance Month, Cites Venezuela Oil Deal"
url3 = "https://www.whitehouse.gov/presidential-actions/2026/10/national-energy-dominance-month-2026/"
img3 = guard.fetch_from_article(url3, story_title=title3, used_on='section-politics.html')
print(f"Story 3 (WH Energy Dominance): {img3}")
if img3 is None:
    for alt in [
        "https://www.whitehouse.gov/fact-sheets/2026/08/fact-sheet-president-donald-j-trump-announces-historic-oil-agreement-to-secure-american-energy-dominance-and-drive-venezuelas-economic-recovery",
        "https://energy.gov/articles/energy-dominance-2026"
    ]:
        img3 = guard.fetch_from_article(alt, story_title=title3, used_on='section-politics.html')
        print(f"  alt {alt}: {img3}")
        if img3:
            break
results['story3'] = img3 or '/img/placeholder.svg'

guard.save_registry()
print("\n=== FINAL RESULTS ===")
print(json.dumps(results, indent=2))
