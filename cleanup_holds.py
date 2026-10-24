#!/usr/bin/env python3
"""Remove story cards that still have wrong/unrelated images per editorial rules."""
import re
import os

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"

def remove_cards(html, titles_to_remove):
    """Remove article cards containing any of the given titles."""
    art_pattern = re.compile(r'<article class="biz-card"[^>]*>.*?</article>', re.DOTALL)
    matches = list(art_pattern.finditer(html))
    
    to_remove = []
    for m in matches:
        text = m.group(0)
        for title in titles_to_remove:
            if title in text:
                to_remove.append(m)
                print(f"  Removing card: {title[:60]}")
                break
    
    # Remove from end to start
    for m in sorted(to_remove, key=lambda x: x.start(), reverse=True):
        html = html[:m.start()] + html[m.end():]
    
    return html

biz_path = os.path.join(SITE, "section-business.html")
with open(biz_path, 'r', encoding='utf-8') as f:
    content = f.read()

orig = content

# Remove cards with wrong/unrelated images
content = remove_cards(content, [
    "Florida Garage Door Pros Named 2026 Best of Florida Award Winner",  # had Big Mac image
    "See the region's top Hispanic and Latino-owned businesses",           # had mobile phone image
    "Florida family restaurant expands from Palm Beach County after 53 years",  # had Big Mac image
])

# Verify a4c090e6ad50aeac (Big Mac) no longer appears (should be 0 after removals)
count_bigmac = content.count('a4c090e6ad50aeac')
count_mobile = content.count('9126b639fa7c1d11')
print(f"\nAfter removals: Big Mac image count={count_bigmac}, Mobile image count={count_mobile}")

if content != orig:
    with open(biz_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SAVED section-business.html")

# Verify final image usage on business page
print("\nFinal image check on business page (looking for remaining duplicates):")
import re
imgs = re.findall(r'src="/img/stories/([^"]+)"', content)
from collections import Counter
counts = Counter(imgs)
dups = {k: v for k, v in counts.items() if v > 1}
if dups:
    print("DUPLICATES FOUND:")
    for img, cnt in dups.items():
        print(f"  {img}: {cnt}x")
else:
    print("  No duplicates on business page!")

# Also check mobile phone and big mac not on other pages
for page in ['section-politics.html', 'section-investigations.html', 'index.html']:
    path = os.path.join(SITE, page)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            pg = f.read()
        for img in ['a4c090e6ad50aeac', '9126b639fa7c1d11']:
            if img in pg:
                print(f"WARNING: {img} found in {page}")
    except:
        pass

print("\nDone.")
