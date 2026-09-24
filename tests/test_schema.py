"""What the schema must reject, and what it must let through.

A validator that cannot fail is worse than none: it says the data is fine and nobody
looks again. So every rule here is tested by breaking one field of a valid fixture and
checking that the complaint names the file and the field.
"""

from __future__ import annotations

import contextlib
import io
import os
import unittest

from wednesdays import paths, records, validate

from .support import FixtureCase

COMPLETE = "mjc-fixture--accueil-de-loisirs--3-11"
SPARSE = "cirque-fixture--atelier--sans-age"


class TheShippedData(unittest.TestCase):
    """The criteria for slice 1, checked against data/ itself."""

    def setUp(self):
        self.dataset, self.problems = records.read(paths.DATA)

    def test_every_data_file_validates(self):
        self.assertEqual([str(problem) for problem in self.problems], [])

    def test_ten_activities(self):
        self.assertEqual(len(self.dataset.activities), 10)

    def test_every_organiser_named_by_an_activity_has_a_record(self):
        for activity in self.dataset.activities:
            self.assertIn(activity["organiser"], self.dataset.organisers, activity["slug"])

    def test_every_activity_cites_a_source(self):
        for activity in self.dataset.activities:
            self.assertTrue(activity["source_url"].startswith("http"), activity["slug"])

    def test_some_record_has_an_empty_event_log(self):
        logs = [activity["events"] for activity in self.dataset.activities]
        self.assertIn([], logs)


class ValidData(FixtureCase):
    def test_the_fixture_validates(self):
        self.assertEqual(self._problems(), [])

    def test_a_record_with_an_empty_event_log_validates(self):
        self.assertEqual(self.read(self.activity(SPARSE)).count("events: []"), 1)
        self.assertEqual(self._problems(), [])

    def test_absent_optional_fields_are_not_problems(self):
        text = self.read(self.activity(SPARSE))
        for absent in ("ages:", "when:", "price_note:", "phone:"):
            self.assertNotIn(absent, text)
        self.assertEqual(self._problems(), [])

    def _problems(self):
        return [str(problem) for problem in records.read(self.data)[1]]


