"""The builder: fixture data in, the page of the design's §4 out.

The load-bearing test is `test_deleting_an_activity_removes_it_from_the_page`. If it
ever fails, something has been hand-written into the markup, and the site has stopped
being a picture of the data.
"""

from __future__ import annotations

import os
import re
import unittest

import yaml

from wednesdays import build, paths, records

from .support import FixtureCase

COMPLETE = "mjc-fixture--accueil-de-loisirs--3-11"
SPARSE = "cirque-fixture--atelier--sans-age"


def _read(path):
    """A data file as the tests read it: straight from disk, not through the builder."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class BuiltPage(FixtureCase):
    def setUp(self):
        super(BuiltPage, self).setUp()
        self.markup = self.rebuild()

    def rebuild(self):
        build.build(
            data_dir=self.data,
            site_dir=self.site,
            about_path=self.about,
            icons_dir=paths.ICONS,
            stylesheet_path=paths.STYLESHEET,
        )
        return self.read(os.path.join(self.site, "index.html"))

    def test_it_writes_one_page(self):
        self.assertEqual(os.listdir(self.site), ["index.html"])

    def test_the_page_is_french_and_sized_for_a_phone(self):
        self.assertIn('<html lang="fr">', self.markup)
        self.assertIn('name="viewport" content="width=device-width, initial-scale=1"', self.markup)

    def test_the_count_band_counts_the_activities(self):
        self.assertIn('<p class="count">2 activités</p>', self.markup)

    def test_a_card_carries_every_field_the_design_names(self):
        card = self._card(COMPLETE)
        record = _read(self.activity(COMPLETE))
        self.assertIn('aria-label="Accueil de loisirs"', card)  # the kind icon
        self.assertIn("<svg", card)
        self.assertIn(record["title_fr"], card)
        self.assertIn("MJC Fixture", card)  # the organiser, by name
        self.assertIn(record["commune"], card)
        self.assertIn("de 3 à 11 ans", card)
        self.assertIn("matin, après-midi ou journée", card)
        self.assertIn("De 6 € à 21 € selon le quotient familial.", card)
        self.assertIn("vérifié le 21/09/2026", card)
        self.assertIn(record["source_url"], card)

    def test_the_organiser_and_the_commune_read_apart_without_the_stylesheet(self):
        """The separator is in the markup, so stripping the styles does not join them."""
        who = self._card(COMPLETE).split('<p class="card-who">')[1].split("</p>")[0]
        self.assertEqual(re.sub(r"<[^>]+>", "", who), "MJC Fixture · Annecy")

    def test_a_card_says_when_the_source_did_not_say(self):
        card = self._card(SPARSE)
        self.assertIn("non précisé par la source", card)
        self.assertIn("horaire non précisé par la source", card)
        self.assertIn("non indiqué par la source", card)
        self.assertEqual(card.count("fact-unknown"), 3)

    def test_the_about_text_is_in_the_footer_and_in_the_description(self):
        about = self.read(self.about).strip()
        self.assertIn("<footer", self.markup)
        self.assertIn(about, self.markup.split("<footer")[1])
        self.assertIn('<meta name="description" content="%s">' % about, self.markup)

    def test_editing_the_about_text_changes_both_of_them(self):
        self.write(self.about, "Un autre texte À propos.\n")
        markup = self.rebuild()
        self.assertIn('<meta name="description" content="Un autre texte À propos.">', markup)
        self.assertIn("Un autre texte À propos.", markup.split("<footer")[1])
        self.assertNotIn("fixture", markup.split("<footer")[1])

    def test_the_header_carries_one_sentence_of_it(self):
        header = self.markup.split("</header>")[0]
        self.assertIn("Le texte À propos de la fixture, en un seul paragraphe.", header)

    def test_deleting_an_activity_removes_it_from_the_page(self):
        os.remove(self.activity(SPARSE))
        markup = self.rebuild()
        self.assertNotIn("Atelier cirque", markup)
        self.assertIn("Accueil de loisirs du mercredi", markup)
        self.assertIn('<p class="count">1 activité</p>', markup)

    def test_the_page_asks_nothing_of_anywhere_else(self):
        """No external request: the icons and the stylesheet are inlined (design §4)."""
        self.assertNotIn("<script", self.markup)
        self.assertNotIn("<link ", self.markup)
        self.assertNotIn("<img", self.markup)
        self.assertNotIn("src=", self.markup)
        self.assertNotIn("@import", self.markup)
        self.assertNotIn("url(", self.markup)
        for href in re.findall(r'href="([^"]+)"', self.markup):
            self.assertIn(href, self._cited_urls(), "%s is linked but not cited by any record" % href)

    def _card(self, slug):
        title = _read(self.activity(slug))["title_fr"]
        cards = self.markup.split('<li class="card">')
        matching = [card for card in cards if ">%s</h2>" % title in card]
        self.assertEqual(len(matching), 1, "expected one card for %s" % slug)
        return matching[0]

    def _cited_urls(self):
        dataset = records.load(self.data)
        return set(activity["source_url"] for activity in dataset.activities)


class RefusesToBuild(FixtureCase):
    def test_it_will_not_build_data_that_does_not_validate(self):
        self.edit(self.activity(COMPLETE), 'verified_on: "2026-09-21"', "verified_on: hier")
        with self.assertRaises(records.DataError) as caught:
            self._build()
        self.assertIn("verified_on", str(caught.exception.problems[0]))
        self.assertFalse(os.path.exists(self.site), "a failed build left a site behind")

    def test_it_will_not_build_without_the_about_text(self):
        os.remove(self.about)
        with self.assertRaises(Exception) as caught:
            self._build()
        self.assertIn("about_fr.md", str(caught.exception))

    def test_it_names_the_kind_whose_icon_is_missing(self):
        with self.assertRaises(build.BuildError) as caught:
            build.load_icons(paths.ICONS, ["accueil_de_loisirs", "poney"])
        self.assertIn("poney.svg", str(caught.exception))

    def _build(self):
        return build.build(
            data_dir=self.data,
            site_dir=self.site,
            about_path=self.about,
            icons_dir=paths.ICONS,
            stylesheet_path=paths.STYLESHEET,
        )


class ShippedAssets(unittest.TestCase):
    def test_every_kind_in_the_controlled_list_has_an_icon(self):
        tags = _read(paths.TAGS)
        icons = build.load_icons(paths.ICONS, tags["kind"])
        self.assertEqual(sorted(icons), sorted(tags["kind"]))
        for kind, svg in icons.items():
            self.assertTrue(svg.strip().startswith("<svg"), kind)
            self.assertNotIn("http://", svg.replace("http://www.w3.org/2000/svg", ""))


if __name__ == "__main__":
    unittest.main()
