#!/usr/bin/env python3
"""Download replacement images for audit violations."""
import urllib.request
import hashlib
import os
import ssl

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"
IMG_DIR = os.path.join(SITE, "img", "stories")

# Don't verify SSL to avoid cert issues
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download(url, label):
    ext = '.jpg'
    for e in ['.png', '.webp', '.gif', '.svg']:
        if url.lower().endswith(e):
            ext = e
            break
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*',
            'Referer': 'https://heronreport.com/'
        })
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            data = r.read()
            ctype = r.headers.get('Content-Type', '')
            if 'png' in ctype: ext = '.png'
            elif 'webp' in ctype: ext = '.webp'
        if not data or len(data) < 500:
            print(f"FAIL (too small): {label}")
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

results = {}

# 1. JD Vance image (for Kansas visit + Ramaswamy stories)
# Try official White House / Congress sources
vance = (
    download("https://www.whitehouse.gov/wp-content/uploads/2025/01/vance_official.jpg", "Vance WH") or
    download("https://upload.wikimedia.org/wikipedia/commons/9/90/JD_Vance%2C_official_portrait%2C_117th_Congress.jpg", "Vance Wiki direct") or
    download("https://thehill.com/wp-content/uploads/sites/2/2024/11/AP24318639698459.jpg?w=640", "Vance Hill")
)
results['vance'] = vance

# 2. Vivek Ramaswamy image (for Ramaswamy ad story)
vivek = (
    download("https://upload.wikimedia.org/wikipedia/commons/7/75/Vivek_Ramaswamy_official_portrait_%28cropped%29.jpg", "Ramaswamy Wiki direct") or
    download("https://thehill.com/wp-content/uploads/sites/2/2023/01/Ramaswamy_Vivek.jpg?w=640", "Ramaswamy Hill")
)
results['vivek'] = vivek

# 3. Mexican taco/restaurant image (for Mexican restaurant story)
tacos = (
    download("https://upload.wikimedia.org/wikipedia/commons/7/73/001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg", "Tacos Wiki direct") or
    download("https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvdjEwMTMtYy0xMC1rb3N6bDYwMzMuanBn.jpg", "Tacos rawpixel")
)
results['tacos'] = tacos

# 4. Garage door image (for Garage Door Pros story)
garage = (
    download("https://upload.wikimedia.org/wikipedia/commons/3/32/Garage_door_opener.jpg", "Garage Wiki direct") or
    download("https://live.staticflickr.com/5183/5639581459_b3d4e4e0d5_b.jpg", "Garage flickr")
)
results['garage'] = garage

# 5. Small business / Hispanic business image
biz = (
    download("https://upload.wikimedia.org/wikipedia/commons/5/5f/Small_business_saturday_2012.jpg", "SmallBiz Wiki direct") or
    download("https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX2NvbnRlbnQvbHIvdjEwMTEtaXAtMDU3Mi5qcGc.jpg", "SmallBiz rawpixel")
)
results['biz'] = biz

# 6. Palm Beach family restaurant image
palmbeach = (
    download("https://upload.wikimedia.org/wikipedia/commons/9/9a/Big_Mac_hamburger.jpg", "PalmBeach restaurant Wiki") or
    download("https://live.staticflickr.com/3076/5837048825_f9a8ae7e54_b.jpg", "Restaurant flickr")
)
results['palmbeach'] = palmbeach

# 7. Wedding rings / marriage fraud image (for investigations page)
wedding = (
    download("https://upload.wikimedia.org/wikipedia/commons/5/5e/Wedding_rings_displayed.jpg", "Wedding Wiki direct") or
    download("https://live.staticflickr.com/7025/6565093679_a7a7a0b3e9_b.jpg", "Wedding flickr")
)
results['wedding'] = wedding

print("\nRESULTS:")
for k, v in results.items():
    print(f"  {k}: {v}")
