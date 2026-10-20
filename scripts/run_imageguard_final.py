#!/usr/bin/env python3
"""Run ImageGuard for 3 FINAL politics stories - Oct 20, 2026"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()
results = {}

# Story 1: Florida AG Uthmeier secures arrest warrant for Raul Castro (Oct 19, 2026)
title1 = "Florida AG Uthmeier Secures State Arrest Warrant for Raúl Castro in 1996 Brothers to the Rescue Shootdown"
alts1 = [
    "https://www.myfloridalegal.com/newsrelease/attorney-general-james-uthmeier-secures-state-arrest-warrant-communist-dictator-cuba",
    "https://aljazeera.com/news/2026/10/19/florida-issues-arrest-warrant-for-cuban-leader-raul-castro",
    "https://oann.com/newsroom/fla-ag-obtains-arrest-warrant-for-fmr-cuban-leader-raul-castro-over-1996-shootdown-that-killed-4",
    "https://flvoicenews.com/uthmeier-announces-state-charge-against-raul-castro-in-1996-killings",
    "https://floridianpress.com/2026/10/florida-announces-arrest-warrant-for-former-cuban-leader-raul-castro",
    "https://wol.com/2026/10/19/florida-secures-arrest-warrant-for-raul-castro",
]
img1 = None
for url in alts1:
    img1 = guard.fetch_from_article(url, story_title=title1, used_on='section-politics.html')
    print(f"  {url}: {img1}")
    if img1:
        break
results['story1_castro'] = img1 or '/img/placeholder.svg'

# Story 2: Trump signs Women's Health executive order (Oct 19, 2026)
title2 = "Trump Signs Women's Health Executive Order, Creates New NIH Division and White House Task Force"
alts2 = [
    "https://apnews.com/article/melania-trump-womens-health-executive-order-47534d721ac1328832ca46d9286ca833",
    "https://www.hhs.gov/press-room/trump-flotus-womens-health-executive-order-new-nih-division.html",
    "https://www.whitehouse.gov/fact-sheets/2026/10/fact-sheet-president-donald-j-trump-and-first-lady-melania-trump-advance-womens-health-to-improve-outcomes-in-all-phases-of-life/",
]
img2 = None
for url in alts2:
    img2 = guard.fetch_from_article(url, story_title=title2, used_on='section-politics.html')
    print(f"  {url}: {img2}")
    if img2:
        break
results['story2_womenshealth'] = img2 or '/img/placeholder.svg'

# Story 3: Trump administration nearly approved Iran military strike (Oct 20, 2026)
title3 = "Trump Administration Came 'Very Close' to Approving Iran Strike Before Pulling Back"
alts3 = [
    "https://www.jpost.com/middle-east/iran-news/article-912315",
    "https://www.gate.com/news/detail/trump-administration-weighed-iran-military-strike-until-final-stage-25084614",
    "https://www.azernews.az/region/265913.html",
    "https://apnews.com/hub/donald-trump",
]
img3 = None
for url in alts3:
    img3 = guard.fetch_from_article(url, story_title=title3, used_on='section-politics.html')
    print(f"  {url}: {img3}")
    if img3:
        break
results['story3_iran'] = img3 or '/img/placeholder.svg'

guard.save_registry()
print("\n=== FINAL IMAGE RESULTS ===")
print(json.dumps(results, indent=2))