class BrokenData(FixtureCase):
    def assertRejected(self, slug, field, fragment):
        problems = records.read(self.data)[1]
        naming = [
            problem
            for problem in problems
            if problem.path.endswith("%s.yml" % slug) and problem.field == field
        ]
        self.assertTrue(
            naming, "no problem named %s in %s; got %s" % (field, slug, [str(p) for p in problems])
        )
        self.assertIn(fragment, str(naming[0]))

    def test_a_tag_outside_the_controlled_list(self):
        self.edit(self.activity(COMPLETE), "tags: [accueil_de_loisirs,", "tags: [poney,")
        self.assertRejected(COMPLETE, "tags", "not in data/tags.yml")

    def test_a_date_that_is_not_a_real_date(self):
        self.edit(self.activity(COMPLETE), 'verified_on: "2026-09-21"', 'verified_on: "2026-02-30"')
        self.assertRejected(COMPLETE, "verified_on", "not a real date")

    def test_a_date_that_is_not_a_date_at_all(self):
        self.edit(self.activity(COMPLETE), 'source_last_seen: "2026-09-20"', "source_last_seen: bientot")
        self.assertRejected(COMPLETE, "source_last_seen", "YYYY-MM-DD")

    def test_a_date_that_is_a_real_day_but_not_zero_padded(self):
        self.edit(self.activity(COMPLETE), 'verified_on: "2026-09-21"', 'verified_on: "2026-9-3"')
        self.assertRejected(COMPLETE, "verified_on", "YYYY-MM-DD")

    def test_a_date_that_int_would_read_but_a_reader_would_not(self):
        self.edit(self.activity(COMPLETE), 'verified_on: "2026-09-21"', 'verified_on: "2026-1_0-01"')
        self.assertRejected(COMPLETE, "verified_on", "YYYY-MM-DD")

    def test_an_organiser_with_no_file(self):
        os.remove(os.path.join(self.data, "organisers", "mjc-fixture.yml"))
        self.assertRejected(COMPLETE, "organiser", "no data/organisers/mjc-fixture.yml")

    def test_an_organiser_reference_that_never_existed(self):
        path = self.activity(COMPLETE)
        self.edit(path, "organiser: mjc-fixture", "organiser: mjc-inconnue")
        self.assertRejected(COMPLETE, "organiser", "no data/organisers/mjc-inconnue.yml")

    def test_a_missing_required_field(self):
        self.edit(self.activity(COMPLETE), "status: verified\n", "")
        self.assertRejected(COMPLETE, "status", "required field is missing")

    def test_an_unknown_field(self):
        self.edit(self.activity(COMPLETE), "status: verified", "status: verified\nplaces: 12")
        self.assertRejected(COMPLETE, "places", "unknown field")

    def test_an_age_range_that_is_not_two_whole_years(self):
        self.edit(self.activity(COMPLETE), "ages: [3, 11]", "ages: [3, 11, 14]")
        self.assertRejected(COMPLETE, "ages", "[min, max]")

    def test_an_age_range_the_wrong_way_round(self):
        self.edit(self.activity(COMPLETE), "ages: [3, 11]", "ages: [11, 3]")
        self.assertRejected(COMPLETE, "ages", "minimum age is above the maximum")

    def test_a_moment_outside_the_controlled_list(self):
        self.edit(self.activity(COMPLETE), "when: [matin,", "when: [mercredi_soir,")
        self.assertRejected(COMPLETE, "when", "is not one of")

    def test_two_kind_tags(self):
        self.edit(self.activity(COMPLETE), "tags: [accueil_de_loisirs,", "tags: [accueil_de_loisirs, cirque,")
        self.assertRejected(COMPLETE, "tags", "exactly one 'kind' tag")

    def test_no_kind_tag(self):
        self.edit(self.activity(COMPLETE), "tags: [accueil_de_loisirs, tous_les_mercredis, ecole]", "tags: [ecole]")
        self.assertRejected(COMPLETE, "tags", "exactly one 'kind' tag")

    def test_an_event_missing_its_note(self):
        self.edit(self.activity(COMPLETE), '    note_fr: "Appelé : il reste des places."\n', "")
        self.assertRejected(COMPLETE, "events[1].note_fr", "required field is missing")

    def test_an_event_log_out_of_order(self):
        self.edit(
            self.activity(COMPLETE),
            'events:\n  - date: "2026-09-21"\n    kind: appel\n',
            'events:\n  - date: "2026-09-22"\n    kind: appel\n'
            '    by: bureau\n    note_fr: plus tard\n  - date: "2026-09-21"\n    kind: appel\n',
        )
        self.assertRejected(COMPLETE, "events[2].date", "oldest first")

    def test_an_event_log_out_of_order_only_when_the_dates_are_padded(self):
        """The order rule compares strings, so an unpadded date must not reach it."""
        self.edit(
            self.activity(COMPLETE),
            'events:\n  - date: "2026-09-21"\n    kind: appel\n',
            'events:\n  - date: "2026-10-01"\n    kind: appel\n'
            '    by: bureau\n    note_fr: plus tard\n  - date: "2026-9-3"\n    kind: appel\n',
        )
        self.assertRejected(COMPLETE, "events[2].date", "YYYY-MM-DD")

    def test_a_date_left_unquoted(self):
        """PyYAML hands back a date object; the schema says so and says what to type."""
        self.edit(self.activity(COMPLETE), 'verified_on: "2026-09-21"', "verified_on: 2026-09-21")
        self.assertRejected(COMPLETE, "verified_on", 'write "2026-09-21"')

    def test_a_date_left_unquoted_that_is_not_a_real_day(self):
        """PyYAML builds this one with datetime.date and lets the ValueError out raw."""
        self.edit(self.activity(COMPLETE), 'verified_on: "2026-09-21"', "verified_on: 2026-02-30")
        self.assertRejected(COMPLETE, "(yaml)", "day is out of range")

    def test_a_parse_failure_names_the_line_it_stopped_on(self):
        lines = self.read(self.activity(COMPLETE)).split("\n")
        lines[8] = "\t" + lines[8].lstrip()
        self.write(self.activity(COMPLETE), "\n".join(lines))
        self.assertRejected(COMPLETE, "(yaml line 9)", "cannot start any token")

    def test_a_block_scalar_whose_second_line_is_indented_less_than_its_first(self):
        """The hand-written reader used to slice every line by the first line's indent,
        so a line indented less than that had characters eaten off its front and the
        record shipped shorter than the file. It is refused now, by file and line."""
        self.edit(
            self.activity(COMPLETE),
            'notes_fr: "Une fiche complète, pour vérifier que chaque champ arrive sur la carte."',
            "notes_fr: |\n    Une fiche complète,\n  repliée trop à gauche.",
        )
        self.assertRejected(COMPLETE, "(yaml line 11)", "expected <block end>")
        dataset, _ = records.read(self.data)
        self.assertEqual([activity["slug"] for activity in dataset.activities], [SPARSE])

    def test_a_filename_that_does_not_start_with_its_organiser(self):
        os.rename(self.activity(COMPLETE), self.activity("autre-mjc--accueil--3-11"))
        self.assertRejected("autre-mjc--accueil--3-11", "(filename)", "must be named mjc-fixture--")

    def test_an_activities_directory_with_nothing_in_it(self):
        for name in os.listdir(os.path.join(self.data, "activities")):
            os.remove(os.path.join(self.data, "activities", name))
        problems = [str(problem) for problem in records.read(self.data)[1]]
        self.assertTrue(any("holds no activity files" in problem for problem in problems), problems)


