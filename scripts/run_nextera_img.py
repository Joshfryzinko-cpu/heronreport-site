import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

# Try additional sources for NextEra Energy image
nextera_urls = [
    'https://www.cnbc.com/2026/10/21/nextera-energy-earnings-q3-2026.html',
    'https://finance.yahoo.com/news/nextera-energy-reports-third-quarter-2026-financial-results/',
    'https://www.marketwatch.com/story/nextera-energy-earnings-2026-q3',
    'https://www.bizjournals.com/southflorida/news/2026/10/21/nextera-energy-earnings-profit-q3.html',
    'https://www.sun-sentinel.com/2026/10/21/nextera-energy-beats-profit-estimates-q3-2026/',
]

img = None
for url in nextera_urls:
    img = guard.fetch_from_article(url, story_title='NextEra Energy Beats Third-Quarter Profit Estimates on AI Power Demand', used_on='section-business.html')
    if img:
        print('OK:', url[:70], '->', img)
        break
    else:
        print('SKIP:', url[:70])

if not img:
    img = '/img/placeholder.svg'
    print('PLACEHOLDER: no image found for NextEra')

guard.save_registry()
import json
print('JSON_RESULT:' + json.dumps({'img': img}))
