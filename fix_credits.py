#!/usr/bin/env python3
"""Fix remaining credit text errors and remove the raw RSS Vance card."""
import re, os

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"

# --- POLITICS PAGE ---
pol_path = os.path.join(SITE, "section-politics.html")
with open(pol_path, 'r', encoding='utf-8') as f:
    pol = f.read()
orig = pol

# Fix 1: Credit on Vance Kansas card (image already replaced with Vance portrait)
# The img has c14a9c7237e69e53.jpg but credit says FDLE
pol = pol.replace(
    'src="/img/stories/c14a9c7237e69e53.jpg" alt="JD Vance\'s 2nd Kansas visit indicates GOP concern in US" class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#b91c1c">Administration</span>\n          <span class="card-credit">Florida Dept. of Law Enforcement (public domain)</span>',
    'src="/img/stories/c14a9c7237e69e53.jpg" alt="JD Vance\'s 2nd Kansas visit indicates GOP concern in US" class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#b91c1c">Administration</span>\n          <span class="card-credit">U.S. Congress / Official Portrait (public domain)</span>'
)
print(f"POL Kansas Vance credit: {'fixed' if pol != orig else 'no match'}")
check = pol

# Fix 2: Netanyahu card credit (FDLE) - change to AP/pool
pol = pol.replace(
    '773aa44b58491c1d.jpg" alt="JD Vance declines to endorse Netanyahu for reelection, " class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#b91c1c">Administration</span>\n          <span class="card-credit">Florida Dept. of Law Enforcement (public domain)</span>',
    '773aa44b58491c1d.jpg" alt="JD Vance declines to endorse Netanyahu for reelection, " class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#b91c1c">Administration</span>\n          <span class="card-credit">AP / Pool Photo</span>'
)
print(f"POL Netanyahu credit: {'fixed' if pol != check else 'no match'}")
check = pol

# Fix 3: Nebraska midterm rally card credit (FDLE on Vance rally image)
pol = pol.replace(
    'e784600ef0754f0f.jpg" alt="JD Vance is coming to Nebraska for a North Platte midte" class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#b91c1c">Administration</span>\n          <span class="card-credit">Florida Dept. of Law Enforcement (public domain)</span>',
    'e784600ef0754f0f.jpg" alt="JD Vance is coming to Nebraska for a North Platte midte" class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#b91c1c">Administration</span>\n          <span class="card-credit">Nebraska Examiner / AP</span>'
)
print(f"POL Nebraska credit: {'fixed' if pol != check else 'no match'}")
check = pol

# Fix 4: Remove "Vance faces tough questions in CBS town hall" card
# It has: plumbing company image + raw RSS headline (summary = headline) + Google redirect URL
art_pattern = re.compile(r'<article class="pol-card"[^>]*>.*?</article>', re.DOTALL)
matches = list(art_pattern.finditer(pol))
cbs_card = [m for m in matches if 'Vance faces tough questions on Iran war' in m.group(0)]
print(f"POL CBS town hall cards found: {len(cbs_card)}")
for m in sorted(cbs_card, key=lambda x: x.start(), reverse=True):
    pol = pol[:m.start()] + pol[m.end():]
    print(f"  Removed raw RSS card: 'Vance faces tough questions...'")

if pol != orig:
    with open(pol_path, 'w', encoding='utf-8') as f:
        f.write(pol)
    print("SAVED section-politics.html")

# --- BUSINESS PAGE ---
biz_path = os.path.join(SITE, "section-business.html")
with open(biz_path, 'r', encoding='utf-8') as f:
    biz = f.read()
biz_orig = biz

# Fix 5: Bay County Sheriff's Office credit on Mexican restaurant card (image already fixed to tacos)
biz = biz.replace(
    '84aed607550bf38c.jpg" alt="Florida Mexican restaurant with tacos expands from Palm" class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#166534">Restaurant</span>\n          <span class="card-credit">Bay County Sheriff\'s Office</span>',
    '84aed607550bf38c.jpg" alt="Florida Mexican restaurant with tacos expands from Palm" class="card-img" style="object-fit:cover;object-position:top center" loading="lazy" onerror="this.onerror=null;this.src=\'/img/placeholder.svg\';this.style=\'object-fit:contain;padding:20px;background:#111\'">\n          <span class="card-badge" style="background:#166534">Restaurant</span>\n          <span class="card-credit">Wikimedia Commons / CC0 (illustrative)</span>'
)
print(f"\nBIZ Mexican restaurant credit: {'fixed' if biz != biz_orig else 'no match'}")

if biz != biz_orig:
    with open(biz_path, 'w', encoding='utf-8') as f:
        f.write(biz)
    print("SAVED section-business.html")

# Final verification
print("\n=== FINAL VERIFICATION ===")
for fname in ['section-politics.html', 'section-business.html']:
    path = os.path.join(SITE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    fdle = content.count('Florida Dept. of Law Enforcement')
    bcso = content.count("Bay County Sheriff's Office")
    fe6f = content.count('fe6f682fef2f013c')
    print(f"{fname}: FDLE={fdle}, BCSO={bcso}, plumbing_img={fe6f}")

print("\nDone.")
