"""The À propos text: one file, two places on the page.

content/about_fr.md is the site's own description (design §2). It is what the footer
shows and what a link preview quotes, and there is exactly one copy of it so the two
can never drift apart. The file is plain paragraphs separated by blank lines; anything
that looks like Markdown markup is shown as typed, not interpreted.
"""

from __future__ import annotations

import html
import re

from . import paths


class AboutMissing(Exception):
    """The site cannot be built without its own description."""


class About(object):
    def __init__(self, paragraphs):
        self.paragraphs = paragraphs

    @property
    def text(self):
        """One line, for a meta description or a link preview."""
        return " ".join(self.paragraphs)

    @property
    def first_sentence(self):
        """The design's header band is one sentence from the same paragraph (§4)."""
        return re.split(r"(?<=[.!?])\s", self.paragraphs[0].strip(), maxsplit=1)[0]

    @property
    def html(self):
        return "\n".join("<p>%s</p>" % html.escape(p) for p in self.paragraphs)


def load(path=paths.ABOUT):
    try:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
    except OSError as error:
        raise AboutMissing("%s: %s" % (path, error.strerror or error))
    paragraphs = [" ".join(block.split()) for block in re.split(r"\n\s*\n", raw) if block.strip()]
    if not paragraphs:
        raise AboutMissing("%s: the À propos text is empty" % path)
    return About(paragraphs)
