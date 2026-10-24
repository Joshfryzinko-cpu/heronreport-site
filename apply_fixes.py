#!/usr/bin/env python3
"""Download remaining images and apply all HTML replacements."""
import urllib.request
import hashlib
import os
import ssl
import time
import re

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"
IMG_DIR = os.path.join(SITE, "img", "stories")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download(url, label, ext=None):
    if ext is None:
        ext = '.jpg'
        ul = url.lower().split('?')[0]
        if ul.endswith('.png'): ext = '.png'
        elif ul.endswith('.webp'): ext = '.webp'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'TheHeronReport/1.0 (https://heronreport.com; news@heronreport.com)',
            'Accept': 'image/webp,image/jpeg,image/*',
        })
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            data = r.read()
            ct = r.headers.get('Content-Type', '')
            if 'png' in ct: ext = '.png'
            elif 'webp' in ct: ext = '.webp'
        if not data or len(data) < 500:
            print(f"TINY: {label}")
            return None
        h = hashlib.md5(data).hexdigest()[:16]
        fname = f"{h}{ext}"
        fpath = os.path.join(IMG_DIR, fname)
        with open(fpath, 'wb') as f:
            f.write(data)
        print(f"OK: {label} -> {fname} ({len(data):,} bytes)")
        return fname
    except Exception as e:
        print(f"FAIL: {label}: {e}")
        return None

# ========== DOWNLOAD PHASE ==========
print("=== Downloading images ===")

# Wedding rings (for marriage fraud story)
wedding = download(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Wedding_rings.jpg/500px-Wedding_rings.jpg",
    "Wedding rings"
)
time.sleep(1)

if not wedding:
    wedding = download(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/A_pair_of_wedding_rings.jpg/500px-A_pair_of_wedding_rings.jpg",
        "Wedding rings pair"
    )
    time.sleep(1)

# Garage door (for Garage Door Pros story)
# Try several file hashes
garage = None
for fn, h, ext in [
    ('Garage_door.JPG', '7/7f', '.jpg'),
    ('Blue_garage_door.jpg', '4/4c', '.jpg'),
    ('Garage_Doors_in_California_01.jpg', 'd/d7', '.jpg'),
    ('Garage_Doors_Raleigh_NC.jpg', 'a/a2', '.jpg'),
]:
    for size in ['500px', '960px']:
        url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h}/{fn}/{size}-{fn}"
        garage = download(url, f"Garage {fn[:20]} {size}")
        if garage:
            break
        time.sleep(1)
    if garage:
        break

# Hispanic small business image
biz = None
# Try SBA / USDA images, or find a Wikimedia small business image
for fn, h in [
    ('Small_business_storefront.jpg', '1/1e'),
    ('Main_Street_small_business.jpg', '5/5f'),
    ('Entrepreneurs.jpg', 'a/a3'),
]:
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h}/{fn}/500px-{fn}"
    biz = download(url, f"SmallBiz {fn[:20]}")
    if biz:
        break
    time.sleep(1)

# If still no biz image, try a Florida Chamber of Commerce type image
if not biz:
    # Try the Gage Skidmore Vivek Ramaswamy photo as biz alternative... no, different story
    # Use a generic market/commerce image from Wikimedia
    biz = download(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/500px-Image_created_with_a_mobile_phone.png",
        "biz mobile fallback"
    )

print(f"\nwedding: {wedding}")
print(f"garage: {garage}")
print(f"biz: {biz}")

# ========== HTML UPDATE PHASE ==========
print("\n=== Applying HTML fixes ===")

# These images are confirmed downloaded from previous script:
vance = 'c14a9c7237e69e53.jpg'
vivek = '6d86e1a4b4acf903.jpg'
tacos = '84aed607550bf38c.jpg'
palmbeach = 'a4c090e6ad50aeac.jpg'

# Verify these exist
for name, fname in [('vance', vance), ('vivek', vivek), ('tacos', tacos), ('palmbeach', palmbeach)]:
    fpath = os.path.join(IMG_DIR, fname)
    exists = os.path.exists(fpath)
    print(f"  {name}: {fname} {'EXISTS' if exists else 'MISSING'}")

# --- FIX POLITICS PAGE ---
pol_path = os.path.join(SITE, "section-politics.html")
with open(pol_path, 'r', encoding='utf-8') as f:
    pol = f.read()

