"""The reader parses what the data files use, and refuses what it does not understand.

The second half matters more than the first: a reader that quietly mis-parses a file it
cannot handle would publish wrong information without anybody noticing.
"""

from __future__ import annotations

import datetime
import glob
import os
import unittest

from wednesdays import paths
from wednesdays.yaml_subset import YamlSubsetError, loads

try:
    import yaml as pyyaml
except ImportError:  # the build never needs it; the cross-check is skipped without it
    pyyaml = None


class ParsesTheSubset(unittest.TestCase):
    def test_mapping_of_scalars(self):
        doc = loads("title_fr: Les mercredis\nages: [3, 11]\ncount: 7\nok: true\nnone: null\n")
        self.assertEqual(
            doc, {"title_fr": "Les mercredis", "ages": [3, 11], "count": 7, "ok": True, "none": None}
        )

    def test_nested_mapping_and_sequence(self):
        doc = loads(
            "events:\n"
            "  - date: 2026-09-23\n"
            "    kind: appel\n"
            "  - date: 2026-09-24\n"
            "    kind: crawl\n"
            "organiser:\n"
            "  name: MJC\n"
            "  commune: Annecy\n"
        )
        self.assertEqual(doc["events"][1], {"date": "2026-09-24", "kind": "crawl"})
        self.assertEqual(doc["organiser"]["commune"], "Annecy")

    def test_empty_flow_sequence(self):
        self.assertEqual(loads("events: []\n"), {"events": []})

    def test_quotes_and_escapes(self):
        doc = loads('a: "deux\\nlignes"\nb: \'l\'\'école\'\nc: "12 € : cher"\n')
        self.assertEqual(doc, {"a": "deux\nlignes", "b": "l'école", "c": "12 € : cher"})

    def test_comments_are_dropped_but_not_inside_quotes(self):
        doc = loads("# a comment\nkey: value # trailing\nurl: \"https://x.test/#anchor\"\n")
        self.assertEqual(doc, {"key": "value", "url": "https://x.test/#anchor"})

    def test_block_scalars(self):
        doc = loads("literal: |\n  un\n  deux\nfolded: >-\n  un\n  deux\n")
        self.assertEqual(doc, {"literal": "un\ndeux\n", "folded": "un deux"})

    def test_dates_stay_text(self):
        """The schema, not the reader, decides whether a date is a real date."""
        self.assertEqual(loads("verified_on: 2026-09-23\n"), {"verified_on": "2026-09-23"})


class RefusesTheRest(unittest.TestCase):
    def assertRefused(self, text, expected):
        with self.assertRaises(YamlSubsetError) as caught:
            loads(text, origin="fichier.yml")
        message = str(caught.exception)
        self.assertIn(expected, message)
        self.assertTrue(message.startswith("fichier.yml:"), message)

    def test_tab_indentation(self):
        self.assertRefused("a:\n\t- x\n", "tab")

    def test_anchors(self):
        self.assertRefused("a: &anchor x\n", "anchors")

    def test_flow_mapping(self):
        self.assertRefused("a: {b: 1}\n", "flow mappings")

    def test_multiple_documents(self):
        self.assertRefused("a: 1\n---\nb: 2\n", "documents")

    def test_duplicate_key(self):
        self.assertRefused("a: 1\na: 2\n", "duplicate key")

    def test_key_without_value(self):
        self.assertRefused("events:\nstatus: verified\n", "has no value")

    def test_unterminated_quote(self):
        self.assertRefused('a: "oops\n', "unterminated")

    def test_empty_file(self):
        self.assertRefused("\n# nothing\n", "empty")

    def test_message_carries_the_line_number(self):
        with self.assertRaises(YamlSubsetError) as caught:
            loads("a: 1\nb: 2\n\tc: 3\n", origin="fichier.yml")
        self.assertIn("fichier.yml:3:", str(caught.exception))


@unittest.skipIf(pyyaml is None, "PyYAML is not installed")
class AgreesWithRealYaml(unittest.TestCase):
    """Proof that the subset means what YAML means, over the files we actually ship.

    PyYAML resolves an unquoted 2026-09-23 to a date object; we keep dates as text so
    that a date which is not a real date is reported by the schema, against its field,
    rather than by the parser. That is the one known difference, normalised here.
    """

    def test_every_data_file_parses_the_same(self):
        files = sorted(glob.glob(os.path.join(paths.DATA, "**", "*.yml"), recursive=True))
        self.assertGreaterEqual(len(files), 18)
        for path in files:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            self.assertEqual(_as_text(pyyaml.safe_load(text)), loads(text, path), path)


def _as_text(value):
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, dict):
        return dict((key, _as_text(item)) for key, item in value.items())
    if isinstance(value, list):
        return [_as_text(item) for item in value]
    return value
