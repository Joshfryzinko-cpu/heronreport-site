"""
probe_og3.py — probe more story URLs for OG images
"""
import sys, requests, re
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

guard = ImageGuard()

test_urls = [
    ("FL AG Insurance Probe", "https://www.fox13news.com/news/florida-ag-targets-insurance-policy-rules-banning-public-adjusters"),
    ("Tampa Selmon Expressway", "https://www.fox13news.com/news/selmon-expressway-expansion-two-year-road-closure-begins-tampa"),
    ("FrankCrum Cemetery", "https://www.fox13news.com/news/hundreds-graves-buried-beneath-clearwater-business-despite-7-5m-settlement"),
    ("Kissimmee Mayor Arrest", "https://news4jax.com/news/local/2026/10/21/uthmeier-announces-arrest-of-kissimmee-mayor-accused-in-50k-grant-fraud-case"),
]

for label, url in test_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        og = re.search(r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', r.text)
        if not og:
            og = re.search(r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', r.text)
        og_url = og.group(1) if og else None
        if og_url:
            result = guard.fetch_unique(og_url, story_title=label, used_on="section-business.html")
            print(f"[{label}] status={r.status_code} og_prefix={og_url[:60]} result={result}")
        else:
            print(f"[{label}] status={r.status_code} og=NONE")
    except Exception as e:
        print(f"[{label}] ERROR: {e}")

guard.save_registry()
print("DONE")
