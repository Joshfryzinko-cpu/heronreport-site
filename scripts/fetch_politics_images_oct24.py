import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
guard = ImageGuard()

results = {}

# Story 1: Iran prolonging talks / US midterms
url1 = "https://usnews.com/news/world/articles/2026-10-20/iran-prolongs-talks-in-stalemate-to-influence-us-midterms-officials-say"
img1 = guard.fetch_from_article(url1, story_title="Iran Prolongs Nuclear Talks to Influence US Midterms", used_on='section-politics.html')
results['story1'] = img1
print(f"Story 1 image: {img1}")

if img1 is None:
    for alt in [
        "https://amp.dw.com/en/is-iran-ready-for-another-major-us-attack-after-midterm-elections/a-79734082",
        "https://time.com/article/2026/10/21/trump-iran-war-midterm-elections-deadlock",
    ]:
        img1 = guard.fetch_from_article(alt, story_title="Iran Prolongs Nuclear Talks to Influence US Midterms", used_on='section-politics.html')
        if img1:
            results['story1'] = img1
            print(f"Story 1 alt image: {img1}")
            break

# Story 2: Operation Ice Breaker Florida
url2 = "https://wflx.com/2026/10/13/operation-ice-breaker-25-charged-major-south-florida-drug-trafficking-investigation"
img2 = guard.fetch_from_article(url2, story_title="Operation Ice Breaker: Florida AG Charges 25 in Drug Trafficking Ring", used_on='section-politics.html')
results['story2'] = img2
print(f"Story 2 image: {img2}")

if img2 is None:
    for alt in [
        "https://cbs12.com/news/local/florida-drug-trafficking-bust-leads-19-arrests-6-more-suspects-sought-selling-fentanyl-cocaine-florida-department-of-law-enforcement-west-palm-beach-field-office-palm-beach-county-sheriffs-office-florida-news",
        "https://hoodline.com/2026/10/miami-beach-whatsapp-drug-ring-busted-70-pounds-of-narcotics-and-49k-seized",
    ]:
        img2 = guard.fetch_from_article(alt, story_title="Operation Ice Breaker: Florida AG Charges 25 in Drug Trafficking Ring", used_on='section-politics.html')
        if img2:
            results['story2'] = img2
            print(f"Story 2 alt image: {img2}")
            break

# Story 3: Montana super range DOD
url3 = "https://katv.com/news/nation-world/trump-announces-new-montana-super-range-for-dod-to-test-advanced-military-technology-steve-daines-tim-sheehy-greg-gianforte"
img3 = guard.fetch_from_article(url3, story_title="Trump Announces Montana Super Range for DOD Advanced Military Technology", used_on='section-politics.html')
results['story3'] = img3
print(f"Story 3 image: {img3}")

if img3 is None:
    for alt in [
        "https://www.whitehouse.gov/releases/2026/10/president-trump-is-putting-american-industry-jobs-and-paychecks-back-on-the-map/",
        "https://defense.gov/News/News-Stories/",
    ]:
        img3 = guard.fetch_from_article(alt, story_title="Trump Announces Montana Super Range for DOD Advanced Military Technology", used_on='section-politics.html')
        if img3:
            results['story3'] = img3
            print(f"Story 3 alt image: {img3}")
            break

guard.save_registry()
print("Registry saved.")
print("FINAL:", results)
