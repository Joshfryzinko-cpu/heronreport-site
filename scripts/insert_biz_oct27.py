"""
insert_biz_oct27.py — Insert 3 story cards into October 27 card-grid,
clean up duplicate empty date rows, keep newest 21 days
"""
import re
from pathlib import Path
from datetime import date, timedelta

SITE = Path("C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site")
PAGE = SITE / "section-business.html"

# The 3 stories with their confirmed images
CARDS_HTML = """
    <article class="biz-card">
      <a href="https://www.clickorlando.com/news/space-news/2026/10/21/subcontractor-at-kennedy-space-center-is-laying-off-workers/" class="card-link" target="_blank" rel="noopener">
        <div class="card-img-wrap">
          <img src="/img/stories/3a7266887589dbad.jpg" alt="Kennedy Space Center subcontractor layoffs" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
          <span class="card-badge" style="background:#1a5c38">Business</span>
          <span class="card-credit">Click Orlando</span>
        </div>
        <div class="card-body">
          <h2 class="card-title">Subcontractor at Kennedy Space Center Laying Off Workers</h2>
          <p class="card-summary">A subcontractor at Kennedy Space Center is shedding jobs, impacting workers tied to Florida&#39;s space coast economy.</p>
          <div class="card-foot">
            <span class="card-source">Click Orlando</span>
            <span class="card-date">October 21, 2026</span>
          </div>
        </div>
      </a>
    </article>
    <article class="biz-card">
      <a href="https://news4jax.com/news/local/2026/10/23/fitch-downgrades-jtas-credit-rating-cites-weakened-financial-resilience-amid-40m-budget-shortfall" class="card-link" target="_blank" rel="noopener">
        <div class="card-img-wrap">
          <img src="/img/stories/773425d6d113762d.jpg" alt="Jacksonville Transportation Authority credit downgrade" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
          <span class="card-badge" style="background:#1a5c38">Finance</span>
          <span class="card-credit">News4Jax</span>
        </div>
        <div class="card-body">
          <h2 class="card-title">Fitch Downgrades Jacksonville Transit Authority Amid $40M Budget Shortfall</h2>
          <p class="card-summary">Fitch cut JTA&#39;s credit rating two notches to AA- after the agency&#39;s $39 million shortfall triggered nearly 200 layoffs and service cuts.</p>
          <div class="card-foot">
            <span class="card-source">News4Jax</span>
            <span class="card-date">October 23, 2026</span>
          </div>
        </div>
      </a>
    </article>
    <article class="biz-card">
      <a href="https://www.fox13news.com/news/florida-ag-targets-insurance-policy-rules-banning-public-adjusters" class="card-link" target="_blank" rel="noopener">
        <div class="card-img-wrap">
          <img src="/img/stories/9c316ebe1f6a98a2.jpg" alt="Florida AG insurance probe public adjusters" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
          <span class="card-badge" style="background:#1a5c38">Insurance</span>
          <span class="card-credit">FOX 13</span>
        </div>
        <div class="card-body">
          <h2 class="card-title">Florida AG Probes Insurer Over Rules Blocking Public Adjusters</h2>
          <p class="card-summary">AG James Uthmeier opened an investigation into Velocity Risk Underwriters over policy clauses that bar homeowners from hiring public adjusters on storm claims.</p>
          <div class="card-foot">
            <span class="card-source">FOX 13 Tampa Bay</span>
            <span class="card-date">October 21, 2026</span>
          </div>
        </div>
      </a>
    </article>"""

html = PAGE.read_text(encoding="utf-8")

# Target: the first card-grid after the October 27 day-sep
# Replace:  <div class="card-grid">\n    </div>  (the empty Oct 27 grid)
# With the cards inserted

# Find the Oct 27 day-sep section followed by empty card-grid
old_snippet = """<div class="day-sep">
    <div class="day-line"></div>
    <div class="day-label">Published</div>
    <div class="day-date">October 27, 2026</div>
    <div class="day-line"></div>
  </div>
  <div class="card-grid">
    </div>"""

new_snippet = """<div class="day-sep">
    <div class="day-line"></div>
    <div class="day-label">Published</div>
    <div class="day-date">October 27, 2026</div>
    <div class="day-line"></div>
  </div>
  <div class="card-grid">""" + CARDS_HTML + """
  </div>"""

if old_snippet in html:
    html = html.replace(old_snippet, new_snippet, 1)
    print("Inserted 3 cards into Oct 27 grid")
else:
    print("ERROR: Could not find Oct 27 empty grid snippet")
    print("Looking for it...")
    # Try to find the Oct 27 card-grid
    idx = html.find('October 27, 2026')
    if idx > -1:
        print(f"Found Oct 27 at char {idx}")
        print(repr(html[idx:idx+200]))
    import sys
    sys.exit(1)

# Now remove duplicate empty date rows. Keep only one per date.
# Strategy: find all day-sep + card-grid pairs, deduplicate
# For dates older than 21 days from today, remove them too

today = date.today()  # Oct 27, 2026
cutoff = today - timedelta(days=21)  # Oct 6, 2026

# Pattern for empty date+grid block
empty_block_pattern = re.compile(
    r'\s*<div class="day-sep">\s*<div class="day-line"></div>\s*<div class="day-label">[^<]*</div>\s*<div class="day-date">([^<]*)</div>\s*<div class="day-line"></div>\s*</div>\s*<div class="card-grid">\s*</div>',
    re.IGNORECASE
)

seen_dates = set()
removed = 0

def handle_match(m):
    global removed
    date_str = m.group(1).strip()
    # Parse the date
    try:
        from datetime import datetime
        d = datetime.strptime(date_str, "%B %d, %Y").date()
    except:
        # Keep malformed dates
        return m.group(0)
    if d < cutoff:
        removed += 1
        return ""  # Remove blocks older than 21 days
    if date_str in seen_dates:
        removed += 1
        return ""  # Remove duplicate date blocks
    seen_dates.add(date_str)
    return m.group(0)  # Keep unique, recent, empty blocks

# Process but skip the Oct 27 block we just filled (it has cards now, not empty)
html = empty_block_pattern.sub(handle_match, html)

print(f"Removed {removed} empty/duplicate/old date rows")

PAGE.write_text(html, encoding="utf-8")
print(f"Written {len(html)} chars to {PAGE}")

# Verify
verify = PAGE.read_text(encoding="utf-8")
ksc_ok = "Kennedy Space Center Laying Off Workers" in verify
jta_ok = "Jacksonville Transit Authority" in verify
ag_ok = "Velocity Risk Underwriters" in verify
print(f"Verify: KSC={ksc_ok}, JTA={jta_ok}, AG={ag_ok}")
