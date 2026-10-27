"""Check OG images for Broward story sources"""
import requests, re, sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

urls = [
    'https://thesouthfloridabusinessowner.news/browards-318m-investment-wave-has-a-hiring-signal-inside-it',
    'https://www.gflalliance.org/news/2026/10/20/in-the-news/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says/',
    'https://www.bizjournals.com/southflorida/news/2026/10/15/greater-fort-lauderdale-alliance-lures.html',
    'https://sun-sentinel.com/2026/10/15/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says',
]

guard = ImageGuard()

for u in urls:
    try:
        r = requests.get(u, headers=HEADERS, timeout=10)
        og = re.search(r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text)
        if not og:
            og = re.search(r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', r.text)
        og_url = og.group(1) if og else None
        print(f"URL: {u[:70]}")
        print(f"  Status: {r.status_code}")
        print(f"  OG: {og_url}")
        if og_url:
            # Try fetching it
            result = guard.fetch_unique(og_url, story_title="Broward 318M", used_on="section-business.html")
            print(f"  Fetch result: {result}")
        print()
    except Exception as e:
        print(f"URL: {u[:70]} -> ERROR: {e}")
        print()

guard.save_registry()
print("DONE")
