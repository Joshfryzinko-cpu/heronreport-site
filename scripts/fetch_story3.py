#!/usr/bin/env python3
"""Fetch image for a third investigation story."""
import sys, json
from pathlib import Path

SCRIPTS = Path(__file__).parent
SITE = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from image_guard import ImageGuard

guard = ImageGuard()

# Try Rivera (FL former congressman sentenced Oct 3) or Trayon White (DC bribery Oct 22)
candidates = [
    {
        "story": "Former Florida Congressman David Rivera Sentenced 10 Years Federal Prison Venezuelan Foreign Agent Money Laundering",
        "urls": [
            "https://wltreport.com/2026/10/03/former-congressman-10-year-federal-prison-secret-foreign-influence-money-laundering",
            "https://www.justice.gov/usao-sdfl/pr/former-us-congressman-sentenced-10-years-federal-prison-secretly-acting-agent",
        ]
    },
    {
        "story": "DC Councilmember Trayon White Superseding Federal Bribery Indictment Cash Caught on Video",
        "urls": [
            "https://wjla.com/news/local/doj-to-retry-dc-councilmember-trayon-white-with-superseding-indictment",
            "https://www.nbcwashington.com/news/local/trayon-white-superseding-indictment-federal-bribery/",
        ]
    },
    {
        "story": "Cornelius Thompson Ocala Florida Federal Prison Guard Pleads Guilty Bribery Smuggling",
        "urls": [
            "http://justice.gov/usao-mdfl/pr/federal-correctional-officer-pleads-guilty-sexual-abuse-inmate-and-receipt-bribe",
        ]
    }
]

result = None
for cand in candidates:
    print(f"\n=== Candidate: {cand['story'][:60]}", flush=True)
    for url in cand['urls']:
        print(f"  Trying: {url[:80]}", flush=True)
        img = guard.fetch_from_article(url, story_title=cand['story'], used_on='section-investigations.html')
        if img:
            print(f"  SUCCESS: {img}", flush=True)
            result = {"story": cand['story'], "img": img}
            break
        else:
            print(f"  None", flush=True)
    if result:
        break

if result is None:
    result = {"story": candidates[0]['story'], "img": "/img/placeholder.svg"}
    print("\nAll candidates returned no image, using placeholder", flush=True)

print(f"\nFINAL: {result}", flush=True)
guard.save_registry()

with open(SITE / "scripts/story3_result.json", "w") as f:
    json.dump(result, f, indent=2)
print("Written to story3_result.json", flush=True)
