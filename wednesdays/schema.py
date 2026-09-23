"""The record shape, and the rules that decide whether a data file may ship.

Every rule here answers the same question: would a parent be misled? A guessed age
range, a date that is not a real date, or an organiser nobody can look up are all the
same defect wearing different clothes, so they all stop the build.

Absence is a first-class answer. A field the source does not state is left out; it is
never filled in with something plausible. That is why so few fields are required.
"""

from __future__ import annotations

import datetime
import re

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:--[a-z0-9]+(?:-[a-z0-9]+)*)*$")
# Tags are snake_case (apres_midi, arts_plastiques); file slugs are hyphenated.
TAG = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
URL = re.compile(r"^https?://\S+$")
# Dates are stored zero-padded because the event log is ordered by comparing them as
# strings; int() would happily read "2026-9-3" and that string sorts before "2026-10-01".
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ACTIVITY_REQUIRED = (
    "title_fr",
    "organiser",
    "commune",
    "tags",
    "source_url",
    "source_last_seen",
    "verified_on",
    "status",
    "events",
)
ACTIVITY_OPTIONAL = (
    "ages",
    "when",
    "price_note",
    "address",
    "phone",
    "email",
    "booking_url",
    "notes_fr",
)

ORGANISER_REQUIRED = ("name", "commune", "page")
ORGANISER_OPTIONAL = ("address", "phone", "email")

EVENT_REQUIRED = ("date", "kind", "by", "note_fr")
EVENT_OPTIONAL = ("source_url",)

WHEN = ("matin", "apres_midi", "journee")
STATUS = ("verified", "unverified")
EVENT_KINDS = ("appel", "email", "visite", "source", "correction", "crawl")

# Wide enough that a plausible entry is never blocked, narrow enough that a typo is.
AGE_FLOOR, AGE_CEILING = 0, 18


class Problem(object):
    """One reason a data file may not ship, named by file and field."""

    def __init__(self, path, field, message):
        self.path = path
        self.field = field
        self.message = message

    def __str__(self):
        return "%s: %s: %s" % (self.path, self.field, self.message)


def check_tags_file(path, doc):
    """`data/tags.yml` is the controlled list: groups of tags, one group per kind."""
    problems = []
    if not isinstance(doc, dict):
        return [Problem(path, "(file)", "expected a mapping of tag groups")]
    if "kind" not in doc:
        problems.append(Problem(path, "kind", "the controlled list has no 'kind' group"))
    for group, tags in doc.items():
        if not isinstance(tags, list) or not tags:
            problems.append(Problem(path, group, "expected a non-empty list of tags"))
            continue
        for tag in tags:
            if not isinstance(tag, str) or not TAG.match(tag):
                problems.append(
                    Problem(path, group,
                            "%r is not a tag name (lowercase, underscores)" % (tag,))
                )
    return problems


def check_organiser(path, slug, doc):
    problems = []
    if not isinstance(doc, dict):
        return [Problem(path, "(file)", "expected a mapping of fields")]
    problems += _slug_of_filename(path, slug)
    problems += _fields(path, doc, ORGANISER_REQUIRED, ORGANISER_OPTIONAL)
    for field in ("name", "commune"):
        problems += _nonempty_text(path, doc, field)
    problems += _url(path, doc, "page")
    for field in ("address", "phone", "email"):
        if field in doc:
            problems += _nonempty_text(path, doc, field)
    return problems


def check_activity(path, slug, doc, tags, organisers):
    """`tags` is the controlled list; `organisers` the slugs found in data/organisers/."""
    problems = []
    if not isinstance(doc, dict):
        return [Problem(path, "(file)", "expected a mapping of fields")]
    problems += _slug_of_filename(path, slug)
    problems += _fields(path, doc, ACTIVITY_REQUIRED, ACTIVITY_OPTIONAL)
    for field in ("title_fr", "commune"):
        problems += _nonempty_text(path, doc, field)
    problems += _organiser_reference(path, slug, doc, organisers)
    problems += _tags(path, doc, tags)
    problems += _ages(path, doc)
    problems += _when(path, doc)
    problems += _url(path, doc, "source_url")
    if "booking_url" in doc:
        problems += _url(path, doc, "booking_url")
    for field in ("source_last_seen", "verified_on"):
        problems += _date(path, doc, field, doc.get(field))
    problems += _one_of(path, doc, "status", STATUS)
    for field in ("price_note", "address", "phone", "email", "notes_fr"):
        if field in doc:
            problems += _nonempty_text(path, doc, field)
    problems += _events(path, doc)
    return problems


def _fields(path, doc, required, optional):
    problems = []
    for field in required:
        if field not in doc:
            problems.append(Problem(path, field, "required field is missing"))
    known = set(required) | set(optional)
    for field in doc:
        if field not in known:
            problems.append(
                Problem(path, field, "unknown field; the shape is documented in docs/schema.md")
            )
    return problems


def _slug_of_filename(path, slug):
    if not SLUG.match(slug):
        return [
            Problem(path, "(filename)", "%r is not a slug (lowercase, digits, hyphens)" % slug)
        ]
    return []


