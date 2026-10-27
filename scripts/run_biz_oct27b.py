"""
run_biz_oct27b.py — fetch image for story 1 replacement (Fort Lauderdale water plant)
"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()

# Story 1 replacement: Fort Lauderdale $666M water treatment plant
story1_urls = [
    "https://local10.com/news/local/2026/10/15/fort-lauderdale-cuts-ribbon-on-new-water-treatment-facility",
    "https://www.local10.com/news/local/2026/10/12/miamis-first-supertall-skyscraper-nears-completion-as-downtowns-skyline-reaches-new-heights/",
]

img = None
used_url = None
for url in story1_urls:
    img = guard.fetch_from_article(url, story_title="Fort Lauderdale Opens $666M Prospect Lake Clean Water Center", used_on="section-business.html")
    if img:
        used_url = url
        break
    print(f"No image from {url[:70]}")

print(f"Story 1 img: {img}")
print(f"Used URL: {used_url}")

guard.save_registry()

result = {"story1_img": img, "story1_url": used_url}
with open("C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts/biz_oct27b_result.json", "w") as f:
    json.dump(result, f, indent=2)
print("DONE")
