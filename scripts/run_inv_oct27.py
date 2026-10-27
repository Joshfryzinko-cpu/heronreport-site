import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()

# Story 1: Kissimmee Mayor Espinosa - arrest Oct 21 2026
title1 = "Kissimmee Mayor Arrested for Funneling COVID Relief to Family Businesses"
url1 = "https://www.wfla.com/news/florida/kissimmee-mayor-arrested-for-abusing-her-office-for-personal-gain-fl-cfo-says/"
img1 = guard.fetch_from_article(url1, story_title=title1, used_on='section-investigations.html')
print(f"Story 1 img: {img1}")

# Alt: try FL Voice News
if img1 is None:
    alt1 = "https://flvoicenews.com/kissimmee-mayor-jackie-espinosa-faces-up-to-30-years-in-prison-following-corruption-arrest"
    img1 = guard.fetch_from_article(alt1, story_title=title1, used_on='section-investigations.html')
    print(f"Story 1 alt img: {img1}")

# Story 2: PBSO $54M Renovation Audit - Oct 20 2026
title2 = "Audit Slams $54M Palm Beach Sheriff HQ Renovation: Missing Receipts, Overcharges"
url2 = "https://www.wlrn.org/government-politics/2026-10-20/missing-receipts-overcharges-unapproved-spending-audit-slams-54m-pbso-hq-renovation"
img2 = guard.fetch_from_article(url2, story_title=title2, used_on='section-investigations.html')
print(f"Story 2 img: {img2}")

# Story 3: DOJ National Tax Enforcement Surge - Oct 14 2026
title3 = "DOJ Exposes $490M in Tax Fraud in Nationwide Enforcement Surge"
url3 = "https://www.justice.gov/opa/pr/dojs-fraud-division-irs-and-irs-ci-expose-more-490m-tax-fraud-national-tax-enforcement-surge"
img3 = guard.fetch_from_article(url3, story_title=title3, used_on='section-investigations.html')
print(f"Story 3 img: {img3}")

# Alt sources for story 3 if DOJ returns badge/seal
if img3 is None:
    alt3 = "https://www.irs.gov/compliance/criminal-investigation/middle-district-of-florida-joins-doj-fraud-division-irs-irs-ci-and-the-fbi-in-national-tax-enforcement-surge-exposing-more-than-490m-in-tax-fraud"
    img3 = guard.fetch_from_article(alt3, story_title=title3, used_on='section-investigations.html')
    print(f"Story 3 alt img: {img3}")

guard.save_registry()
print("DONE")
print(f"FINAL: img1={img1}, img2={img2}, img3={img3}")
