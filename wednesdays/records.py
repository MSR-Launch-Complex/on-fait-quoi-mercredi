"""Reading data/ into memory, and refusing to when it does not hold up.

Nothing else in the project reads a data file. The builder asks for a dataset and gets
either a whole valid one or a list of problems - there is no half-loaded state, because
a site built from half the data looks fine and lies.
"""

from __future__ import annotations

import os
import unicodedata

import yaml

from . import paths, schema


class _Loader(yaml.SafeLoader):
    """`yaml.safe_load` - still safe, nothing here widens what it will construct - minus
    one silence: PyYAML lets a key be given twice and keeps the last value. A record with
    two verified_on lines is a person disagreeing with themselves, and picking one of the
    two quietly is how the wrong date ships. The reader this replaced said so by name.
    """

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    "while reading a mapping", node.start_mark,
                    "the key %r is given twice" % (key,), key_node.start_mark
                )
            seen.add(key)
        return super(_Loader, self).construct_mapping(node, deep=deep)


class DataError(Exception):
    """The data does not validate. `problems` holds every reason, not just the first."""

    def __init__(self, problems):
        self.problems = problems
        super(DataError, self).__init__(
            "%d problem%s in the data" % (len(problems), "" if len(problems) == 1 else "s")
        )


class Dataset(object):
    def __init__(self, tags, organisers, activities):
        self.tags = tags
        self.organisers = organisers
        self.activities = activities

    def organiser_of(self, activity):
        return self.organisers[activity["organiser"]]


def load(data_dir=paths.DATA):
    """Return the whole dataset, or raise DataError listing everything wrong with it."""
    dataset, problems = read(data_dir)
    if problems:
        raise DataError(problems)
    return dataset


def read(data_dir=paths.DATA):
    """Return (dataset, problems). The dataset is usable only when problems is empty."""
    problems = []

    tags_path = os.path.join(data_dir, "tags.yml")
    tags, failure = _read_file(tags_path)
    if failure:
        return None, [failure]
    problems += schema.check_tags_file(_relative(tags_path), tags)
    if not isinstance(tags, dict):
        # The schema has just said this is not a mapping. Everything below reads it as
        # one, and a crash here would bury the problem it was about to print.
        return None, problems

    organisers = {}
    for path, slug in _yaml_files(os.path.join(data_dir, "organisers")):
        doc, failure = _read_file(path)
        if failure:
            problems.append(failure)
            continue
        problems += schema.check_organiser(_relative(path), slug, doc)
        if not isinstance(doc, dict):
            continue
        organisers[slug] = doc

    activities = []
    for path, slug in _yaml_files(os.path.join(data_dir, "activities")):
        doc, failure = _read_file(path)
        if failure:
            problems.append(failure)
            continue
        problems += schema.check_activity(_relative(path), slug, doc, tags, organisers)
        if not isinstance(doc, dict):
            continue
        doc["slug"] = slug
        activities.append(doc)

    if not activities:
        problems.append(
            schema.Problem(_relative(os.path.join(data_dir, "activities")), "(directory)",
                           "holds no activity files")
        )
    activities.sort(key=_reading_order)
    return Dataset(tags, organisers, activities), problems


def _yaml_files(directory):
    if not os.path.isdir(directory):
        return []
    found = []
    for name in sorted(os.listdir(directory)):
        if name.endswith(".yml"):
            found.append((os.path.join(directory, name), name[: -len(".yml")]))
    return found


def _read_file(path):
    """One file read, or the problem that stopped it - never a traceback."""
    try:
        with open(path, encoding="utf-8") as handle:
            return yaml.load(handle, _Loader), None
    except yaml.YAMLError as error:
        return None, schema.Problem(_relative(path), _yaml_field(error), _yaml_message(error))
    except ValueError as error:
        # PyYAML resolves an unquoted 2026-02-30 by calling datetime.date and lets the
        # ValueError out raw. Without this the validator dies on a data file instead of
        # naming it; the schema's own date rules only see values that parsed.
        return None, schema.Problem(_relative(path), "(yaml)", str(error))
    except OSError as error:
        return None, schema.Problem(_relative(path), "(file)", error.strerror or str(error))


def _yaml_field(error):
    """PyYAML knows which line it stopped on; a problem naming only the file wastes it."""
    mark = getattr(error, "problem_mark", None)
    if mark is None:
        return "(yaml)"
    return "(yaml line %d)" % (mark.line + 1)


def _yaml_message(error):
    problem = getattr(error, "problem", None)
    if problem is None:
        return str(error)
    context = getattr(error, "context", None)
    if context is None:
        return problem
    return "%s: %s" % (context, problem)


def _reading_order(activity):
    """Commune, then title, ignoring accents and case - the order a human would scan."""
    return (_foldable(activity.get("commune", "")), _foldable(activity.get("title_fr", "")))


def _foldable(text):
    stripped = unicodedata.normalize("NFKD", text if isinstance(text, str) else "")
    return "".join(char for char in stripped if not unicodedata.combining(char)).casefold()


def _relative(path):
    """Paths in messages are relative to the repository, so they are clickable."""
    try:
        return os.path.relpath(path, paths.ROOT)
    except ValueError:
        return path
