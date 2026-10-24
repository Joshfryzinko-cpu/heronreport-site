#!/usr/bin/env python3
"""Final comprehensive cross-site image duplicate audit."""
import re
import os
from collections import defaultdict

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"

pages = [
    'index.html',
    'section-politics.html', 
    'section-business.html',
    'section-investigations.html',
    'heroes.html',
    'aj-smith-franklin-county.html',
    'amber-williams.html',
    'amendment-3-homestead-exemption.html',
]

# Collect all img srcs (exclude data: URIs and logos)
img_usage = defaultdict(list)  # img -> [pages]

for page in pages:
    path = os.path.join(SITE, page)
    if not os.path.exists(path):
        print(f"MISSING: {page}")
        continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find all img src pointing to /img/stories/
    imgs = re.findall(r'src="/img/stories/([^"]+)"', html)
    
    # Find within-page duplicates
    from collections import Counter
    page_counts = Counter(imgs)
    within_dups = {k: v for k, v in page_counts.items() if v > 1}
    if within_dups:
        print(f"\nWITHIN-PAGE DUPLICATES in {page}:")
        for img, cnt in within_dups.items():
            # Find context
            matches = [(m.start(), html[max(0,m.start()-200):m.start()+200]) 
                      for m in re.finditer(re.escape(img), html)]
            for pos, ctx in matches:
                titles = re.findall(r'card-title[^>]*>([^<]+)<', ctx)
                if titles:
                    print(f"  {img}: {titles[0][:50]}")
    
    for img in set(imgs):
        img_usage[img].append(page)

# Cross-page duplicates
print("\nCROSS-PAGE DUPLICATES (story images used on multiple different pages):")
found_any = False
for img, pages_used in img_usage.items():
    if len(pages_used) > 1:
        # Exclude logo/brand images that are intentionally shared
        if 'b6a8752ca101efbf' in img:  # Dryer 911 ad
            continue
        found_any = True
        print(f"  {img}: {' | '.join(pages_used)}")

if not found_any:
    print("  NONE FOUND")

# Check for known bad patterns
print("\nBAD IMAGE CREDITS CHECK:")
bad_patterns = [
    ("FDLE on non-law-enforcement story", 'Florida Dept. of Law Enforcement', 
     r'card-credit[^>]*>Florida Dept\. of Law Enforcement.*?card-title[^>]*>([^<]+)', re.DOTALL),
    ("Bay County Sheriff on non-sheriff story",
     "Bay County Sheriff's Office",
     r"card-credit[^>]*>Bay County Sheriff.*?card-title[^>]*>([^<]+)", re.DOTALL),
]

for page in ['section-business.html', 'section-politics.html', 'section-investigations.html']:
    path = os.path.join(SITE, page)
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    fdle_count = html.count("Florida Dept. of Law Enforcement")
    bcso_count = html.count("Bay County Sheriff's Office")
    
    if fdle_count > 0 or bcso_count > 0:
        print(f"  {page}: FDLE mentions={fdle_count}, BCSO mentions={bcso_count}")
        # Show context
        for pattern in ["Florida Dept. of Law Enforcement", "Bay County Sheriff's Office"]:
            if pattern in html:
                idx = html.find(pattern)
                ctx = html[max(0,idx-300):idx+300]
                title = re.search(r'card-title[^>]*>([^<]+)', ctx)
                if title:
                    print(f"    -> Story: {title.group(1)[:60]}")

print("\nSUMMARY STATS:")
for page in pages:
    path = os.path.join(SITE, page)
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    imgs = re.findall(r'src="/img/stories/([^"]+)"', html)
    cards_titles = re.findall(r'card-title[^>]*>([^<]+)', html)
    print(f"  {page}: {len(imgs)} images, {len(cards_titles)} titles")

print("\nDONE - All checks complete")
