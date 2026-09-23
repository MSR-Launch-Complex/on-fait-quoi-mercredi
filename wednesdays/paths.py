"""Where things live. One place, so a caller never joins paths by hand."""

from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA = os.path.join(ROOT, "data")
ACTIVITIES = os.path.join(DATA, "activities")
ORGANISERS = os.path.join(DATA, "organisers")
TAGS = os.path.join(DATA, "tags.yml")
CONTENT = os.path.join(ROOT, "content")
ABOUT = os.path.join(CONTENT, "about_fr.md")
ASSETS = os.path.join(ROOT, "assets")
ICONS = os.path.join(ASSETS, "icons")
STYLESHEET = os.path.join(ASSETS, "site.css")
SITE = os.path.join(ROOT, "site")
