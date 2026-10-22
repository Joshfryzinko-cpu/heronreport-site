import sys
sys.path.insert(0, 'scripts')
from image_guard import ImageGuard
guard = ImageGuard()

stories = [
    {
        'title': 'Kissimmee Mayor Arrested for Grand Theft COVID Grant Fraud',
        'primary_url': 'https://www.clickorlando.com/news/local/2026/10/21/kissimmee-mayor-arrested-on-theft-fraud-charges-ag-says/',
        'alts': [
            'https://abcnews.com/US/mayor-kissimmee-florida-arrested-grand-theft-fraud-charges/story?id=137448984',
            'https://www.myfloridalegal.com/newsrelease/attorney-general-james-uthmeier-announces-arrest-kissimmee-mayor-grand-theft-organized',
        ]
    },
    {
        'title': 'DOJ First-Ever National Tax Fraud Surge 76 Defendants 490M',
        'primary_url': 'https://www.justice.gov/opa/pr/dojs-fraud-division-irs-and-irs-ci-expose-more-490m-tax-fraud-national-tax-enforcement-surge',
        'alts': [
            'https://govexec.com/management/2026/10/enforcement-surge-doj-irs-uncovers-490m-suspected-tax-fraud/416662',
            'https://cpapracticeadvisor.com/2026/10/15/nationwide-enforcement-surge-uncovers-490-million-in-tax-fraud/191746',
            'https://wltreport.com/2026/10/14/trump-doj-national-tax-fraud-surge-76-defendants-490-million',
        ]
    },
    {
        'title': 'Florida Cop Arrested Stealing Dead Mans Identity and Home',
        'primary_url': 'https://www.miamiherald.com/news/local/community/broward/article317708117.html',
        'alts': [
            'https://www.local10.com/news/local/2026/10/21/lauderhill-cop-arrested-after-allegedly-stealing-dead-mans-identity-home/',
            'https://www.wsvn.com/news/local/broward/lauderhill-officer-arrested-for-allegedly-stealing-a-dead-mans-identity/',
        ]
    },
]

results = []
for s in stories:
    img = guard.fetch_from_article(s['primary_url'], story_title=s['title'], used_on='section-investigations.html')
    if img is None:
        print(f'DUPE_OR_FAIL: {s["title"][:40]}')
        for alt in s['alts']:
            img = guard.fetch_from_article(alt, story_title=s['title'], used_on='section-investigations.html')
            if img:
                print(f'  ALT_WORKED: {alt[:70]}')
                break
    if img is None:
        img = '/img/placeholder.svg'
        print(f'PLACEHOLDER: {s["title"][:40]}')
    else:
        print(f'OK: {img} | {s["title"][:50]}')
    results.append({'title': s['title'], 'img': img})

guard.save_registry()
print('DONE')
for r in results:
    print('RESULT:', r['img'], '|||', r['title'])
