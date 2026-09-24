# on-fait-quoi-mercredi

**On fait quoi mercredi ?** There is no school on Wednesday in France, so every family
with young children has to fill the day, and the information about what is on offer
around Annecy is scattered across a dozen websites, a season brochure in PDF and a
municipal enrolment portal. This is a French static site that gathers it in one place:
who runs it, for which ages, Wednesday morning or afternoon or all day, roughly what it
costs, and a link to the organiser.

Ages 3-11, the Annecy agglomeration, Wednesdays only. The design, as accepted:
[docs/design/DESIGN.md](docs/design/DESIGN.md). The record shape:
[docs/schema.md](docs/schema.md).

## Where it is up to

This is slice 1 of ten: the shape, a working site, and the tests. Ten activities are
typed by hand from the sources listed in the intake inventory; nothing is crawled yet.
The page is a list of cards and nothing else - the filters, the Wednesday grid, the map,
the detail sheet and the correction form belong to later slices.

## Build it

```sh
pip install -e .   # once: Python 3.9 or newer, and PyYAML, which is the one dependency
make build         # data/ + content/ -> site/index.html
make serve         # the same, then http://localhost:8000
```

PyYAML reads `data/`; it is declared in `pyproject.toml` and is the whole install. The
build itself asks nothing of the network, and neither does the page it writes.

## Test it

```sh
make test      # schema validation over data/, then the schema and builder tests
```

`make test` is the single entry point and what `.bureau.yml` declares as `test_command`.
It fails if any data file breaks the schema, and it names the file and the field.

## Add or change an activity

Write or edit a file in `data/activities/`, following
[docs/schema.md](docs/schema.md), and run `make test`. If the activity's organiser is new,
add `data/organisers/<slug>.yml` too. Enter only what the cited page actually states: a
field the source does not give is left out, and the card says so.

## Publish it

GitHub Actions builds and deploys to Pages on every push to `main`, so a merge is a
publish: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) builds the site
and [`.github/workflows/test.yml`](.github/workflows/test.yml) runs `make test` on every
pull request. Once, before the first deploy: **Settings → Pages → Build and deployment →
Source: GitHub Actions**.

## Before this is shared beyond people you know

- [ ] **Mentions légales.** What a personal, non-commercial French site is required to
      carry has not been established, and nothing has been written for it. Confirm what
      is needed and put it in the footer before sharing the site outside the household
      (design §6, §8). Nothing on the site claims it today.
- [ ] Switch GitHub Pages to the GitHub Actions source, so that merges publish. The
      workflows are in `.github/workflows/`; the setting is the half that only a person
      with repository access can do.

## Layout

| Path | What it is |
| :--- | :--- |
| `data/activities/`, `data/organisers/`, `data/tags.yml` | the data; git is the database |
| `content/about_fr.md` | the À propos text: the footer and the page description, one copy |
| `assets/` | the stylesheet and one card icon per kind, both inlined into the page |
| `wednesdays/` | the reader, the schema, the renderer, the builder |
| `pyproject.toml` | the one dependency, PyYAML |
| `bin/build`, `bin/validate` | the two entry points the Makefile calls |
| `tests/` | run by `make test` |
| `docs/` | the design (`docs/design/DESIGN.md`) and the record shape (`docs/schema.md`) |
