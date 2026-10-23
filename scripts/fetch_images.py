#!/usr/bin/env python3
"""Fetch images for 3 politics stories using ImageGuard."""
import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

results = {}

# Story 1: Trump invokes Defense Production Act for oil refinery
story1_title = "Trump Invokes Defense Production Act to Boost Oil Refinery Capacity"
img1 = guard.fetch_from_article(
    "https://www.energy.gov/articles/energy-department-use-defense-production-act-funding-restart-american-refinery-and-expand",
    story_title=story1_title, used_on='section-politics.html'
)
print(f"Story 1 (DOE): {img1}")
if img1 is None:
    img1 = guard.fetch_from_article(
        "https://time.com/article/2026/10/23/defense-production-act-memorandum-oil-gas-diesel-energy-us-iran/",
        story_title=story1_title, used_on='section-politics.html'
    )
    print(f"Story 1 (TIME): {img1}")
if img1 is None:
    img1 = guard.fetch_from_article(
        "https://rollcall.com/2026/10/22/defense-production-act-funds-steered-to-gop-backed-energy-projects/",
        story_title=story1_title, used_on='section-politics.html'
    )
    print(f"Story 1 (RollCall): {img1}")
results['story1'] = img1
print(f"FINAL Story 1: {img1}")

# Story 2: Trump declares wind turbine imports a national security threat
story2_title = "Trump Declares Wind Turbine Imports a Threat to National Security"
img2 = guard.fetch_from_article(
    "https://www.reuters.com/world/trump-directs-trade-negotiations-wind-turbine-imports-executive-order-2026-10-22/",
    story_title=story2_title, used_on='section-politics.html'
)
print(f"Story 2 (Reuters): {img2}")
if img2 is None:
    img2 = guard.fetch_from_article(
        "https://www.whitehouse.gov/presidential-actions/2026/10/presidential-determination-pursuant-to-section-303-of-the-defense-production-act-of-1950-as-amended-on-domestic-petroleum-production-refining-and-logistics-capacity-c139/",
        story_title=story2_title, used_on='section-politics.html'
    )
    print(f"Story 2 (WH): {img2}")
if img2 is None:
    img2 = guard.fetch_from_article(
        "https://insurancejournal.com/news/national/2026/10/23/890088.htm",
        story_title=story2_title, used_on='section-politics.html'
    )
    print(f"Story 2 (IJ): {img2}")
results['story2'] = img2
print(f"FINAL Story 2: {img2}")

# Story 3: Firebomb attempt on ICE facility in Atlanta
story3_title = "Man Attempts to Firebomb ICE Facility in Atlanta; FBI Offers $20K Reward"
img3 = guard.fetch_from_article(
    "https://www.dhs.gov/news/2026/10/22/dhs-issues-statement-after-man-attempts-firebomb-ice-facility-atlanta",
    story_title=story3_title, used_on='section-politics.html'
)
print(f"Story 3 (DHS): {img3}")
if img3 is None:
    img3 = guard.fetch_from_article(
        "https://apnews.com/article/atlanta-ice-building-incendiary-device-c44ce5424cecc35616ac48029ca73b60",
        story_title=story3_title, used_on='section-politics.html'
    )
    print(f"Story 3 (AP): {img3}")
if img3 is None:
    img3 = guard.fetch_from_article(
        "https://www.wsbtv.com/news/local/search-growing-man-accused-trying-firebomb-ice-office-20k-reward-offered/7JLQ2EZ6RZATDPMZKBGDHOIJ5Y/",
        story_title=story3_title, used_on='section-politics.html'
    )
    print(f"Story 3 (WSBTV): {img3}")
results['story3'] = img3
print(f"FINAL Story 3: {img3}")

guard.save_registry()
print("Registry saved.")
print("RESULTS:", results)