def _nonempty_text(path, doc, field):
    if field not in doc:
        return []
    value = doc[field]
    if not isinstance(value, str) or not value.strip():
        return [Problem(path, field, "expected some text, found %r" % (value,))]
    return []


def _url(path, doc, field):
    if field not in doc:
        return []
    value = doc[field]
    if not isinstance(value, str) or not URL.match(value):
        return [Problem(path, field, "expected an http(s) URL, found %r" % (value,))]
    return []


def _one_of(path, doc, field, allowed):
    if field not in doc:
        return []
    if doc[field] not in allowed:
        return [
            Problem(path, field, "%r is not one of %s" % (doc[field], ", ".join(allowed)))
        ]
    return []


def _organiser_reference(path, slug, doc, organisers):
    if "organiser" not in doc:
        return []
    reference = doc["organiser"]
    if not isinstance(reference, str) or not SLUG.match(reference or ""):
        return [Problem(path, "organiser", "expected an organiser slug, found %r" % (reference,))]
    problems = []
    if reference not in organisers:
        problems.append(
            Problem(path, "organiser", "no data/organisers/%s.yml for %r" % (reference, reference))
        )
    # The slug is the duplicate-detection backstop (design §6), so it has to start with
    # the organiser it belongs to or two organisers can collide on one activity name.
    if not slug.startswith(reference + "--"):
        problems.append(
            Problem(path, "(filename)", "a file for %r must be named %s--<activity>--<ages>.yml"
                    % (reference, reference))
        )
    return problems


def _tags(path, doc, tags):
    if "tags" not in doc:
        return []
    value = doc["tags"]
    if not isinstance(value, list) or not value:
        return [Problem(path, "tags", "expected a non-empty list of tags")]
    problems = []
    known = set()
    for group in tags.values():
        known |= set(group)
    for tag in value:
        if tag not in known:
            problems.append(Problem(path, "tags", "%r is not in data/tags.yml" % (tag,)))
    kinds = [tag for tag in value if tag in set(tags.get("kind", ()))]
    if len(kinds) != 1:
        problems.append(
            Problem(path, "tags", "expected exactly one 'kind' tag, found %d" % len(kinds))
        )
    return problems


def _ages(path, doc):
    if "ages" not in doc:
        return []
    value = doc["ages"]
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(age, int) and not isinstance(age, bool) for age in value)
    ):
        return [Problem(path, "ages", "expected [min, max] as whole years, found %r" % (value,))]
    low, high = value
    if low > high:
        return [Problem(path, "ages", "the minimum age is above the maximum: %r" % (value,))]
    if low < AGE_FLOOR or high > AGE_CEILING:
        return [
            Problem(path, "ages", "outside %d-%d years: %r" % (AGE_FLOOR, AGE_CEILING, value))
        ]
    return []


def _when(path, doc):
    if "when" not in doc:
        return []
    value = doc["when"]
    if not isinstance(value, list) or not value:
        return [
            Problem(path, "when", "expected a non-empty list of %s, or no field at all "
                                  "when the source does not say" % ", ".join(WHEN))
        ]
    problems = []
    for moment in value:
        if moment not in WHEN:
            problems.append(
                Problem(path, "when", "%r is not one of %s" % (moment, ", ".join(WHEN)))
            )
    if len(set(value)) != len(value):
        problems.append(Problem(path, "when", "the same moment is listed twice: %r" % (value,)))
    return problems


def _date(path, doc, field, value):
    if field not in doc:
        return []
    if not isinstance(value, str) or not DATE.match(value):
        return [Problem(path, field, "expected a date as YYYY-MM-DD, found %r" % (value,))]
    year, month, day = (int(part) for part in value.split("-"))
    try:
        datetime.date(year, month, day)
    except ValueError:
        return [Problem(path, field, "%r is not a real date (YYYY-MM-DD)" % (value,))]
    return []


def _events(path, doc):
    """The log is appended to and never rewritten, so it is stored oldest first."""
    if "events" not in doc:
        return []
    value = doc["events"]
    if not isinstance(value, list):
        return [Problem(path, "events", "expected a list, or [] when nothing has happened yet")]
    problems, previous = [], None
    for position, event in enumerate(value, start=1):
        where = "events[%d]" % position
        if not isinstance(event, dict):
            problems.append(Problem(path, where, "expected a mapping of event fields"))
            continue
        found = _fields(path, event, EVENT_REQUIRED, EVENT_OPTIONAL)
        found += _date(path, event, "date", event.get("date"))
        found += _one_of(path, event, "kind", EVENT_KINDS)
        for field in ("by", "note_fr"):
            found += _nonempty_text(path, event, field)
        if "source_url" in event:
            found += _url(path, event, "source_url")
        date = event.get("date")
        if isinstance(date, str) and previous and date < previous:
            found.append(
                Problem(path, "date", "the event log runs oldest first; %s follows %s"
                        % (date, previous))
            )
        if isinstance(date, str):
            previous = date
        for problem in found:
            problem.field = "%s.%s" % (where, problem.field)
        problems += found
    return problems
