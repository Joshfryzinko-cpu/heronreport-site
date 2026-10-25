import sys
sys.path.insert(0, 'scripts')
from image_guard import ImageGuard
guard = ImageGuard()
print(f'Registry loaded. Total entries: {len(guard._entries)}')

# Story 1: Trump wind turbine national security (Oct 22, 2026)
story1_urls = [
    'https://www.reuters.com/world/trump-directs-trade-negotiations-wind-turbine-imports-executive-order-2026-10-22',
    'https://duke.fm/2026/10/22/trump-directs-trade-negotiations-on-wind-turbine-imports-in-executive-order-2/',
    'https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/102326-white-house-proclamation-orders-trade-negotiations-over-wind-turbine-imports',
]
img1 = None
for url in story1_urls:
    img1 = guard.fetch_from_article(url, story_title='Trump Declares Wind Turbine Imports a National Security Threat', used_on='section-politics.html')
    if img1:
        print(f'STORY1_IMG:{img1}:FROM:{url}')
        break
    else:
        print(f'Story1 fail: {url}')
if not img1:
    print('STORY1_IMG:NONE')

# Story 2: Trump waives Russia sanctions (Oct 17, 2026)
story2_urls = [
    'https://time.com/article/2026/10/17/what-trump-s-waiver-of-new-russia-sanctions-means-for-ukraine/',
    'https://www.cnbc.com/2026/10/17/trump-waives-russia-related-sanctions-citing-national-interest.html',
    'https://www.cnn.com/2026/10/16/europe/us-ukraine-russia-sanctions-intl-hnk',
]
img2 = None
for url in story2_urls:
    img2 = guard.fetch_from_article(url, story_title='Trump Waives Russia Sanctions, Ukraine Condemns Decision', used_on='section-politics.html')
    if img2:
        print(f'STORY2_IMG:{img2}:FROM:{url}')
        break
    else:
        print(f'Story2 fail: {url}')
if not img2:
    print('STORY2_IMG:NONE')

# Story 3: Florida immigration arrests 25000+ (DeSantis/Operation Tidal Wave)
story3_urls = [
    'https://www.flgov.com/eog/news/press/2026/governor-ron-desantis-announces-results-major-immigration-enforcement-operations',
    'https://www.wpbf.com/article/undocumented-immigrants-arrested-desantis-florida-immigration-enforcement/71444161',
    'https://www.winknews.com/news/state/desantis-and-ice-hold-press-conference-on-operation-tidal-wave/article_f4297f25-9c30-4b37-a1ea-759be36cab58.html',
]
img3 = None
for url in story3_urls:
    img3 = guard.fetch_from_article(url, story_title='Florida Surpasses 25,000 Immigration Arrests as DeSantis Expands Federal Enforcement Partnership', used_on='section-politics.html')
    if img3:
        print(f'STORY3_IMG:{img3}:FROM:{url}')
        break
    else:
        print(f'Story3 fail: {url}')
if not img3:
    print('STORY3_IMG:NONE')

guard.save_registry()
print('Registry saved.')
