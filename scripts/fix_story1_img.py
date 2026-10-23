#!/usr/bin/env python3
"""Fix Story 1 image - replace DOE seal with a real news photo."""
import sys, hashlib
from pathlib import Path
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

story1_title = "Trump Invokes Defense Production Act to Boost Oil Refinery Capacity"

# Remove the bad DOE seal image from registry so it's available to other stories if needed
# Actually just delete and try a better one
bad_local = '/img/stories/0450c11ad9a76d5e.png'
bad_path = Path("C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site") / bad_local.lstrip('/')

# Remove bad entry from registry
guard._entries = [e for e in guard._entries if e.get('local_path') != bad_local]
# Remove bad hash from known hashes
if bad_path.exists():
    import hashlib
    raw = bad_path.read_bytes()
    h = hashlib.md5(raw).hexdigest()
    guard._known_hashes.discard(h)
    bad_path.unlink()
    print(f"Removed bad image {bad_local}")

# Now try real news images directly
direct_urls = [
    # TIME article gas prices photo - Patrick T. Fallon AFP/Getty
    "https://static.time.com/v3/assets/bltea6093859af6183b/blte584c636698a5197/6adb3027290ea833fd6995f8/gas_prices.jpg",
    # Reuters DPA story would have an oil/refinery image
    "https://cloudfront-us-east-1.images.arcpublishing.com/rollcall/HWKDISIBDNHBXMYVL6ST2VLQCY.jpg",
    # AP/energy related
    "https://dims.apnews.com/dims4/default/refinery-oil.jpg",
]

img1 = None
for url in direct_urls:
    img1 = guard.fetch_unique(url, story_title=story1_title, used_on='section-politics.html')
    print(f"  {url[:70]}: {img1}")
    if img1:
        break

# If still None, try article og:image from rollcall or other pages
if img1 is None:
    for src in [
        "https://rollcall.com/2026/10/22/defense-production-act-funds-steered-to-gop-backed-energy-projects/",
        "https://time.com/article/2026/10/23/defense-production-act-memorandum-oil-gas-diesel-energy-us-iran/",
        "https://www.energy.gov/articles/energy-department-use-defense-production-act-funding-restart-american-refinery-and-expand",
    ]:
        img1 = guard.fetch_from_article(src, story_title=story1_title, used_on='section-politics.html')
        print(f"  Article {src[:60]}: {img1}")
        if img1:
            break

print(f"FINAL Story 1 replacement: {img1}")
guard.save_registry()
