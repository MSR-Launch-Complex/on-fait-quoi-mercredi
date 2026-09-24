"""Shared plumbing: where the fixtures are, and how to get a writable copy of them."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
FIXTURE_DATA = os.path.join(FIXTURES, "data")
FIXTURE_ABOUT = os.path.join(FIXTURES, "content", "about_fr.md")


class FixtureCase(unittest.TestCase):
    """A test that edits data. Each one gets its own copy, so they cannot interfere."""

    def setUp(self):
        self.workspace = tempfile.mkdtemp(prefix="wednesdays-test-")
        self.addCleanup(shutil.rmtree, self.workspace, True)
        self.data = os.path.join(self.workspace, "data")
        shutil.copytree(FIXTURE_DATA, self.data)
        self.about = os.path.join(self.workspace, "about_fr.md")
        shutil.copyfile(FIXTURE_ABOUT, self.about)
        self.site = os.path.join(self.workspace, "site")

    def activity(self, slug):
        return os.path.join(self.data, "activities", "%s.yml" % slug)

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def edit(self, path, old, new):
        """Replace one line in a data file, to make it wrong in exactly one way."""
        text = self.read(path)
        self.assertIn(old, text, "fixture no longer contains %r" % old)
        self.write(path, text.replace(old, new))
