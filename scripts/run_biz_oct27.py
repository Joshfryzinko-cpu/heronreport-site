"""
run_biz_oct27.py — fetch images for Oct 27 business stories
"""
import sys, json
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()

stories = [
    {
        "id": "broward-318m",
        "title": "Broward Lands $318M in Business Investment, 1,100 New Jobs",
        "article_url": "https://sun-sentinel.com/2026/10/15/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says",
        "alt_urls": [
            "https://thesouthfloridabusinessowner.news/browards-318m-investment-wave-has-a-hiring-signal-inside-it",
            "https://www.gflalliance.org/news/2026/10/20/in-the-news/business-is-booming-broward-welcomed-many-employers-expansions-greater-fort-lauderdale-alliance-says/",
            "https://www.bizjournals.com/southflorida/news/2026/10/15/greater-fort-lauderdale-alliance-lures.html",
        ],
    },
    {
        "id": "vology-pinellas",
        "title": "Vology to Expand in Pinellas County, 200 High-Paying Jobs Projected",
        "article_url": "https://www.floridatrend.com/article/22093/vology-to-expand-in-pinellas-county--200-high-paying-jobs-projected-in-the-next-2-4-years/",
        "alt_urls": [
            "https://floridacorporatenews.com/fl-corp-news-release/florida-hiring-trends-for-fall-2026/",
        ],
    },
    {
        "id": "birdon-pensacola",
        "title": "Denver Firm Birdon Plans $275M Shipyard at Port of Pensacola, 2,000 Jobs",
        "article_url": "https://www.floridatrend.com/articles/2026/10/15/maritime-jobs/",
        "alt_urls": [
            "https://www.wjhg.com/2026/10/21/northwest-florida-maritime-aviation-growth-driving-thousands-jobs/",
        ],
    },
]

results = []
duplicates_rejected = 0

for story in stories:
    img = guard.fetch_from_article(story["article_url"], story_title=story["title"], used_on="section-business.html")
    tried = [story["article_url"]]
    if img is None:
        duplicates_rejected += 1
        for alt_url in story["alt_urls"]:
            tried.append(alt_url)
            img = guard.fetch_from_article(alt_url, story_title=story["title"], used_on="section-business.html")
            if img:
                duplicates_rejected -= 1
                break
    if img is None:
        img = "/img/placeholder.svg"
    story["img"] = img
    story["tried"] = tried
    results.append(story)
    print(f"[{story['id']}] img={img}")

print(f"duplicates_rejected={duplicates_rejected}")
guard.save_registry()

out = {"stories": results, "duplicates_rejected": duplicates_rejected}
with open("C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts/biz_oct27_result.json", "w") as f:
    json.dump(out, f, indent=2)
print("DONE")
