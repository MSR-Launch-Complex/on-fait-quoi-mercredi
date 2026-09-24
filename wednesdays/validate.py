"""`bin/validate`: read every data file and print every reason it may not ship.

It prints all the problems, not the first: a hand-typed entry usually has more than one,
and three runs to find three mistakes is how people stop running it.
"""

from __future__ import annotations

import sys

from . import paths, records


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    data_dir = argv[0] if argv else paths.DATA
    if len(argv) > 1:
        sys.stderr.write("usage: bin/validate [data-directory]\n")
        return 2

    dataset, problems = records.read(data_dir)
    for problem in problems:
        sys.stderr.write("%s\n" % problem)
    if problems:
        sys.stderr.write(
            "%d problem%s; the record shape is documented in docs/schema.md\n"
            % (len(problems), "" if len(problems) == 1 else "s")
        )
        return 1
    sys.stdout.write(
        "%d activities, %d organisers: all valid\n"
        % (len(dataset.activities), len(dataset.organisers))
    )
    return 0