pol_orig = pol

# Fix 1: FDLE badge (2ab8e1e20d5e2918.png) on "JD Vance's 2nd Kansas visit"
fdle_img = '2ab8e1e20d5e2918.png'
if fdle_img in pol and os.path.exists(os.path.join(IMG_DIR, vance)):
    pol = pol.replace(
        f'src="/img/stories/{fdle_img}" alt="JD Vance\'s 2nd Kansas visit indicates GOP concern in US"',
        f'src="/img/stories/{vance}" alt="JD Vance\'s 2nd Kansas visit indicates GOP concern in US"'
    )
    pol = pol.replace(
        '>Florida Dept. of Law Enforcement (public domain)</span>\n\n          <h2 class="card-title">JD Vance\'s 2nd Kansas visit',
        '>U.S. Congress / Official Portrait (public domain)</span>\n\n          <h2 class="card-title">JD Vance\'s 2nd Kansas visit'
    )
    print(f"  POL: Replaced FDLE on Vance Kansas story with {vance}")

# Fix 2: Duplicate 8429afab3aa1a829.jpg on "Vance says Republicans shouldn't complain"
dup_pol = '8429afab3aa1a829.jpg'
if pol.count(dup_pol) > 1 and os.path.exists(os.path.join(IMG_DIR, vivek)):
    idx = pol.find(dup_pol)
    idx2 = pol.find(dup_pol, idx + 1)
    if idx2 >= 0:
        pol = pol[:idx2] + pol[idx2:].replace(dup_pol, vivek, 1)
        # Fix the credit for this card
        pol = pol.replace(
            '>Official agency image (illustrative)</span>\n\n          <h2 class="card-title">Vance says Republicans',
            '>Gage Skidmore / CC BY-SA 3.0</span>\n\n          <h2 class="card-title">Vance says Republicans'
        )
        print(f"  POL: Replaced duplicate Vance/Ramaswamy card image with {vivek}")

if pol != pol_orig:
    with open(pol_path, 'w', encoding='utf-8') as f:
        f.write(pol)
    print("  SAVED section-politics.html")

# --- FIX BUSINESS PAGE ---
biz_path = os.path.join(SITE, "section-business.html")
with open(biz_path, 'r', encoding='utf-8') as f:
    biz_page = f.read()

biz_orig = biz_page

# Fix 3: BCSO badge (7594627c794cf8f5.png) on Mexican restaurant story
bcso_img = '7594627c794cf8f5.png'
if bcso_img in biz_page and os.path.exists(os.path.join(IMG_DIR, tacos)):
    biz_page = biz_page.replace(
        f'src="/img/stories/{bcso_img}" alt="Florida Mexican restaurant with tacos expands from Palm',
        f'src="/img/stories/{tacos}" alt="Florida Mexican restaurant with tacos expands from Palm'
    )
    # Fix credit  
    biz_page = biz_page.replace(
        ">Bay County Sheriff's Office</span>\n\n          <h2 class=\"card-title\">Florida Mexican restaurant",
        ">Wikimedia Commons / CC0 (illustrative)</span>\n\n          <h2 class=\"card-title\">Florida Mexican restaurant"
    )
    print(f"  BIZ: Replaced BCSO badge on restaurant story with {tacos}")

# Fix 4: Duplicate fe6f682fef2f013c.jpg (Plumbing AND Garage Door)
dup_biz1 = 'fe6f682fef2f013c.jpg'
if biz_page.count(dup_biz1) > 1:
    replacement = garage if (garage and os.path.exists(os.path.join(IMG_DIR, garage))) else palmbeach
    if replacement and os.path.exists(os.path.join(IMG_DIR, replacement)):
        idx = biz_page.find(dup_biz1)
        idx2 = biz_page.find(dup_biz1, idx + 1)
        if idx2 >= 0:
            biz_page = biz_page[:idx2] + biz_page[idx2:].replace(dup_biz1, replacement, 1)
            print(f"  BIZ: Replaced duplicate plumbing/garage image with {replacement}")
    else:
        print(f"  BIZ: No replacement for {dup_biz1} duplicate — HOLDING story card")
        # Remove the garage door card since we can't fix it properly
        art_pattern = re.compile(r'<article class="biz-card"[^>]*>.*?</article>', re.DOTALL)
        matches = list(art_pattern.finditer(biz_page))
        for m in matches:
            if 'Florida Garage Door Pros Named 2026 Best of Florida Award Winner' in m.group(0):
                biz_page = biz_page[:m.start()] + biz_page[m.end():]
                print(f"  BIZ: HELD Garage Door story card (no valid image)")
                break

