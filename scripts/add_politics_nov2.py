#!/usr/bin/env python3
"""Add 3 fresh politics stories to section-politics.html - Nov 2, 2026"""
import hashlib, requests, re, sys
from pathlib import Path

site = Path("C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site")
img_dir = site / "img/stories"

existing_stems = {f.stem for f in img_dir.glob("*")}
print(f"Existing images: {len(existing_stems)}", flush=True)

BANNED = {'8429afab3aa1a829','2ab8e1e20d5e2918','7594627c794cf8f5','80a54cc24c5d5711',
          'f024c847e358e3e3','8574e38bd76d7c0d','064dac983aafa7d6','fa3b8256b814b7ac',
          'fb5fe9a2217ed004','bc6dc8af3e22b40e','9c88cf990fe41746','e784600ef0754f0f'}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
}

# ---- Story definitions ----
stories = [
    {
        'key': 'scotus_ca_ballots',
        'title': 'Trump Appeals to Supreme Court to Block 20,000 California Mail Ballots One Day Before Election',
        'summary': 'The Trump administration asked the Supreme Court on Monday to set aside thousands of disputed California mail ballots claimed to be from possible noncitizens — an emergency appeal the day before the midterm elections, after two lower courts rejected the same request.',
        'url': 'https://abc11.com/post/trump-administration-appeals-supreme-court-push-sideline-20000-california-mail-ballots/20008299/',
        'source': 'AP / ABC News',
        'date': 'November 2, 2026',
        'badge': 'Election',
        'badge_color': '#7c3aed',
        'img_urls': [
            'https://cdn.abcotvs.com/dip/images/20008336_110226-kabc-ca-voter-rolls-tn.jpg',
            'https://cdn.abcotvs.com/dip/images/19993355_102826-kabc-11pm-ca-voter-rolls-vid.jpg',
        ],
    },
    {
        'key': 'murphy_stroke',
        'title': 'Connecticut Sen. Chris Murphy Hospitalized After Suffering Stroke',
        'summary': 'Sen. Chris Murphy, 53, was rushed to Johns Hopkins Hospital after experiencing arm numbness at his son\'s hockey game Saturday. His office says he is awake, alert, and doctors are optimistic he will make a full recovery — a sudden health scare one day before Election Day.',
        'url': 'https://apnews.com/article/chris-murphy-stroke-senate-connecticut-61676279143ddcc6f0de5f058fc6495a',
        'source': 'AP News',
        'date': 'November 2, 2026',
        'badge': 'Breaking',
        'badge_color': '#c0392b',
        'img_urls': [
            'https://assets.apnews.com/8d/1e/3af1398b5007f4d40965bc5f9abf/42f16ee2af544a47986f606b7c5db37e',
            'https://dims.apnews.com/dims4/default/578351f/2147483647/strip/true/crop/7720x5147+0+0/resize/800x533!/quality/90/?url=https%3A%2F%2Fassets.apnews.com%2F8d%2F1e%2F3af1398b5007f4d40965bc5f9abf%2F42f16ee2af544a47986f606b7c5db37e',
            'https://dims.apnews.com/dims4/default/a2b1c3d/2147483647/strip/true/crop/3867+0+0+0/resize/800x533!/quality/90/?url=https://assets.apnews.com/8d/1e/3af1398b5007f4d40965bc5f9abf/42f16ee2af544a47986f606b7c5db37e',
        ],
    },
    {
        'key': 'stevens_rogers',
        'title': "Michigan Democrat Stuns Party by Endorsing GOP's Mike Rogers Two Days Before Election",
        'summary': "Congresswoman Haley Stevens shocked Democratic leaders Sunday when she endorsed Trump-backed Republican Senate nominee Mike Rogers after attending church with him in Detroit — upending Democratic unity in one of the most critical Senate races of 2026.",
        'url': 'https://apnews.com/article/elsayed-michigan-stevens-democrats-unity-midterms-d7053bbd0ed2fd70756896c6e4b66a27',
        'source': 'AP News',
        'date': 'November 2, 2026',
        'badge': 'Elections 2026',
        'badge_color': '#0d4f8b',
        'img_urls': [
            'https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2026/11/320/180/haley-mike-rogers-church.png?ve=1&tl=1',
            'https://static.foxnews.com/foxnews.com/content/uploads/2026/11/haley-mike-rogers-church.png',
            'https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/2026/11/haley-mike-rogers-church.png',
        ],
    },
]

