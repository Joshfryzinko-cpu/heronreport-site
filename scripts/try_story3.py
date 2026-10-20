#!/usr/bin/env python3
"""Try more image sources for story 3 - energy dominance"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()

title3 = "Trump Proclaims October National Energy Dominance Month, Cites Venezuela Oil Deal"
# Try multiple news outlets that covered this story
alt_urls = [
    "https://www.foxnews.com/politics/trump-proclaims-october-national-energy-dominance-month",
    "https://justthenews.com/government/white-house/trump-proclaims-national-energy-dominance-month-marking-administration",
    "https://www.heritage.org/energy/commentary/why-american-energy-dominance-strategic-imperative",
    "https://www.energy.gov/",
    "https://www.eia.gov/",
    "https://www.dvids.mil/News/All/",
]
for url in alt_urls:
    img = guard.fetch_from_article(url, story_title=title3, used_on='section-politics.html')
    print(f"  {url}: {img}")
    if img:
        break

guard.save_registry()
print("done")