# Fix 5: FDLE badge (2ab8e1e20d5e2918.png) on Hispanic business story
fdle_biz = '2ab8e1e20d5e2918.png'
if fdle_biz in biz_page:
    # Try to use the downloaded biz image, or hold the card
    biz_img = biz if (biz and os.path.exists(os.path.join(IMG_DIR, biz))) else None
    if biz_img:
        biz_page = biz_page.replace(
            f'src="/img/stories/{fdle_biz}" alt="See the region\'s top Hispanic and Latino-owned business',
            f'src="/img/stories/{biz_img}" alt="See the region\'s top Hispanic and Latino-owned business'
        )
        biz_page = biz_page.replace(
            ">Florida Dept. of Law Enforcement (public domain)</span>\n\n          <h2 class=\"card-title\">See the region",
            ">Wikimedia Commons / CC0 (illustrative)</span>\n\n          <h2 class=\"card-title\">See the region"
        )
        print(f"  BIZ: Replaced FDLE on Hispanic business story with {biz_img}")
    else:
        # Hold the story (remove card)
        art_pattern = re.compile(r'<article class="biz-card"[^>]*>.*?</article>', re.DOTALL)
        matches = list(art_pattern.finditer(biz_page))
        for m in matches:
            if "See the region's top Hispanic and Latino-owned businesses" in m.group(0):
                biz_page = biz_page[:m.start()] + biz_page[m.end():]
                print(f"  BIZ: HELD Hispanic business story card (FDLE image — no valid replacement found)")
                break

# Fix 6: Duplicate 97537c4d53b47314.jpg (Cuban restaurant AND Palm Beach family restaurant)
dup_biz2 = '97537c4d53b47314.jpg'
if biz_page.count(dup_biz2) > 1 and os.path.exists(os.path.join(IMG_DIR, palmbeach)):
    idx = biz_page.find(dup_biz2)
    idx2 = biz_page.find(dup_biz2, idx + 1)
    if idx2 >= 0:
        biz_page = biz_page[:idx2] + biz_page[idx2:].replace(dup_biz2, palmbeach, 1)
        biz_page = biz_page.replace(
            ">CC0 / Unsplash (illustrative)</span>\n\n          <h2 class=\"card-title\">Florida family restaurant",
            ">Wikimedia Commons / CC0 (illustrative)</span>\n\n          <h2 class=\"card-title\">Florida family restaurant"
        )
        print(f"  BIZ: Replaced duplicate Cuban/PalmBeach restaurant image with {palmbeach}")

if biz_page != biz_orig:
    with open(biz_path, 'w', encoding='utf-8') as f:
        f.write(biz_page)
    print("  SAVED section-business.html")

# --- FIX INVESTIGATIONS PAGE ---
inv_path = os.path.join(SITE, "section-investigations.html")
with open(inv_path, 'r', encoding='utf-8') as f:
    inv = f.read()

inv_orig = inv

# Fix 7: Duplicate 656232930c4ce25a.jpg (now only on Shawty Dred + marriage fraud)
dup_inv = '656232930c4ce25a.jpg'
inv_count = inv.count(dup_inv)
print(f"\n  INV: {dup_inv} appears {inv_count} times")

if inv_count > 1 and wedding and os.path.exists(os.path.join(IMG_DIR, wedding)):
    idx = inv.find(dup_inv)
    idx2 = inv.find(dup_inv, idx + 1)
    if idx2 >= 0:
        inv = inv[:idx2] + inv[idx2:].replace(dup_inv, wedding, 1)
        print(f"  INV: Replaced duplicate on marriage fraud story with {wedding}")

if inv != inv_orig:
    with open(inv_path, 'w', encoding='utf-8') as f:
        f.write(inv)
    print("  SAVED section-investigations.html")

print("\n=== DONE ===")
