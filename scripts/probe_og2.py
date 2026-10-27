"""
probe_og2.py — probe additional recent Florida business story URLs
"""
import sys, requests, re
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

guard = ImageGuard()

test_urls = [
    ("KSC Layoffs Oct21", "https://www.clickorlando.com/news/space-news/2026/10/21/subcontractor-at-kennedy-space-center-is-laying-off-workers/"),
    ("JTA Downgrade Oct23", "https://news4jax.com/news/local/2026/10/23/fitch-downgrades-jtas-credit-rating-cites-weakened-financial-resilience-amid-40m-budget-shortfall"),
    ("Broward Data Centers Oct20", "https://local10.com/news/local/2026/10/20/broward-county-moves-toward-one-year-moratorium-on-large-scale-data-centers"),
    ("GFL Alliance", "https://www.gflalliance.org/news/2026/10/20/in-the-news/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says/"),
    ("FL Trend Maritime Oct15", "https://www.floridatrend.com/articles/2026/10/15/maritime-jobs/"),
    ("WJHG Maritime Oct21", "https://www.wjhg.com/2026/10/21/northwest-florida-maritime-aviation-growth-driving-thousands-jobs/"),
]

for label, url in test_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        og = re.search(r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text)
        if not og:
            og = re.search(r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', r.text)
        og_url = og.group(1) if og else None
        if og_url:
            # Try actually fetching the image
            result = guard.fetch_unique(og_url, story_title=label, used_on="section-business.html")
            print(f"[{label}] status={r.status_code} og=YES result={result}")
        else:
            print(f"[{label}] status={r.status_code} og=NONE")
    except Exception as e:
        print(f"[{label}] ERROR: {e}")

guard.save_registry()
print("DONE")
