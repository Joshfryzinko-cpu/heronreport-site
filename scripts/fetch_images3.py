#!/usr/bin/env python3
"""Fetch image for story 3 - ICE firebomb Atlanta."""
import sys, requests
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

story3_title = "Man Attempts to Firebomb ICE Facility in Atlanta; FBI Offers $20K Reward"

# Try more sources
sources = [
    "https://www.washingtonexaminer.com/news/crime/4775508/feds-seek-suspect-in-attempted-firebomb-attack-on-atlanta-ice-facility/",
    "https://www.cbsnews.com/atlanta/news/fbi-continues-investigation-into-atlanta-ice-headquarters-arson-attempt-serious-risk-to-the-community/",
    "https://www.foxnews.com/us/man-attempted-firebomb-ice-facility-atlanta-device-caught-fence-dhs",
    "https://www.breitbart.com/immigration/2026/10/22/dhs-man-attempted-to-firebomb-ice-facility-in-atlanta/",
    "https://nypost.com/2026/10/22/us-news/molotov-cocktail-thrown-at-ice-building-in-atlanta-fbi-offering-20k-reward/",
]

img3 = None
for src in sources:
    img3 = guard.fetch_from_article(src, story_title=story3_title, used_on='section-politics.html')
    print(f"  {src[:60]}: {img3}")
    if img3:
        break

# If still None, try direct image from DHS/FBI press releases
if img3 is None:
    print("Trying direct image URLs...")
    # DHS released images of device and fence - try to find direct OGP image
    direct_urls = [
        "https://storage.googleapis.com/afs-prod/media/c44ce5424cecc35616ac48029ca73b60/3000.jpeg",
        "https://cloudfront-us-east-1.images.arcpublishing.com/gray/7JLQ2EZ6RZATDPMZKBGDHOIJ5Y.jpg",
    ]
    for url in direct_urls:
        img3 = guard.fetch_unique(url, story_title=story3_title, used_on='section-politics.html')
        print(f"  Direct {url[:60]}: {img3}")
        if img3:
            break

print(f"FINAL Story 3: {img3}")
guard.save_registry()
