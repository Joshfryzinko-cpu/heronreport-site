#!/usr/bin/env python3
"""Check recent image registry entries."""
import sys
sys.path.insert(0, 'C:/Users/Dryer/AppData/Local/hermes/cache/scratch/heronreport-site/scripts')
from image_guard import ImageGuard
g = ImageGuard()
for e in g._entries[-6:]:
    print(e.get('local_path'), '|', e.get('source_url','')[:80], '|', e.get('story_context','')[:40])
