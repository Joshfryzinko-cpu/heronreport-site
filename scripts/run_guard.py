#!/usr/bin/env python3
"""Run ImageGuard to fetch images for 3 investigation stories."""
import sys, os, hashlib, requests, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from image_guard import ImageGuard

guard = ImageGuard()
used = guard._entries
print(f"Total registered images: {len(used)}", flush=True)

SITE = Path(__file__).parent.parent
img_dir = SITE / "img/stories"
img_dir.mkdir(parents=True, exist_ok=True)

stories = [
    {
        "title": "Virginia State Senator Louise Lucas Indicted for Racketeering, Drug Trafficking and Corruption",
        "urls": [
            "https://www.justice.gov/opa/pr/virginia-state-senator-indicted-leading-criminal-marijuana-distribution-enterprise",
            "https://apnews.com/article/l-louise-lucas-virginia-corruption-investigation-767ed83f970ba6dec48048dcff2a28d0",
            "https://www.nbcnews.com/politics/justice-department/virginia-state-senator-l-louise-lucas-charged-public-corruption-case-d-rcna604870",
            "https://abcnews.com/US/virginia-state-lawmaker-indicted-doj-marijuana-trafficking-conspiracy/story?id=137476798",
            "https://www.wavytv10.com/article/news/local/virginia-senator-louise-lucas-indicted/291-a1234567",
        ]
    },
    {
        "title": "Fort Bend County Tax Assessor Indicted for Theft of Government Funds and Wire Fraud",
        "urls": [
            "https://coveringkaty.com/news/fort-bend/federal-prosecutors-accuse-fort-bend-county-tax-assessor-col/",
            "https://www.texastribune.org/2026/10/22/texas-fort-bend-tax-assessor-collector-carmen-turner-federal-indictment/",
        ]
    },
    {
        "title": "Congress Demands Federal Probe of Hope Florida $10M Medicaid Diversion After Grand Jury Findings",
        "urls": [
            "https://soto.house.gov/media/press-releases/soto-castor-demand-federal-investigation-accountability-after-grand-jury-finds",
            "https://castor.house.gov/news/documentsingle.aspx?DocumentID=405273",
        ]
    }
]

results = []
for story in stories:
    print(f"\n--- Story: {story['title'][:60]}", flush=True)
    img = None
    for url in story['urls']:
        print(f"  Trying: {url[:80]}", flush=True)
        img = guard.fetch_from_article(url, story_title=story['title'], used_on='section-investigations.html')
        if img:
            print(f"  Got image: {img}", flush=True)
            break
        else:
            print(f"  None (duplicate or no image found)", flush=True)
    if img is None:
        img = '/img/placeholder.svg'
        print(f"  Using placeholder", flush=True)
    results.append({"title": story['title'], "img": img})

print("\n\nFINAL RESULTS:", flush=True)
for r in results:
    print(f"  {r['title'][:60]} => {r['img']}", flush=True)

guard.save_registry()
print("\nRegistry saved.", flush=True)

# Write results to a JSON file for the parent to read
with open(SITE / "scripts/guard_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("Results written to guard_results.json", flush=True)
