"""`make build`: data/ and content/ in, site/ out. Nothing else, and nothing fetched.

The build refuses to run on data that does not validate. A site built from half-valid
data looks perfectly fine and tells parents things that are not true, which is the one
failure this project cannot afford.
"""

from __future__ import annotations

import os
import shutil
import sys

from . import about as about_text
from . import paths, records, render


class BuildError(Exception):
    """Something the build needs is missing or wrong. Never a partial site."""


def build(data_dir=paths.DATA, site_dir=paths.SITE, about_path=paths.ABOUT,
          icons_dir=paths.ICONS, stylesheet_path=paths.STYLESHEET):
    """Write the site and return the paths written."""
    dataset = records.load(data_dir)
    about = about_text.load(about_path)
    icons = load_icons(icons_dir, dataset.tags.get("kind", ()))
    stylesheet = _read(stylesheet_path)

    markup = render.page(dataset, about, icons, stylesheet)

    # Rebuilt from scratch: an activity file that was deleted must leave no page behind.
    if os.path.isdir(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir)
    index = os.path.join(site_dir, "index.html")
    with open(index, "w", encoding="utf-8") as handle:
        handle.write(markup)
    return [index]


def load_icons(icons_dir, kinds):
    """One icon per kind in the controlled list, shipped with the site (design §4)."""
    icons = {}
    for kind in kinds:
        path = os.path.join(icons_dir, "%s.svg" % kind)
        if not os.path.isfile(path):
            raise BuildError(
                "%s is missing: every kind in data/tags.yml needs a card icon" % path
            )
        icons[kind] = _read(path)
    return icons


def _read(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as error:
        raise BuildError("%s: %s" % (path, error.strerror or error))


def main(argv=None):
    """The `bin/build` entry point. Returns a shell exit status."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        sys.stderr.write("usage: bin/build\n")
        return 2
    try:
        written = build()
    except records.DataError as error:
        sys.stderr.write("the data does not validate, so nothing was built:\n")
        for problem in error.problems:
            sys.stderr.write("  %s\n" % problem)
        return 1
    except (BuildError, about_text.AboutMissing) as error:
        sys.stderr.write("build failed: %s\n" % error)
        return 1
    for path in written:
        sys.stdout.write("wrote %s\n" % os.path.relpath(path, paths.ROOT))
    return 0
