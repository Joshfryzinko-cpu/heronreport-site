"""
probe_og.py — probe OG images from multiple Florida business story URLs
"""
import sys, requests, re
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

guard = ImageGuard()

test_urls = [
    ("Mosaic Layoffs Polk County", "https://www.wfla.com/news/polk-county/mosaic-to-lay-off-nearly-200-workers-at-polk-county-facility-as-iran-war-throttles-supply-chain/"),
    ("SpaceX Pipeline Brevard", "https://www.clickorlando.com/news/local/2026/10/08/spacex-plans-32-mile-natural-gas-pipeline-through-brevard-county/"),
    ("KSC Layoffs", "https://www.clickorlando.com/news/space-news/2026/10/21/subcontractor-at-kennedy-space-center-is-laying-off-workers/"),
    ("Miami Supertall", "https://www.local10.com/news/local/2026/10/12/miamis-first-supertall-skyscraper-nears-completion-as-downtowns-skyline-reaches-new-heights/"),
    ("AAR Aircraft Miami", "https://www.local10.com/video/news/local/2026/08/18/aar-expands-aircraft-maintenance-operation-at-miami-international-airport-adding-200-jobs/"),
    ("Alro Metals Oviedo", "https://www.bizjournals.com/orlando/news/2026/10/22/alro-metals-expansion-oviedo-warehouse-new-jobs.html"),
    ("Vology Pinellas floridatrend", "https://www.floridatrend.com/article/22093/vology-to-expand-in-pinellas-county--200-high-paying-jobs-projected-in-the-next-2-4-years/"),
    ("Maritime Jobs floridatrend", "https://www.floridatrend.com/articles/2026/10/15/maritime-jobs/"),
]

for label, url in test_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        og = re.search(r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text)
        if not og:
            og = re.search(r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', r.text)
        og_url = og.group(1) if og else None
        print(f"[{label}] status={r.status_code} og={'YES: '+og_url[:80] if og_url else 'NONE'}")
    except Exception as e:
        print(f"[{label}] ERROR: {e}")

print("DONE")
