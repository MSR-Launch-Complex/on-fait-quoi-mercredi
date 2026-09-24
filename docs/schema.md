# The record shape

Two kinds of file, both YAML, both under `data/`. `make test` checks every one of them
against the rules below and names the file and the field when something is wrong.

The rule that matters more than any other: **a field the source does not state is left
out.** Not guessed, not rounded, not "probably the afternoon". The site says "non
précisé par la source" on the card, which is true and useful; a plausible invention is
neither.

## An activity — `data/activities/<slug>.yml`

The slug is `<organiser>--<activity>--<ages>`, and it has to begin with the organiser's
own slug: it is the backstop against the same activity being entered twice (design §6).

```yaml
title_fr: Les mercredis du SOU          # what the organiser calls it
organiser: sou-des-ecoles-laiques-annecy  # a file in data/organisers/
commune: Annecy                          # always shown, including for the edges
ages: [3, 12]                            # whole years, min then max. Absent if unstated
when: [matin, apres_midi, journee]       # any of the three. Absent if unstated
tags: [accueil_de_loisirs, tous_les_mercredis, ecole]  # from data/tags.yml
price_note: "Selon le quotient familial CAF : ..."     # free text; prices are rarely a number
address: École de Novel, Annecy           # where the child goes, not the office
phone: 04 50 27 65 09                     # only if this activity has its own
email: sou.annecy@gmail.com               # same
booking_url: https://...                  # the enrolment page, if the source gives one
notes_fr: "..."                           # the description, for the detail sheet (slice 6)
source_url: http://soudesecoles-annecy.fr/les-mercredis-du-sou/   # what we read
source_last_seen: "2026-09-23"            # when we last read it
verified_on: "2026-09-23"                 # what the card shows
status: verified                          # verified | unverified
events: []                                # the log, below. Empty is a valid answer
```

Required: `title_fr`, `organiser`, `commune`, `tags`, `source_url`, `source_last_seen`,
`verified_on`, `status`, `events`. Everything else is optional and means "the source did
not say" when it is absent. Any other field name is rejected, so a typo cannot become a
silently ignored fact.

`tags` must carry **exactly one** `kind` tag: it chooses the card icon, and every kind in
`data/tags.yml` has one in `assets/icons/`.

## The event log

Appended to, never rewritten, and stored oldest first. This is where anything we learn
that the source does not say goes - a phone call, a correction, what the crawler did.

```yaml
events:
  - date: "2026-09-23"
    kind: source          # appel | email | visite | source | correction | crawl
    by: bureau            # first names only, never anybody else's details
    note_fr: "La page indique : complet pour la saison 2026-2027."
    source_url: https://... # optional
```

## An organiser — `data/organisers/<slug>.yml`

```yaml
name: Sou des Écoles Laïques d'Annecy
commune: Annecy
page: http://soudesecoles-annecy.fr/les-mercredis-du-sou/
address: 2 rue des Aravis, 74000 Annecy   # optional
phone: 04 50 27 65 09                     # optional
email: sou.annecy@gmail.com               # optional
```

Required: `name`, `commune`, `page`. Contact details are published only as the structure
publishes them on its own page, and a private individual's number is never published -
if a page gives a staff member's mobile, it does not go in (design §4).

## The controlled list — `data/tags.yml`

Groups of tags: `kind` (what it is, and the card icon), `rhythm` (how often), `setting`
(where). A tag outside this file is rejected, which is what stops the extractor in slice
3 inventing vocabulary one page at a time.

## What the YAML may look like

The files are read with PyYAML's `yaml.safe_load` - whole YAML, so anything valid parses
and a syntax error is reported against the file and the line it stopped on. Two habits
the data keeps anyway:

- **Quote every date**: `verified_on: "2026-09-23"`. Unquoted, YAML 1.1 resolves it to a
  date object and stops recording which text was typed; the event log is ordered by
  comparing these as text. A date that arrives unquoted is refused, with the quoted form
  to type in the message.
- **Quote a number with a leading zero**: `phone: "0450276509"`, which YAML 1.1 would
  otherwise be entitled to read as octal. Written the French way, in pairs
  (`04 50 27 65 09`), it is already text.

## Known gaps against the design

- The design's `when: date` case, and §4's "Ponctuel" strip of dated stages and
  spectacles, are not implemented: none of the ten records is a dated one-off, and
  building a strip with nothing in it would be guesswork about a shape we have not had to
  render yet. The schema rejects `date` as a moment until then.
- `lat`/`lon` on the organiser record belong to slice 10 (the map) and are not accepted
  yet, so nobody types coordinates that nothing reads.
