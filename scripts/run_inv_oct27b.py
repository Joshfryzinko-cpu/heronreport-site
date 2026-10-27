import sys, hashlib, json
from pathlib import Path

sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard

guard = ImageGuard()

# ── Story 1: Kissimmee Mayor Espinosa arrest photo ─────────────────────────
# Image found in WFLA article: arrest scene photo
img1 = None
title1 = "Kissimmee Mayor Arrested for Funneling COVID Relief to Family Businesses"
for url in [
    "https://www.wfla.com/wp-content/uploads/sites/71/2026/10/HVKWo87XoAEiiY1.jpg",
    "https://www.wfla.com/wp-content/uploads/sites/71/2026/10/16-x-9-1.png",
    # FL Voice article image (police officers talking)
    "https://flvoicenews.com/wp-content/uploads/sites/2/2026/10/kissimmee-police.jpg",
]:
    img1 = guard.fetch_unique(url, story_title=title1, used_on='section-investigations.html')
    print(f"  tried {url}: {img1}")
    if img1:
        break

print(f"Story 1 final: {img1}")

# ── Story 2: Already registered from first run ──────────────────────────────
# cc83efff2964ee6e.jpg was saved successfully in the first run
# We just need to verify it exists on disk
img2_path = Path('C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/img/stories/cc83efff2964ee6e.jpg')
img2 = '/img/stories/cc83efff2964ee6e.jpg' if img2_path.exists() else None
print(f"Story 2 final: {img2}")

# ── Story 3: DOJ Tax Surge - try IRS Tampa article, then Tampa Bay Times ────
title3 = "DOJ Exposes $490M in Tax Fraud in Nationwide Enforcement Surge"
img3 = None
for url in [
    # IRS Criminal Investigation usually has a seal - skip; try news outlets
    "https://www.irs.gov/compliance/criminal-investigation/middle-district-of-florida-joins-doj-fraud-division-irs-irs-ci-and-the-fbi-in-national-tax-enforcement-surge-exposing-more-than-490m-in-tax-fraud",
    "https://www.tampabay.com/news/florida-politics/2026/10/15/florida-us-attorney-joins-490m-tax-fraud-enforcement-surge/",
    "https://www.orlandosentinel.com/2026/10/15/doj-tax-fraud-surge-490-million/",
]:
    img3 = guard.fetch_from_article(url, story_title=title3, used_on='section-investigations.html')
    print(f"  tried {url}: {img3}")
    if img3:
        break

# If still None, try a direct image related to IRS/tax enforcement
if img3 is None:
    for url in [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Department_of_Justice_seal.svg/500px-Department_of_Justice_seal.svg.png",
    ]:
        img3 = guard.fetch_unique(url, story_title=title3, used_on='section-investigations.html')
        print(f"  tried direct {url}: {img3}")
        if img3:
            break

if img3 is None:
    img3 = '/img/placeholder.svg'

print(f"Story 3 final: {img3}")

guard.save_registry()
print("Registry saved.")
print(f"RESULTS: img1={img1}, img2={img2}, img3={img3}")
