#!/usr/bin/env python3
"""Download replacement images using correct Wikimedia thumbnail sizes (250, 330, 500, 960px)."""
import urllib.request
import hashlib
import os
import ssl
import time

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"
IMG_DIR = os.path.join(SITE, "img", "stories")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download(url, label, ext=None):
    if ext is None:
        ext = '.jpg'
        url_lower = url.lower().split('?')[0]
        if url_lower.endswith('.png'): ext = '.png'
        elif url_lower.endswith('.webp'): ext = '.webp'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'TheHeronReport/1.0 (https://heronreport.com; news@heronreport.com) Python/3',
            'Accept': 'image/webp,image/jpeg,image/*',
        })
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            data = r.read()
            ct = r.headers.get('Content-Type', '')
            if 'png' in ct: ext = '.png'
            elif 'webp' in ct: ext = '.webp'
        if not data or len(data) < 800:
            print(f"FAIL (tiny): {label}")
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

# JD Vance official VP portrait - use correct 500px thumbnail
vance = None
for size in ['500px', '960px', '330px', '250px']:
    fname_encoded = 'JD_Vance_official_portrait_%28headshot%29.jpg'
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/{fname_encoded}/{size}-{fname_encoded}"
    vance = download(url, f"Vance VP portrait {size}")
    if vance:
        break
    time.sleep(1)

# Vivek Ramaswamy - 500px thumbnail
vivek = None
for size in ['500px', '960px', '330px']:
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Vivek_Ramaswamy_by_Gage_Skidmore.jpg/{size}-Vivek_Ramaswamy_by_Gage_Skidmore.jpg"
    vivek = download(url, f"Vivek Ramaswamy {size}")
    if vivek:
        break
    time.sleep(1)

# Tacos - 500px thumbnail 
tacos_fn = '001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg'
tacos = None
for size in ['500px', '960px', '330px']:
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/{tacos_fn}/{size}-001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg"
    tacos = download(url, f"Tacos {size}")
    if tacos:
        break
    time.sleep(1)

# Garage door 
garage = None
garage_fn = 'Garage_door_opener.jpg'
for size in ['500px', '330px', '250px']:
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/{garage_fn}/{size}-{garage_fn}"
    garage = download(url, f"Garage door {size}")
    if garage:
        break
    time.sleep(1)

# Hispanic small business
biz = None
biz_fn = 'Small_business_saturday_2012.jpg'
for size in ['500px', '330px', '250px']:
    url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/{biz_fn}/{size}-{biz_fn}"
    biz = download(url, f"Small biz {size}")
    if biz:
        break
    time.sleep(1)

# Palm Beach family restaurant (replace duplicate Cuban image)
# Use a diner/restaurant interior image
palmbeach = None
for name, h, fn in [
    ('Big Mac', '9/9a', 'Big_Mac_hamburger.jpg'),
    ('Diner', '1/12', 'Lakeview_Restaurant.jpg'),
]:
    for size in ['500px', '330px']:
        url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h}/{fn}/{size}-{fn}"
        palmbeach = download(url, f"Restaurant {name} {size}")
        if palmbeach:
            break
        time.sleep(1)
    if palmbeach:
        break

# Wedding rings for marriage fraud story
wedding = None
wedding_fn = 'Wedding_rings.jpg'
for h, fn in [('5/5e', 'Wedding_rings_displayed.jpg'), ('e/e7', 'Wedding_rings.jpg')]:
    for size in ['500px', '330px']:
        url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h}/{fn}/{size}-{fn}"
        wedding = download(url, f"Wedding rings {size}")
        if wedding:
            break
        time.sleep(1)
    if wedding:
        break

print("\nSUMMARY:")
print(f"  vance   = {vance}")
print(f"  vivek   = {vivek}")
print(f"  tacos   = {tacos}")
print(f"  garage  = {garage}")
print(f"  biz     = {biz}")
print(f"  palmbeach = {palmbeach}")
print(f"  wedding = {wedding}")
