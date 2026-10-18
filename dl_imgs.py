
import requests, hashlib, os, sys

IMG_DIR = 'img/stories'
os.makedirs(IMG_DIR, exist_ok=True)

def download_img(url, fallback=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    for u in ([url] + ([fallback] if fallback else [])):
        try:
            r = requests.get(u, headers=headers, timeout=20, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 2000:
                ext = u.split('?')[0].split('.')[-1].lower()
                if ext not in ('jpg','jpeg','png','webp','gif','svg'):
                    ext = 'jpg'
                fname = hashlib.md5(u.encode()).hexdigest()[:16] + '.' + ext
                path = os.path.join(IMG_DIR, fname)
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f'OK: {fname} ({len(r.content)} bytes)')
                return fname
            else:
                print(f'FAIL {r.status_code} len={len(r.content)} - {u[:80]}')
        except Exception as e:
            print(f'ERR: {str(e)[:80]}')
    return None

# 1. Maduro - Wikimedia Commons (CC-BY-SA)
r1 = download_img(
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Nicol%C3%A1s_Maduro_Moros_en_el_Ministerio_de_la_Defensa.jpg/640px-Nicol%C3%A1s_Maduro_Moros_en_el_Ministerio_de_la_Defensa.jpg'
)

# 2. MDC Brooklyn exterior - Wikimedia CC
r2 = download_img(
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/MDC_Brooklyn.jpg/800px-MDC_Brooklyn.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/1/1b/MDC_Brooklyn.jpg'
)

# 3. FDLE seal for Nick Mimms/Florida corruption story (SVG thumbnail)
r3 = download_img(
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Seal_of_the_Florida_Department_of_Law_Enforcement.svg/240px-Seal_of_the_Florida_Department_of_Law_Enforcement.svg.png'
)

print('---RESULTS---')
print('MADURO:', r1)
print('MDC:', r2)
print('FDLE:', r3)
