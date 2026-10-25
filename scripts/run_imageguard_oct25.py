import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

stories = [
    {
        'title': 'Maryland Lab Owner Convicted of 18.7M Medicare Fraud Targeting COVID-Desperate Nursing Homes',
        'url': 'https://www.justice.gov/usao-md/pr/maryland-felon-convicted-187-million-medicare-fraud',
        'alts': [
            'https://www.cbsnews.com/baltimore/news/maryland-man-guilty-18-million-medicare-fraud/',
            'https://wfla.com/news/florida/nearly-42m-in-snap-benefit-fraud-uncovered-in-operation-doj',
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
        'url': 'https://wfla.com/news/florida/nearly-42m-in-snap-benefit-fraud-uncovered-in-operation-doj',
        'alts': [
            'https://yahoo.com/news/us/articles/nearly-42m-snap-benefit-fraud-105318372.html',
            'https://oann.com/newsroom/trump-admin-announces-enforcement-actions-against-over-40-defendants-accused-of-nearly-42m-in-snap-fraud',
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
