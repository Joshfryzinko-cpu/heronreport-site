import re
from pathlib import Path
from datetime import datetime, timedelta

SITE = Path('C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site')
page = SITE / 'section-investigations.html'
html = page.read_text(encoding='utf-8')

# Image results from ImageGuard run
img1 = '/img/stories/dc1fbba1c08ce0cc.jpg'   # Kissimmee Mayor arrest photo
img2 = '/img/stories/cc83efff2964ee6e.jpg'   # PBSO police cars
img3 = '/img/placeholder.svg'                # DOJ tax story - placeholder

# 3 new inv-card blocks for October 27, 2026
new_cards = f"""
<div class="day-sep">
  <div class="day-line"></div>
  <span class="day-label">Published</span>
  <span class="day-date">October 27, 2026</span>
  <div class="day-line"></div>
</div>
<div class="card-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:24px;padding:0 0 12px">

  <article class="inv-card">
    <a href="https://www.wfla.com/news/florida/kissimmee-mayor-arrested-for-abusing-her-office-for-personal-gain-fl-cfo-says/" class="card-link" target="_blank" rel="noopener">
      <div class="card-img-wrap">
        <img src="{img1}" alt="Kissimmee Mayor Jackie Espinosa arrested" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
        <span class="card-badge" style="background:#7c2d12">Florida Corruption</span>
        <span class="card-credit">WFLA / Osceola County Jail</span>
      </div>
      <div class="card-body">
        <h2 class="card-title">Kissimmee Mayor Arrested for Funneling $50K in COVID Relief to Family Businesses</h2>
        <p class="card-summary">Kissimmee Mayor Jackie Espinosa was arrested Wednesday after a joint investigation by FDLE and the Florida Department of Financial Services found she steered $50,000 in federal pandemic relief grants to businesses owned by her family — even after the city attorney warned her it was a prohibited conflict of interest. She faces up to 30 years in prison on felony grand theft and organized fraud charges. <em>Espinosa has pleaded not guilty; all charges are allegations and she is presumed innocent unless convicted.</em></p>
        <div class="card-foot">
          <span class="card-source">WFLA</span>
          <span class="card-date">Oct 21, 2026</span>
        </div>
      </div>
    </a>
  </article>

  <article class="inv-card">
    <a href="https://www.wlrn.org/government-politics/2026-10-20/missing-receipts-overcharges-unapproved-spending-audit-slams-54m-pbso-hq-renovation" class="card-link" target="_blank" rel="noopener">
      <div class="card-img-wrap">
        <img src="{img2}" alt="Palm Beach County Sheriff's Office vehicles" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
        <span class="card-badge" style="background:#7c2d12">Florida Accountability</span>
        <span class="card-credit">PBSO / WLRN</span>
      </div>
      <div class="card-body">
        <h2 class="card-title">Audit Slams $54M Palm Beach Sheriff HQ Renovation: Missing Receipts, $903K in Unauthorized Payments</h2>
        <p class="card-summary">A Palm Beach County Inspector General audit found the construction manager on the $54M PBSO headquarters overhaul was overpaid by $223,000 — billing for costs it couldn't document — while county staff approved more than $903,000 in unauthorized change orders, sometimes more than a year before commissioners gave formal approval. The project is funded by a voter-approved one-cent surtax.</p>
        <div class="card-foot">
          <span class="card-source">WLRN</span>
          <span class="card-date">Oct 20, 2026</span>
        </div>
      </div>
    </a>
  </article>

  <article class="inv-card">
    <a href="https://www.justice.gov/opa/pr/dojs-fraud-division-irs-and-irs-ci-expose-more-490m-tax-fraud-national-tax-enforcement-surge" class="card-link" target="_blank" rel="noopener">
      <div class="card-img-wrap">
        <img src="{img3}" alt="DOJ National Tax Enforcement Surge" class="card-img" loading="lazy" onerror="this.onerror=null;this.src='/img/placeholder.svg'">
        <span class="card-badge" style="background:#1a3a5c">Federal Enforcement</span>
        <span class="card-credit">U.S. Department of Justice</span>
      </div>
      <div class="card-body">
        <h2 class="card-title">DOJ Exposes $490M in Tax Fraud in First-Ever National Tax Enforcement Surge</h2>
        <p class="card-summary">The Justice Department's Fraud Division and IRS Criminal Investigation announced prosecution actions against 76 defendants in the first-ever National Tax Enforcement Surge, exposing over $490 million in alleged and proven tax fraud. The Middle District of Florida participated, including the extradition of a Tampa-area defendant charged in a multi-million dollar scheme. <em>Defendants charged but not yet convicted are presumed innocent under the law.</em></p>
        <div class="card-foot">
          <span class="card-source">U.S. Department of Justice</span>
          <span class="card-date">Oct 14, 2026</span>
        </div>
      </div>
    </a>
  </article>

</div>
"""

# Insert new date section before the existing grid-wrap content
# The existing content starts after <div class="grid-wrap">
insert_marker = '<div class="grid-wrap">'
if insert_marker in html:
    html = html.replace(insert_marker, insert_marker + '\n' + new_cards, 1)
    print("Inserted new date section successfully.")
else:
    print("ERROR: could not find grid-wrap marker")

# Write updated page
page.write_text(html, encoding='utf-8')
print("File written.")

# Verify insertion
check = 'Kissimmee Mayor Arrested' in html and 'PBSO HQ Renovation' in html and 'DOJ Exposes' in html
print(f"Verification: all 3 stories present = {check}")
