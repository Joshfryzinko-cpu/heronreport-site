#!/usr/bin/env python3
"""Fetch ICE story image for politics section."""
import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

sources_s2 = [
    'https://www.dvidshub.net/image/8928900/tren-de-aragua-arrests',
    'https://www.dvidshub.net/image/8928892/tren-de-aragua-arrests',
    'https://d1ldvf68ux039x.cloudfront.net/thumbs/photos/2503/8928900/1000w_q95.jpg',
    'https://d1ldvf68ux039x.cloudfront.net/thumbs/photos/2503/8928892/1000w_q95.jpg',
    'https://www.ice.gov/node/66608',
    'https://www.ice.gov/node/66606',
    'https://www.dvidshub.net/unit/ICE/?sort=date&view=list',
]

result = None
for url in sources_s2:
    img = guard.fetch_from_article(url, story_title='ICE_Gang_Arrests_Oct2026_v2', used_on='section-politics.html')
    print(f"{'OK' if img else 'None'}: {url} => {img}")
    if img:
        result = img
        break

guard.save_registry()
print(f"FINAL_S2: {result}")
