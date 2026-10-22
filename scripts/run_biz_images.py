import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

stories = [
    {
        'title': "Leslie's Pool Supplies Closing 19 Florida Stores in Chapter 11 Bankruptcy",
        'urls': [
            'https://www.sun-sentinel.com/2026/10/06/leslies-closing-multiple-florida-pool-supply-stores-after-filing-for-chapter-11-bankruptcy/',
            'https://www.sun-sentinel.com/2026/10/05/leslies-pool-supplies-closes-13-southern-california-stores-in-bankruptcy/',
        ]
    },
    {
        'title': 'NextEra Energy Beats Third-Quarter Profit Estimates on AI Power Demand',
        'urls': [
            'https://www.reuters.com/business/energy/nextera-energy-beats-third-quarter-profit-estimates-2026-10-21/',
            'https://apnews.com/article/nextera-energy-earnings-profit-2026',
        ]
    },
    {
        'title': 'Art Basel Miami Beach Deal Redesigned Through 2031',
        'urls': [
            'https://www.miamitodaynews.com/2026/10/21/art-basel-deal-with-miami-beach-gets-a-redesign/',
            'https://www.sun-sentinel.com/2026/10/21/art-basel-miami-beach-convention-center/',
        ]
    }
]

results = []
for story in stories:
    img = None
    for url in story['urls']:
        img = guard.fetch_from_article(url, story_title=story['title'], used_on='section-business.html')
        if img:
            print('OK:', story['title'][:50], '->', img)
            break
        else:
            print('SKIP (dupe or no img):', url[:70])
    if not img:
        img = '/img/placeholder.svg'
        print('PLACEHOLDER for:', story['title'][:50])
    results.append({'title': story['title'], 'img': img})

guard.save_registry()
import json
print('JSON_RESULTS:' + json.dumps(results))