# ---- Download images ----
saved = {}
for s in stories:
    key = s['key']
    for url in s['img_urls']:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200 and len(r.content) > 5000:
                md5 = hashlib.md5(r.content).hexdigest()[:16]
                print(f"  {key}: HTTP 200, {len(r.content)} bytes, md5={md5}", flush=True)
                if md5 in BANNED:
                    print(f"    BANNED - skip", flush=True)
                    continue
                if md5 in existing_stems:
                    print(f"    DUPLICATE - reusing existing", flush=True)
                    saved[key] = md5
                    break
                # Save
                ext = '.jpg' if not url.lower().endswith('.png') else '.png'
                out = img_dir / f"{md5}{ext}"
                out.write_bytes(r.content)
                existing_stems.add(md5)
                print(f"    SAVED as {md5}{ext}", flush=True)
                saved[key] = md5
                break
            else:
                print(f"  {key}: HTTP {r.status_code} from {url[:60]}", flush=True)
        except Exception as e:
            print(f"  {key}: ERROR {e} from {url[:60]}", flush=True)

    if key not in saved:
        print(f"WARNING: No image saved for {key}", flush=True)

print(f"\nSaved images: {saved}", flush=True)

if len(saved) < 3:
    print("ERROR: Could not get images for all 3 stories. Aborting.", flush=True)
    sys.exit(1)

# ---- Build card HTML ----
def make_card(s, md5):
    ext = '.png' if 'png' in s['img_urls'][0].lower() else '.jpg'
    # Detect if saved file is png or jpg
    for e in ['.jpg', '.png', '.webp']:
        if (img_dir / f"{md5}{e}").exists():
            ext = e
            break
    img_path = f"/img/stories/{md5}{ext}"
    return f"""
<article class="pol-card">
  <a href="{s['url']}" target="_blank" rel="noopener" class="card-link">
    <div class="card-img-wrap">
      <img src="{img_path}" alt="{s['title']}" class="card-img" style="object-fit:cover;object-position:center" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
      <span class="card-badge" style="background:{s['badge_color']}">{s['badge']}</span>
    </div>
    <div class="card-body">
      <h2 class="card-title">{s['title']}</h2>
      <p class="card-summary">{s['summary']}</p>
      <div class="card-foot">
        <span class="card-source">{s['source']}</span>
        <span class="card-date">{s['date']}</span>
      </div>
    </div>
  </a>
</article>"""

new_cards_html = '\n'.join(make_card(s, saved[s['key']]) for s in stories if s['key'] in saved)

# ---- Inject into section-politics.html ----
page_path = site / "section-politics.html"
html = page_path.read_text(encoding='utf-8')

# Find first external link card (href="http...)
# Must insert AFTER all internal cards (href="/...) and BEFORE first external card
first_ext = re.search(r'(<article class="pol-card">\s*<a href="https?://)', html)
if not first_ext:
    print("ERROR: Could not find first external card!", flush=True)
    sys.exit(1)

insert_pos = first_ext.start()
print(f"Inserting before external card at char position {insert_pos}", flush=True)

# Also check there are internal cards before this position
pre_html = html[:insert_pos]
internal_cards = re.findall(r'href="/', pre_html)
print(f"Internal cards before insertion point: {len(internal_cards)}", flush=True)

new_html = html[:insert_pos] + new_cards_html + '\n\n' + html[insert_pos:]
page_path.write_text(new_html, encoding='utf-8')
print(f"Written section-politics.html ({len(new_html)} chars)", flush=True)

# Verify
verify = page_path.read_text(encoding='utf-8')
for s in stories:
    if s['key'] in saved:
        found = s['title'][:30] in verify
        print(f"Verify '{s['title'][:40]}': {'OK' if found else 'MISSING'}", flush=True)

print("\nDone.", flush=True)
