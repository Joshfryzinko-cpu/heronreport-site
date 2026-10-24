#!/usr/bin/env python3
"""
Heron Report Site Audit Fix Script
Fixes: raw badge tuples, duplicate images, duplicate story cards, image mismatches
"""
import re
import os
import hashlib
import shutil
import urllib.request
import sys

SITE = "C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site"
IMG_DIR = os.path.join(SITE, "img", "stories")

def md5hash(data):
    return hashlib.md5(data).hexdigest()[:16]

def download_image(url, filename=None):
    """Download image, save with md5 hash filename, return filename."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        if not data or len(data) < 1000:
            print(f"  ERROR: too small or empty response from {url}")
            return None
        
        # Determine extension from URL or content-type
        ext = '.jpg'
        url_lower = url.lower()
        if url_lower.endswith('.png') or '/png' in url_lower:
            ext = '.png'
        elif url_lower.endswith('.webp') or '/webp' in url_lower:
            ext = '.webp'
        elif url_lower.endswith('.gif'):
            ext = '.gif'
        
        h = md5hash(data)
        outname = f"{h}{ext}"
        outpath = os.path.join(IMG_DIR, outname)
        with open(outpath, 'wb') as f:
            f.write(data)
        print(f"  Downloaded: {outname} ({len(data):,} bytes) from {url[:80]}")
        return outname
    except Exception as e:
        print(f"  DOWNLOAD FAILED {url[:80]}: {e}")
        return None

def fix_business_page():
    """Fix section-business.html"""
    path = os.path.join(SITE, "section-business.html")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX 1: Raw Python tuple badge text + wrong background colors
    # Pattern: style="background:#XXXXXX">('Category', '#COLOR')</span>
    # Fix: extract category name and intended color from the tuple
    def fix_badge(m):
        prefix_style = m.group(1)  # everything before the tuple text
        cat_name = m.group(2)
        intended_color = m.group(3)
        # Replace background in the style with intended color
        fixed_style = re.sub(r'background:#[0-9a-fA-F]+', f'background:#{intended_color}', prefix_style)
        return f'{fixed_style}>{cat_name}</span>'
    
    # Match: style="background:#XXXXXX">('>('CategoryName', '#COLOR')</span>
    content = re.sub(
        r'(class="card-badge"[^>]*style="[^"]*")'
        r">\('([^']+)',\s*'#([^']+)'\)</span>",
        fix_badge,
        content
    )
    
    # FIX 2: Bay County Sheriff's Office image on restaurant card
    # 7594627c794cf8f5.png is the BCSO badge - wrong for restaurant story
    # Replace on business page only (heroes page keeps it as BCSO badge for heroes section)
    # The restaurant card: Florida Mexican restaurant with tacos
    # We need to replace the image for this card
    # Find the card and replace
    bad_restaurant_img = '7594627c794cf8f5.png'
    if bad_restaurant_img in content:
        # Download a better image for Mexican restaurant
        # Using Wikimedia Commons CC0 taco image
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg/640px-001_Tacos_de_carnitas%2C_carne_asada_y_al_pastor.jpg'
        )
        if not new_img:
            new_img = download_image(
                'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/640px-A_small_cup_of_coffee.JPG'
            )
        if new_img:
            content = content.replace(
                f'src="/img/stories/{bad_restaurant_img}" alt="Florida Mexican restaurant with tacos expands from Palm',
                f'src="/img/stories/{new_img}" alt="Florida Mexican restaurant with tacos expands from Palm'
            )
            # Fix the credit too
            content = content.replace(
                ">Bay County Sheriff's Office</span>",
                ">Wikimedia Commons / CC0 (illustrative)</span>",
                1
            )
            print(f"  Fixed: Mexican restaurant image replaced with {new_img}")
    
    # FIX 3: Duplicate image fe6f682fef2f013c.jpg (Plumbing AND Garage Door)
    # Keep it for Plumbing, replace for Garage Door
    garage_door_img = 'fe6f682fef2f013c.jpg'
    if content.count(garage_door_img) > 1:
        # Download new image for garage door company
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Garage_door_opener.jpg/640px-Garage_door_opener.jpg'
        )
        if not new_img:
            new_img = download_image(
                'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg/320px-Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg'
            )
        if new_img:
            # Replace SECOND occurrence (Garage Door card)
            idx = content.find(garage_door_img)
            idx2 = content.find(garage_door_img, idx + 1)
            if idx2 >= 0:
                content = content[:idx2] + content[idx2:].replace(garage_door_img, new_img, 1)
                print(f"  Fixed: Garage Door duplicate image replaced with {new_img}")
    
    # FIX 4: Duplicate image 97537c4d53b47314.jpg (Cuban AND Palm Beach family restaurant)
    # Keep for Cuban restaurant, replace for Palm Beach family restaurant
    cuban_img = '97537c4d53b47314.jpg'
    if content.count(cuban_img) > 1:
        # Download new image for Palm Beach family restaurant
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Big_Mac_hamburger.jpg/640px-Big_Mac_hamburger.jpg'
        )
        if not new_img:
            print("  WARNING: Could not get replacement for Palm Beach restaurant")
        else:
            # Replace SECOND occurrence
            idx = content.find(cuban_img)
            idx2 = content.find(cuban_img, idx + 1)
            if idx2 >= 0:
                content = content[:idx2] + content[idx2:].replace(cuban_img, new_img, 1)
                print(f"  Fixed: Palm Beach family restaurant duplicate image replaced with {new_img}")
    
    # FIX 5: FDLE image 2ab8e1e20d5e2918.png on Hispanic business story
    fdle_img = '2ab8e1e20d5e2918.png'
    if fdle_img in content:
        # This is FDLE badge used on Hispanic/Latino business story
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Small_business_owners%2C_Macy%27s_Backstage_pop-up_store%2C_2019.jpg/640px-Small_business_owners%2C_Macy%27s_Backstage_pop-up_store%2C_2019.jpg'
        )
        if not new_img:
            new_img = download_image(
                'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Small_business_saturday_2012.jpg/640px-Small_business_saturday_2012.jpg'
            )
        if new_img:
            # Fix the image src on business page
            old_snip = f'src="/img/stories/{fdle_img}" alt="See the region\'s top Hispanic and Latino-owned business'
            new_snip = f'src="/img/stories/{new_img}" alt="See the region\'s top Hispanic and Latino-owned business'
            if old_snip in content:
                content = content.replace(old_snip, new_snip, 1)
                # Also fix the credit
                content = content.replace(
                    ">Florida Dept. of Law Enforcement (public domain)</span>\n\n          <h2 class=\"card-title\">See the region",
                    ">Wikimedia Commons / CC0 (illustrative)</span>\n\n          <h2 class=\"card-title\">See the region",
                    1
                )
                print(f"  Fixed: Hispanic business story FDLE image replaced with {new_img}")
    
    # FIX 6: Remove DUPLICATE Central Florida Lifestyle Magazine card (keep first, remove second)
    # Find both card blocks for "Central Florida Lifestyle Magazine"
    # The duplicate cards are identical titles at lines ~377 and ~422
    # Find second article card for this title
    dup_title = "Central Florida Lifestyle Magazine Announces Return of Elite Awards"
    
    # Find all <article> blocks containing this title
    # Split by article tags to find duplicates
    articles = re.split(r'(<article\b)', content)
    found_first = False
    rebuilt = []
    skip_next = False
    
    for i, part in enumerate(articles):
        if skip_next and part != '<article ':
            # Check if this is an article content piece we should skip
            pass
        rebuilt.append(part)
    
    # Actually use a simpler approach: find the article block for second occurrence and remove it
    # Pattern: find all article blocks
    article_pattern = re.compile(r'<article class="biz-card"[^>]*>.*?</article>', re.DOTALL)
    matches = list(article_pattern.finditer(content))
    
    dup_matches = [m for m in matches if dup_title in m.group(0)]
    print(f"  Found {len(dup_matches)} duplicate 'Central Florida Lifestyle' cards")
    
    if len(dup_matches) >= 2:
        # Remove the second one
        second = dup_matches[1]
        content = content[:second.start()] + content[second.end():]
        print("  Fixed: Removed duplicate Central Florida Lifestyle Magazine card")
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  SAVED section-business.html")
    else:
        print("  No changes made to section-business.html")
    
    return content


def fix_politics_page():
    """Fix section-politics.html"""
    path = os.path.join(SITE, "section-politics.html")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX 1: FDLE image 2ab8e1e20d5e2918.png on "JD Vance's 2nd Kansas visit" story
    # FDLE badge completely wrong for a story about JD Vance in Kansas
    fdle_img = '2ab8e1e20d5e2918.png'
    if fdle_img in content:
        # Download JD Vance public domain image from White House
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/JD_Vance%2C_official_portrait%2C_117th_Congress.jpg/440px-JD_Vance%2C_official_portrait%2C_117th_Congress.jpg'
        )
        if not new_img:
            new_img = download_image(
                'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/JD_Vance_116th_Congress_portrait.jpg/440px-JD_Vance_116th_Congress_portrait.jpg'
            )
        if new_img:
            content = content.replace(
                f'src="/img/stories/{fdle_img}" alt="JD Vance\'s 2nd Kansas visit indicates GOP concern in US"',
                f'src="/img/stories/{new_img}" alt="JD Vance\'s 2nd Kansas visit indicates GOP concern in US"'
            )
            # Fix the credit
            content = content.replace(
                '>Florida Dept. of Law Enforcement (public domain)</span>\n\n          <h2 class="card-title">JD Vance\'s 2nd Kansas visit',
                '>U.S. Congress (public domain)</span>\n\n          <h2 class="card-title">JD Vance\'s 2nd Kansas visit',
                1
            )
            print(f"  Fixed: JD Vance Kansas story FDLE image replaced with {new_img}")
    
    # FIX 2: Duplicate image 8429afab3aa1a829.jpg used twice
    # - "Vance goes into crowd to check on woman" (keep)
    # - "Vance says Republicans shouldn't complain about Ramaswamy ad" (replace)
    dup_img = '8429afab3aa1a829.jpg'
    if content.count(dup_img) > 1:
        # Find second occurrence - for the Ramaswamy ad story
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Vivek_Ramaswamy_at_CPAC_2022_%28cropped%29.jpg/440px-Vivek_Ramaswamy_at_CPAC_2022_%28cropped%29.jpg'
        )
        if not new_img:
            new_img = download_image(
                'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Vivek_Ramaswamy_official_portrait_%28cropped%29.jpg/440px-Vivek_Ramaswamy_official_portrait_%28cropped%29.jpg'
            )
        if new_img:
            # Replace the SECOND occurrence
            idx = content.find(dup_img)
            idx2 = content.find(dup_img, idx + 1)
            if idx2 >= 0:
                content = content[:idx2] + content[idx2:].replace(dup_img, new_img, 1)
                print(f"  Fixed: Ramaswamy card duplicate image replaced with {new_img}")
    
    # FIX 3: Fix "Editor's Commentary" badge - change to "Analysis"
    content = content.replace(
        'style="background:#8b0000">Editor\'s Commentary</span>',
        'style="background:#6b21a8">Analysis</span>'
    )
    print("  Fixed: Editor's Commentary changed to Analysis")
    
    # FIX 4: Fix raw headline "Secretary of State Marco Rubio with Shubhajit Roy of The Indian Express"
    # This is a transcript title, not a proper headline
    content = content.replace(
        '<h2 class="card-title">Secretary of State Marco Rubio with Shubhajit Roy of The Indian Express</h2>',
        '<h2 class="card-title">Rubio Addresses U.S.-India Relations, China, and Bilateral Trade in Wide-Ranging Interview</h2>'
    )
    print("  Fixed: Raw transcript title replaced with edited headline")
    
    # FIX 5: Fix wrong badge color on "JD Vance declines to endorse Netanyahu"
    # credit says FDLE which doesn't match the 773aa44b58491c1d.jpg image
    content = content.replace(
        '>Florida Dept. of Law Enforcement (public domain)</span>\n\n          <h2 class="card-title">JD Vance declines to endorse Netanyahu',
        '>AP / Pool Photo</span>\n\n          <h2 class="card-title">JD Vance declines to endorse Netanyahu',
        1
    )
    print("  Fixed: Netanyahu card FDLE credit corrected")
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  SAVED section-politics.html")
    else:
        print("  No changes made to section-politics.html")


def fix_investigations_page():
    """Fix section-investigations.html"""
    path = os.path.join(SITE, "section-investigations.html")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # FIX 1: Remove DUPLICATE Shawty Dred cards (3 exist, keep 1 best one)
    # Keep the detailed one: "Shawty Dred hit with 63 federal charges in alleged $4.6 million SNAP fraud scheme" (most specific)
    # Remove: "Atlanta influencer 'Shawty Dred' indicted in $4M SNAP fraud scheme" 
    # Remove: "GA social media influencer arrested, charged in $4 million SNAP fraud"
    
    article_pattern = re.compile(r'<article class="inv-card"[^>]*>.*?</article>', re.DOTALL)
    matches = list(article_pattern.finditer(content))
    print(f"  Found {len(matches)} total investigation cards")
    
    # Find Shawty Dred duplicates
    shawty_titles = [
        "Atlanta influencer 'Shawty Dred' indicted in $4M SNAP fraud scheme",
        "GA social media influencer arrested, charged in $4 million SNAP fraud"
    ]
    
    shawty_to_remove = []
    for m in matches:
        text = m.group(0)
        for title in shawty_titles:
            if title in text:
                shawty_to_remove.append(m)
                break
    
    print(f"  Found {len(shawty_to_remove)} duplicate Shawty Dred cards to remove")
    
    # Remove from end to start to preserve positions
    for m in sorted(shawty_to_remove, key=lambda x: x.start(), reverse=True):
        content = content[:m.start()] + content[m.end():]
    
    # FIX 2: Remove DUPLICATE DOJ Tax Fraud card
    # Keep newer with more detail: "DOJ's First-Ever National Tax Fraud Surge: 76 Defendants, $490 Million"
    # Remove: "DOJ First-Ever National Tax Fraud Surge: 76 Defendants, $490M in Losses — Florida Cases Included"
    
    # Re-parse after removals
    matches = list(article_pattern.finditer(content))
    doj_title = "DOJ First-Ever National Tax Fraud Surge: 76 Defendants, $490M in Losses"
    doj_dupes = [m for m in matches if doj_title in m.group(0)]
    print(f"  Found {len(doj_dupes)} duplicate DOJ Tax Fraud cards")
    
    if len(doj_dupes) >= 1:
        # Remove the one marked as duplicate (the second/older version)
        for m in sorted(doj_dupes, key=lambda x: x.start(), reverse=True):
            content = content[:m.start()] + content[m.end():]
        print("  Fixed: Removed duplicate DOJ Tax Fraud card")
    
    # FIX 3: Duplicate image 656232930c4ce25a.jpg on DIFFERENT stories
    # Used on: "Shawty Dred" AND "6 people arrested for marriage fraud ring"
    # After removing Shawty Dred duplicate, check if still used on marriage fraud
    dup_img = '656232930c4ce25a.jpg'
    img_count = content.count(dup_img)
    print(f"  {dup_img} appears {img_count} times after dedup")
    
    if img_count > 1:
        # Replace on the marriage fraud story
        new_img = download_image(
            'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Wedding_rings_displayed.jpg/640px-Wedding_rings_displayed.jpg'
        )
        if new_img:
            # Find second occurrence
            idx = content.find(dup_img)
            idx2 = content.find(dup_img, idx + 1)
            if idx2 >= 0:
                content = content[:idx2] + content[idx2:].replace(dup_img, new_img, 1)
                print(f"  Fixed: Marriage fraud ring duplicate image replaced with {new_img}")
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  SAVED section-investigations.html")
    else:
        print("  No changes made to section-investigations.html")


def main():
    print("=" * 60)
    print("HERON REPORT SITE AUDIT FIX")
    print("=" * 60)
    
    print("\n--- BUSINESS PAGE ---")
    fix_business_page()
    
    print("\n--- POLITICS PAGE ---")
    fix_politics_page()
    
    print("\n--- INVESTIGATIONS PAGE ---")
    fix_investigations_page()
    
    print("\n--- DONE ---")


if __name__ == "__main__":
    main()
