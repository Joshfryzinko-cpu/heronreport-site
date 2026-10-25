import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

stories = [
    {
        'title': 'Maryland Lab Owner Convicted of 18.7M Medicare Fraud Targeting COVID-Desperate Nursing Homes',
        'url': 'https://www.justice.gov/opa/pr/maryland-man-convicted-187m-medicare-fraud-respiratory-testing-scheme-targeting-nursing',
        'alts': [
            'https://apnews.com/article/medicare-fraud-nursing-home-lab-convicted-2026',
            'https://www.cbsnews.com/news/maryland-lab-medicare-fraud-nursing-home-covid-convicted/',
            'https://www.msn.com/en-us/money/news/maryland-man-convicted-187m-medicare-fraud',
        ]
    },
    {
        'title': 'Accountability Group Challenges Court Ruling That Erased Hope Florida Grand Jury Report',
        'url': 'https://floridatrident.org/hope-florida-grand-jury-rehearing-motion/',
        'alts': [
            'https://www.orlandosentinel.com/2026/10/23/government-watchdog-wants-expungement-of-hope-florida-report-overturned/',
            'https://www.wusf.org/politics-issues/2026-10-08/appeals-court-expunges-hope-florida-grand-jury-report',
        ]
    },
    {
        'title': 'DOJ SNAP Fraud Surge 40 Defendants 42M in Stolen Food Benefits Exposed Nationwide',
        'url': 'https://www.justice.gov/opa/pr/dojs-fraud-division-department-agriculture-and-usda-oig-uncover-nearly-42m-snap-benefit',
        'alts': [
            'https://thehill.com/policy/healthcare/snap-fraud-enforcement-doj-2026',
            'https://apnews.com/article/snap-fraud-enforcement-nationwide-2026',
            'https://www.usatoday.com/story/news/crime/2026/10/21/snap-food-benefits-fraud-doj',
        ]
    }
]

results = {}
for s in stories:
    print('--- Story:', s['title'][:60], '---')
    img = guard.fetch_from_article(s['url'], story_title=s['title'], used_on='section-investigations.html')
    if img is None:
        print('  Primary returned None. Trying alts...')
        for alt in s['alts']:
            img = guard.fetch_from_article(alt, story_title=s['title'], used_on='section-investigations.html')
            if img:
                print('  Alt succeeded:', alt)
                break
    if img is None:
        print('  All None - using placeholder')
        img = '/img/placeholder.svg'
    else:
        print('  Image:', img)
    results[s['title']] = img

guard.save_registry()
print('=== RESULTS ===')
for title, img in results.items():
    print(title[:60], '=>', img)