class TheValidatorReportsRatherThanCrashes(FixtureCase):
    """A file of the wrong shape is a problem to print, not an exception to raise.

    The schema says `expected a mapping`; the reading that follows used to hand the same
    document on regardless and die on it, which turned a named problem into a traceback.
    """

    def test_a_tags_file_that_is_not_a_mapping(self):
        self.write(os.path.join(self.data, "tags.yml"), "- kind\n- sport\n")
        self.assertReported("tags.yml: (file): expected a mapping of tag groups")

    def test_an_activity_file_whose_top_level_is_a_sequence(self):
        self.write(self.activity(COMPLETE), "- un\n- deux\n")
        self.assertReported("%s.yml: (file): expected a mapping of fields" % COMPLETE)

    def test_an_activity_file_that_is_prose_rather_than_a_record(self):
        self.write(self.activity(COMPLETE), "just some prose, not a record\n")
        self.assertReported("%s.yml: (file): expected a mapping of fields" % COMPLETE)

    def assertReported(self, fragment):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = validate.main([self.data])
        self.assertEqual(status, 1)
        self.assertIn(fragment, stderr.getvalue())


class Organisers(FixtureCase):
    def test_an_organiser_without_a_public_page(self):
        path = os.path.join(self.data, "organisers", "mjc-fixture.yml")
        self.edit(path, "page: https://example.invalid/mjc\n", "")
        problems = [str(problem) for problem in records.read(self.data)[1]]
        self.assertTrue(
            any("organisers/mjc-fixture.yml: page: required" in problem for problem in problems),
            problems,
        )

    def test_an_organiser_page_that_is_not_a_url(self):
        path = os.path.join(self.data, "organisers", "mjc-fixture.yml")
        self.edit(path, "page: https://example.invalid/mjc", "page: demander a la MJC")
        problems = [str(problem) for problem in records.read(self.data)[1]]
        self.assertTrue(any("page: expected an http(s) URL" in problem for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()
