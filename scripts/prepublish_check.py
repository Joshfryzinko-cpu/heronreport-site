#!/usr/bin/env python3
"""
Pre-publish validator for The Heron Report.

Runs AFTER a publish script generates/updates HTML, BEFORE the workflow
commits and pushes. Exits non-zero (failing the job, blocking the push) if
any card on a checked page has:

  1. A missing/broken image (placeholder.svg used as the PRIMARY src, not
     just the onerror fallback).
  2. Generic Heron Report branding used AS the story thumbnail (a card image
     pointing at the site's own logo/branding assets instead of a real photo).
  3. A duplicate image file reused across two or more different story cards
     on the same page (same photo claimed for two different stories).
  4. A county name in the card's credit/badge that is NOT mentioned anywhere
     in that card's own headline or description text (county label
     conflicting with the story's own verified content).

This was built after tracing the recurring Heroes-of-the-Week / Business-page
errors to: (a) publish_heroes.py's old hardcoded per-category badge fallback
(always Gulf County for EMS, Bay County Sheriff for law, Seminole County for
fire, regardless of the real story), and (b) old one-off patch scripts that
inserted content bypassing the normal publish pipeline's image checks
entirely. Those bugs are now fixed at the source, but this gate exists so
that ANY future bug of this shape (in these scripts, a new one-off script, or
a manual edit) gets caught before it goes live, not after.

Usage: python3 scripts/prepublish_check.py heroes.html section-business.html ...
Exit code 0 = clean. Exit code 1 = violations found (printed to stdout).
"""
import re
import sys
import hashlib
import urllib.request

GENERIC_BRANDING_MARKERS = [
    'heronreport-logo', 'heron-report-logo', '/img/logo', '/img/heron',
    '/img/brand', 'placeholder.svg',
]

# Known Florida counties we actively badge/label -- used to check a credit's
# named county actually appears in the story's own text.
KNOWN_COUNTIES = [
    'gulf county', 'bay county', 'franklin county', 'calhoun county',
    'liberty county', 'wakulla county', 'jackson county', 'washington county',
    'holmes county', 'walton county', 'okaloosa county', 'santa rosa county',
    'escambia county', 'leon county',
]


def extract_cards(html):
    """Pull out (href, img_src_primary, credit_text, badge_text, headline, desc)
    for every card-like article block, handling both hero-cards and
    biz/pol-cards (different internal markup)."""
    cards = []
    for block in re.findall(r'<article class="(?:biz-card|pol-card)">.*?</article>', html, re.DOTALL):
        img = re.search(r'<img src="([^"]+)"', block)
        credit = re.search(r'class="card-credit"[^>]*>([^<]*)<', block)
        badge = re.search(r'class="card-badge"[^>]*>([^<]*)<', block)
        headline = re.search(r'class="card-title">(.*?)</h2>', block, re.DOTALL)
        href = re.search(r'href="([^"]+)"', block)
        cards.append({
            'img': img.group(1) if img else '',
            'credit': credit.group(1).strip() if credit else '',
            'badge': badge.group(1).strip() if badge else '',
            'headline': re.sub(r'<[^>]+>', '', headline.group(1)) if headline else '',
            'href': href.group(1) if href else '',
            'kind': 'biz/pol',
        })
    for block in re.findall(r'<div class="hero-card">.*?</div>\s*</div>\s*</div>', html, re.DOTALL):
        img = re.search(r'<img src="([^"]+)"', block)
        credit = re.search(r'class="hc-credit"[^>]*>([^<]*)<', block)
        note = re.search(r'class="hc-dept[^"]*">([^<]*)<', block)
        headline = re.search(r'class="hc-name">(.*?)</div>', block, re.DOTALL)
        hc_title = re.search(r'class="hc-title">(.*?)</div>', block, re.DOTALL)
        desc = re.search(r'class="hc-desc">(.*?)</p>', block, re.DOTALL)
        combined_text = ' '.join([
            re.sub(r'<[^>]+>', '', headline.group(1)) if headline else '',
            re.sub(r'<[^>]+>', '', hc_title.group(1)) if hc_title else '',
            re.sub(r'<[^>]+>', '', desc.group(1)) if desc else '',
        ])
        cards.append({
            'img': img.group(1) if img else '',
            'credit': credit.group(1).strip() if credit else '',
            'badge': note.group(1).strip() if note else '',
            'headline': combined_text,
            'href': '',
            'kind': 'hero',
        })
    return cards


def check_page(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    cards = extract_cards(html)
    violations = []

    seen_images = {}
    for i, c in enumerate(cards):
        label = f"card #{i+1} ({c['headline'][:50]!r})"

        # 1. Missing/broken image used as PRIMARY src.
        # Exception: a placeholder is allowed ONLY if it's honestly disclosed as
        # pending/flagged-for-review (credit/alt text says so explicitly) --
        # per editorial rule "if you can't verify an image, flag it for review"
        # rather than publish it looking like a confirmed photo. Anything else
        # (silent placeholder, no disclosure) still blocks.
        if not c['img'] or 'placeholder.svg' in c['img']:
            disclosed = bool(re.search(r'pending|flagged for review', c['credit'], re.I))
            if not disclosed:
                violations.append(f"[{path}] {label}: missing/placeholder image used as primary thumbnail with NO pending-review disclosure")

        # 2. Generic Heron Report branding used as a story thumbnail
        for marker in GENERIC_BRANDING_MARKERS:
            if marker != 'placeholder.svg' and marker in c['img'].lower():
                violations.append(f"[{path}] {label}: generic site-branding image used as story thumbnail ({c['img']})")

        # 3. Duplicate image across different cards
        if c['img'] and 'placeholder.svg' not in c['img']:
            if c['img'] in seen_images:
                other = seen_images[c['img']]
                violations.append(
                    f"[{path}] {label}: same image reused from {other!r} -- duplicate thumbnail")
            else:
                seen_images[c['img']] = c['headline'][:50]

        # 4. County label conflicts with the story's own text
        credit_lower = c['credit'].lower()
        story_text = c['headline'].lower()
        for county in KNOWN_COUNTIES:
            if county in credit_lower and county not in story_text:
                violations.append(
                    f"[{path}] {label}: credit says {county!r} but that county is not named anywhere in the story text/headline")

    return violations


def main():
    paths = sys.argv[1:]
    if not paths:
        print("Usage: prepublish_check.py <file.html> [more files...]")
        sys.exit(2)

    all_violations = []
    for path in paths:
        try:
            all_violations.extend(check_page(path))
        except FileNotFoundError:
            print(f"WARNING: {path} not found, skipping")

    if all_violations:
        print(f"\n❌ PREPUBLISH CHECK FAILED — {len(all_violations)} violation(s):\n")
        for v in all_violations:
            print(f"  - {v}")
        print("\nBlocking commit/push. Fix the source content or the generator script before publishing.")
        sys.exit(1)

    print(f"✅ Prepublish check passed for: {', '.join(paths)}")
    sys.exit(0)


if __name__ == '__main__':
    main()
