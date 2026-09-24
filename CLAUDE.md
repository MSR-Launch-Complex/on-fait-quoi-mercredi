# Arriving cold

This repository builds a French static site listing Wednesday activities for 3-11 year
olds around Annecy. It has no server and no database: the data is YAML files under
`data/`, a merge to `main` is a publish, and the site is one page built from that data.

Read in this order:

1. **[docs/design/DESIGN.md](docs/design/DESIGN.md)** - what the whole thing is. §4 is
   the page, §6 is how it works, §7 is the order of work in ten slices.
2. **[docs/schema.md](docs/schema.md)** - the record shape, and the one rule everything
   else follows: a field the source does not state is left out, never guessed.
3. **[README.md](README.md)** - build and test commands, and the open pre-launch items.

## The commands

```sh
make build     # data/ + content/ -> site/index.html. Offline; needs PyYAML installed
make test      # schema validation over data/, then the schema and builder tests
make serve     # build, then serve site/ on localhost:8000
```

`make test` is `.bureau.yml`'s `test_command`. There is no linter and no type checker.

## Where things are

| Path | What it is |
| :--- | :--- |
| `data/activities/<organiser>--<activity>--<ages>.yml` | one activity |
| `data/organisers/<slug>.yml` | one organiser; activities reference it by slug |
| `data/tags.yml` | the controlled tag list; `kind` also chooses the card icon |
| `content/about_fr.md` | the À propos text, used in the footer and the page description |
| `wednesdays/schema.py` | every rule that can stop a data file shipping |
| `wednesdays/records.py` | reads `data/` into a dataset, or returns every problem |
| `wednesdays/render.py`, `build.py` | the page of design §4, and writing `site/` |
| `wednesdays/french.py` | every French string that is not in `data/` or `content/` |

## Conventions worth knowing before you change anything

- **One dependency, PyYAML.** Declared in `pyproject.toml` (`pip install -e .`) and used
  through `yaml.safe_load` only. Prefer the standard library for anything else; what that
  rule does not mean is reimplementing a standard format, which is why the hand-written
  YAML subset reader that used to live here was pruned (Bobby, 2026-09-24).
- **Dates in `data/` are quoted.** `verified_on: "2026-09-23"`. Unquoted, YAML hands back
  a date object, and the event log is ordered by comparing these as text; the schema
  refuses a date that arrives unquoted and says what to type.
- **Offline is still the rule.** Past the install, `make build` reaches nothing, and the
  page it writes makes no external request.
- **Absence is a value.** No field is invented to fill a card. If a source does not give
  an age range, a price, or whether it is morning or afternoon, the field is absent and
  the card says "non précisé par la source". Do not add defaults.
- **The page is a picture of the data.** Nothing about an activity is written into the
  markup. Deleting a file in `data/activities/` and rebuilding must remove it from the
  page; there is a test that says so.
- **Stay inside the slice.** The design's later slices own the filters and views (6), the
  correction form (7), the event log rendering (8) and the map (10). Half-building one of
  them here makes the review harder, not easier.
- French copy for the site lives in `content/` (editable prose) or `wednesdays/french.py`
  (the template's own words). Never in the templates by hand.
