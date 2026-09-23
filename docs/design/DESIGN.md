<!-- Planned with the Bureau's Navigator (E30). The living copy is the Google Doc:
     https://docs.google.com/document/d/104vcV_vHrxbj13zQUy3KmGxXgPZvRQTrLMiv57fcO0E/edit?usp=drivesdk
     This file is the accepted revision; comment there, not here. -->

# Wednesdays in Annecy

- Type: application  
- Status: exploring  
- Created: 2026-09-23  
- Last updated: 2026-09-23 (revision 4\)  
- Source: `intake.md` (dictated 2026-09-22, Q\&A 2026-09-22/23), comments on drafts 1–4

**What changed in revision 4\.**

| Change | Where |
| :---- | :---- |
| The personal-data redaction pass is dropped from v1: a form response goes into the issue and the drafted PR as typed, and your merge is the gate | §5, §6, §7 slice 7, §8 |
| The rule survives as wording — one line on the form itself and in the contributing notes — rather than as machinery | §6, slice 7 |
| One question back: an issue is opened automatically and is public before you read it | §9 |

Nothing else moved. §4's rule on organiser contact details is unchanged — that is the published-on-the-internet case, and it stands.

## 1\. Name

**Decided: `on-fait-quoi-mercredi`.** It is the question a parent asks when working out the year. Works as a title on the page and as a slug.

## 2\. What it is

There is no school on Wednesday, so every family with young children has to fill the day. The information about what is on offer — the municipal centres de loisirs, the MJCs, the circus school, the associations — exists, but it is spread across a dozen websites, a season brochure in PDF, and a municipal enrolment portal with its own calendar. This is a French website that gathers all of it in one place: who runs it, for which ages, Wednesday morning or afternoon or all day, roughly what it costs, and a link to the organiser. A robot reads the same public pages every day and proposes what it finds; a person checks each proposal before it appears; anyone who spots a mistake fills in a short form.

Translated into French, that paragraph is also the site's *À propos* text and what shows when the link is pasted into a WhatsApp group.

## 3\. Who it is for

| Who | What they do with it |
| :---- | :---- |
| Parents of 3–11 year-olds in the Annecy agglomeration | Open it on a phone, filter by age and commune, read one entry properly, phone or click through to enrol. They do not create an account. |
| Bobby, as the editor | Reviews one pull request per entry on GitHub and merges it. This is the only human gate in v1. |
| Organisers (MJC, associations, municipal services) | Find themselves listed, and use the form to correct a time, a price, or an age range — or to add something we never found. |

Scope of the first release: Annecy agglomeration (including near edges such as Groisy, with the commune always shown), ages 3–11, Wednesdays only, site in French. School holidays and stages during holidays are out of scope for v1.

**It is a directory, not an agenda.** Most Wednesday places are enrolled annually, around June, for the whole year — not booked week by week. So the site lists recurring Wednesday options as standing facts ("every school Wednesday, morning or full day"), and dated one-offs (stages, spectacles) are marked as dated. A calendar-shaped view is welcome where it helps someone read the same facts faster (§4); what the site must not do is imply that an entry was re-checked this week when it was not — that is what the `vérifié le` date and the event log are for.

## 4\. What it looks like

One site, in French, built for a phone. Most people arrive in June or in September looking for something that runs the whole season, so it is built to be scanned once, read properly, and come back to — not refreshed weekly.

**The page, top to bottom**

| Band | What is in it |
| :---- | :---- |
| Header | The title, one sentence from §2, and a link to the correction form |
| Filter bar | Age ("mon enfant a \_\_\_ ans"), commune, moment (matin / après-midi / journée), kind (cirque, sport, arts plastiques, …). Sticky as you scroll |
| View toggle | **Liste** (default) / **Mercredi** / **Carte** |
| Results | A count — "23 activités" — then the cards |
| Dated strip | "Ponctuel : stages et spectacles", the handful of dated items, below the recurring ones |
| Footer | The *À propos* text, the form link, the date of the last full sweep, mentions légales |

**The three views** are the same filtered set, drawn three ways. **Liste** is cards. **Mercredi** is a day grid — matin, après-midi, journée — so you can see what could fill a whole Wednesday. **Carte** is one pin per organiser. Switching views never changes which activities are shown.

**A card** is a summary: an icon for the kind of activity, the title, the organiser, the commune, the age range, the Wednesday pattern, the price note, `vérifié le 14/09/2026`, and the latest event if there is a recent one ("14/10 : complet jusqu'à septembre"). The icons come from one small set shipped with the site, chosen by the activity's kind tag — no external requests. An organiser image appears only if the organiser gave us one through the form or publishes a logo for that purpose; we do not copy photographs off other people's sites.

**The detail sheet.** Tapping a card opens a sheet with everything we hold, laid out for someone who is about to phone: the full description, ages, every Wednesday pattern, the price note, the address, the phone number and email (tappable `tel:` and `mailto:`), the enrolment link, the source we read and when, "ce qu'on sait" (the event log, newest first), and a share button. Contact details are published for structures — mairie, MJC, associations — and only as the structure publishes them on its own page; a private individual's number is never published, and anything is removed on request without argument. The sheet is the same content as the page at `/activite/<slug>`; arriving from a shared link gives you that page directly. That page is static HTML with its own title and Open Graph tags, which is what makes a pasted link show the activity's name and commune.

**Where the data comes from, in the browser.** The site loads a small index — one short record per activity, enough to filter and to draw a card — and fetches the full record for an activity when its sheet opens. Two files, not one lump: `site/data/index.json` and `site/data/activite/<slug>.json`. The index is tens of kilobytes at a few hundred entries; if it outgrows that, the builder shards it by commune and the front end does not change, because it asks the builder for "the index", not for a filename.

**The map.** One pin per organiser (not per activity — several activities share a building). Tapping a pin shows the organiser and the activities there, filtered by whatever the filter bar says. Coordinates are a field on the organiser record: a person copies a `lat`/`lon` from a map once, when the organiser is first added. There are a few dozen organisers, so there is no address-to-coordinates service to sign up for, no API key, and no quota to exceed. The map is Leaflet with public raster tiles, loaded only when Carte is pressed. Before it ships we read the tile provider's usage policy; if it forbids a site like this, the fallback is a static image of the agglomeration with dots drawn at build time.

## 5\. What done looks like

A checkable list for the first release. Each item is verifiable in an afternoon.

- [ ] A public site at `ministry-of-secret-robotron.github.io/on-fait-quoi-mercredi` lists at least 20 Wednesday activities across at least 8 organisers, in French, laid out as §4 describes on a phone-width screen.  
- [ ] Each entry shows: organiser, commune, ages, Wednesday morning / afternoon / full day, price note, a link to the organiser's own page, and the date it was last verified.  
- [ ] A parent can filter by age and by commune without the page reloading, and can switch between the list, the Wednesday grid, and the map.  
- [ ] Tapping an entry opens a sheet with the address and a tappable phone number, and that same content exists as its own page for sharing.  
- [ ] Every entry on the site corresponds to one merged pull request, reviewed by a human.  
- [ ] Every entry carries an event log, and a phone call recorded there ("complet jusqu'à la rentrée") is visible on the site within one merge.  
- [ ] The daily job is declared in `~/bureau/jobs/`, appears in `hq jobs`, runs through the Governor, and writes its logs where every other Bureau job writes them.  
- [ ] A local control panel shows the last runs and their logs and can start a run now.  
- [ ] The daily run re-checks the oldest entries as well as changed pages, and every robot pull request carries an independent check of its fields against the cited source.  
- [ ] Opening the same source twice does not create a second entry for the same activity, and a candidate that resembles an existing entry says so in its pull request.  
- [ ] A "signaler une erreur / proposer une activité" link opens a Google Form; each new response appears as a GitHub issue within a day, with a drafted pull request attached when the response is specific enough to draft one.  
- [ ] Neither intake can open more than the configured number of pull requests in a day.  
- [ ] An entry not verified for 60 days is visibly marked as possibly out of date.  
- [ ] `make test` passes, and CI runs it on every pull request.  
- [ ] Hosting costs nothing: public repo, Pages, Actions for tests and the build. Extraction runs on your existing Claude subscription, at most once a day, over changed pages plus the daily re-check quota.  
- [ ] The README and `docs/` tell a stranger — or Claude, arriving cold to fix a bug — what it is, how to run the build and the sweep locally, and how to install the job.

## 6\. How it works

One public GitHub repository holds everything: the data, the crawler, the site generator, and the site. There is no database and no server. Git is the database; a merge is a publish. The repo is public — free Actions and Pages, and an organiser can open a pull request. The raw response CSV never enters it.

Where there were two ways to do something, this design takes the one with fewer moving parts. Where it does not, it says why.

**The parts**

| Part | What it is | Where it runs |
| :---- | :---- | :---- |
| Seed list | `data/sources.yml` — the URLs from the intake inventory, each with an id, an organiser, and a kind (`html`, `pdf`, `aggregator`) | in the repo |
| Fetcher | Downloads each source, extracts text (including from PDFs), compares a hash against `state/<source-id>.json`, records every attempt and its outcome | your Mac, daily |
| Extractor | For changed pages and for the re-check quota: text → candidate activity records, with tags | your Mac, `claude -p`, same run |
| Matcher | Tags → shortlist of possible duplicates → read them → same, different, or unsure | your Mac, same run |
| Proposer | Turns each candidate into a branch and a draft pull request, one per activity, under a daily ceiling | your Mac, `gh` |
| Checker | Re-reads the cited source and judges each field in the PR, blind to how the extractor got there | GitHub Actions or your Mac, on each robot PR |
| Review | Bobby reads the PR: the diff, the quoted snippet, the checker's verdict, the link. Merge \= publish | GitHub |
| Data | `data/organisers/<slug>.yml`, `data/activities/<slug>.yml`, each with its event log | in the repo |
| Builder | Renders the pages, the index, and one JSON file per activity | GitHub Actions, on push to `main` |
| Site | Static HTML \+ index \+ per-activity JSON \+ vanilla JS \+ Leaflet on the map view | GitHub Pages |
| Corrections | Google Form → published CSV → one issue per new response, and a drafted PR where possible | your Mac, same daily run |
| Panel | A local web page: last runs, logs, attempt log, queue, and a button to run now | localhost, on demand |

**Where the robot lives, and how the Bureau sees it.** Everything that thinks runs on your machine, calling `claude -p` on the subscription you already pay for: no API key, no billing account, no secret in GitHub. It is a **Bureau job**, declared the way `capture-poll` and `todo-reminders-sync` are — one file, `~/bureau/jobs/wednesdays-sweep.md`, with frontmatter:

id: wednesdays-sweep

trigger: "cron: 0 7 \* \* \*"

concurrency: 1

backend: shell

run: "/Users/bobby/src/on-fait-quoi-mercredi/bin/sweep"

output: var/runs/{date}/{id}/

So it lists in `hq jobs`, starts on demand with `hq run wednesdays-sweep`, writes its logs to `~/bureau/var/runs/<date>/wednesdays-sweep/` like every other job, and takes a slot from the Governor (`~/bureau/policy/governor.yml`, `max_agents: 3`) before it spawns anything — so it shows up in `hq status` when you are asking where your machine went, and it queues rather than piling on when the machine is busy. The Bureau owns the schedule, the catch-up after sleep, the concurrency and the log paths; this project owns only the script. Absolute path in `run:` on purpose — launchd has no interactive PATH.

The repo also carries `.bureau.yml` (project, `test_command`, `allowed_repos`, `forbidden_paths`, `landing: on-green`, `max_parallel_agents`), so the corps can be pointed at it to fix a bug the normal way.

GitHub Actions keeps two jobs: run the tests on every pull request, and build and deploy on push to `main`. Neither needs a secret or an LLM, and deploy has to work when your laptop is shut, because that is the step between a merge and the site changing.

**What a human sets up once.** The GitHub repo and Pages under `ministry-of-secret-robotron`; the Google Form and publishing its responses as a CSV; pasting that CSV URL into `config.yml`; `gh` authenticated on the Mac; dropping the job file into `~/bureau/jobs/`; reading the tile provider's policy. After that the only recurring human act is reviewing pull requests — and typing a `lat`/`lon` when a new organiser appears.

**What flows**

your Mac, daily (Bureau job):

  sources.yml → fetch → changed? ┐

  oldest N entries → re-fetch ───┴→ extract (claude \-p) → candidate \+ tags

                                                              ↓

                                          match against existing entries by tag

                                                              ↓

                                        same → edit   different → new   unsure → say so

                                                              ↓

                                            draft PR (gh), under the daily ceiling

                                                              ↓

                                          checker re-reads the source, comments

  Google Form → published CSV → new response? → issue → drafted PR where possible

GitHub, on merge:

  data/\*.yml → build → site/ (pages \+ index \+ one JSON per activity) → Pages

**The record.** One file per activity, YAML, named by a slug derived from `<organiser>--<activity>--<ages>`:

| Field | Note |
| :---- | :---- |
| `title_fr`, `organiser`, `commune` | `organiser` is a reference to a file in `data/organisers/` |
| `ages: [min, max]` | integers; an entry with no stated age range is a question, not a guess |
| `when: matin | apres_midi | journee | date` | `date` for one-off stages and spectacles |
| `tags: [...]` | from the controlled list in `data/tags.yml`; kind, rhythm, setting. Drives the filters, the card icon, and duplicate matching |
| `price_note` | free text in French; prices here are often means-tested and not a number |
| `booking_url`, `source_url`, `source_last_seen` | the source is always linked, never paraphrased away |
| `verified_on` | the date of the merge that last confirmed this entry. This is what the card shows |
| `status: verified | unverified` | set by the merge, not by the robot |
| `notes_fr` | the description shown on the detail sheet |
| `events: [...]` | the event log, below |

The organiser record carries the name, the commune, the public page, the contact details as the organiser publishes them, and `lat`/`lon` for the map.

**The event log.** Each entry keeps a dated list of everything that happened to it, oldest first, and the detail sheet shows it as "ce qu'on sait":

| Field | Example |
| :---- | :---- |
| `date` | `2026-10-14` |
| `kind` | `appel`, `email`, `visite`, `source`, `correction`, `crawl` |
| `by` | `Maggie`, `Bobby`, `robot` |
| `note_fr` | "Appelé : complet jusqu'à la rentrée prochaine, liste d'attente ouverte" |
| `source_url` | optional; the page, form response, or PR the event came from |

This is what replaces guessing. **Availability** is the clearest case: hardly any source says whether a place is free, so the entry claims nothing by default. When someone phones and finds out, that becomes an event with a date and a name, and the card shows it as the latest news. The same log carries outreach ("emailed the MJC, no reply yet"), corrections received, and what the crawler did — including a source that refused to be crawled. Events are appended, never rewritten; a correction adds an event rather than erasing one.

Events written by other people arrive through the same Google Form as corrections, so they pass your merge before they reach an entry. The rule, stated once on the form and once in the contributing notes: first names only, facts about places and not about people, and not someone else's phone number.

**The attempt log.** Every run records, per source: when it was tried, and what happened — fetched, unchanged, 404, timed out, no text extracted, or refused by `robots.txt`. The durable per-source status is committed in `state/`; the full per-run detail sits in the Bureau run directory with the rest of the logs. A source we cannot crawl stays in `sources.yml` marked with why, so it is a visible gap rather than an absence nobody remembers, and the control panel lists them together.

**Keeping entries true over time.** Two mechanisms, both cheap:

1. **The re-check quota.** Each daily run re-reads the *N* entries with the oldest `verified_on` (default 5), whether or not their source changed. If nothing differs, it appends a `crawl` event and bumps `source_last_seen` — no PR, no noise. If something differs, it opens a correction PR. Information gets better a little at a time instead of having to be perfect on the day it is entered.  
2. **The check pass.** Every robot pull request gets a second opinion: a separate run fetches the URL the PR cites and answers, field by field, *supported* / *contradicted* / *not found in the source*, and posts that as a comment with a `vérifié-machine` or `contradiction` label. It is given the diff and the source, never the extractor's reasoning — the Bureau's blind-inspection rule, for the same reason: an explanation of why an answer is right is very good at making a wrong answer look right.

**Rate limits, so the queue stays readable.** At most 10 robot-authored pull requests open at once, and at most 10 opened per day, across both intakes (configurable). Above the ceiling the proposer holds candidates in `state/queue/` and opens them on later runs, so nothing is lost and nothing floods. The form adds its own limits: at most 5 responses processed per run, each response keyed by a hash so it can never be processed twice, and a drafted PR only when the response names an existing entry or supplies a source URL — the rest become issues, which cost nothing to close. The form is anonymous and public, so if it is ever abused the switches are: stop drafting PRs, and close the form in one click.

**The LLM step, and its fences.** An LLM reads the extracted text of a page and returns structured candidate records. It is there because the sources are prose, tables, and season brochures in PDF, in French, with no common format — a parser per site would be a dozen parsers that break every September. Four fences: it only runs on pages whose hash changed, plus the re-check quota; a field is only accepted with a quoted snippet from the source supporting it; the check pass re-reads the source independently; and nothing reaches the site without a human merge.

**Duplicate detection, in two passes.** The slug is the backstop: if the extractor proposes a slug that already exists, the PR edits that file rather than adding one, and if a PR for that slug is already open, it pushes to that branch instead of opening a second. That catches the same page read twice. It does not catch the same activity described differently by two sources — the MJC's own page and the tourist agenda — because those produce different slugs.

So a tag pass goes in front of it. The extractor assigns each candidate tags from the controlled list. The matcher filters existing activities down to those sharing the commune and at least one kind tag — usually a handful, never the whole dataset — and only those get read in full. Then, yes, the decision is another `claude -p` call: it is given the candidate and the shortlist and must answer with one of exactly three words, *same*, *different*, or *unsure*, plus the entry it means. It is a cheap comparison of a dozen short records, not a judgment about the world. *Unsure* is a first-class answer rather than a failure: the PR gets a `doublon?` label and a "doublon possible" section naming and linking what it resembles, and if there is no PR to attach it to, it opens an issue. The robot never silently decides a hard case and never silently drops one.

**Corrections become proposals too.** A form response is a candidate like any other, except the source is a person. The form takes four things: wrong information, a new activity, what someone learned about an entry ("complet jusqu'à la rentrée", which becomes an event), and "I am the organiser". Each new response opens an issue; where it is specific — it names an entry and states what is wrong, or gives a new activity with a source URL — the same proposer drafts the PR and links it from the issue, so your job is to read a diff rather than retype a correction. Where it is vague, the issue stands alone. Either way it is the same human merge gate, and the merge writes a `correction` event onto the entry.

**No redaction step in v1** (Bobby, 2026-09-23). A response becomes an issue body and a drafted diff as typed. The defences are the form's own wording, the same one-line rule in the contributing notes, and your merge — nothing reaches a data file without it. The raw CSV is not committed; the repo holds the drafted diff. An LLM cleansing pass can be added later at the same point in the drafting step if responses turn out to need it. One consequence is open in §9: the issue is opened by the daily run, so a response is public before you read it.

**The control panel.** A small local web app, served from the repo on localhost and bound to localhost only. It shows the last runs with their status and duration, each run's log, the attempt log per source, the held queue, and the open pull requests. It has two buttons: *run now* (which shells `hq run wednesdays-sweep`, so a manual run is the same run) and *pause*. Everything else on it is read-only. This is the per-project dashboard shape the Bureau's roadmap already expects — a central view aggregates over these later; there is no central run dashboard today.

**How we know it works.** Testing is not a slice; it ships with each one, and CI runs it on every pull request.

| What | How |
| :---- | :---- |
| Data files | Every `data/**.yml` validates against a schema — required fields, tags from the controlled list, dates real, coordinates inside a sane bounding box. Fast enough to run as a pre-commit hook |
| Builder | Unit tests: fixture data in, expected pages, index, and per-activity JSON out |
| Extractor | Golden tests over saved snapshots in `tests/fixtures/`. CI uses recorded model output, so CI needs no LLM; a separate `make extract-live` runs the same fixtures through `claude -p` on your machine and reports what drifted |
| Matcher | A fixture set of known duplicate and non-duplicate pairs, including the MJC-page-versus-agenda case; the suite fails if a known duplicate is called *different* |
| Site | The filters and views tested on the built output; a link check over `booking_url` and `source_url` weekly, opening one issue for dead links |
| The whole | `make test` is the single entry point, and `.bureau.yml`'s `test_command`, so `landing: on-green` means something |

**Documentation, for whoever arrives cold.** The README says what it is, how to build, how to run one sweep by hand, and how to install the job. `docs/` holds this design, the data schema with a commented example entry, a runbook for the three things that go wrong most (a source changed shape, the model returned nothing, the deploy failed), and `CLAUDE.md` pointing at all of it — written so Claude can be dropped into the repo to fix a bug without being briefed first.

**Where a human decides.** Exactly one place: merging the pull request. Everything upstream is a proposal; everything downstream is automatic.

**Who publishes it, and where.** The repository and Pages site live under the Bureau login, `ministry-of-secret-robotron`, because `gh` on the Mac is already authenticated as it and the automation pushes as whoever owns the repo. The site therefore starts at `ministry-of-secret-robotron.github.io/on-fait-quoi-mercredi`; a bought domain waits until the site has been shared beyond the family and stuck — a redirect later costs nothing. The site carries mentions légales naming you, with the Google Form as the contact channel. What exactly a personal, non-commercial French site is required to carry, I do not know and will not guess — it is a pre-launch checklist item in slice 1's README, to confirm before the site is shared beyond people you know.

## 7\. Slices — the order of work

§6 is the design; this is the order it gets built in. One row is one issue: a title, what it produces, and the criteria seeds the Scout can accept or bounce. The first one produces something visible.

**Rollout, and what it does to the order.** Both: a closed beta with a handful of parents first, then open sharing. So both intakes land early — the shareable activity pages in slice 6, the correction form in slice 7 — and the order does not have to be re-cut when the beta opens. Freshness moves to slice 8 as a result: correction merges write events into the data files from slice 7, and slice 8 is what renders them and adds the daily re-check.

| \# | Title | Produces |
| :---- | :---- | :---- |
| 1 | The shape, a working site, and the tests | a public page with real activities |
| 2 | The seed list and the daily Bureau job | change detection and an attempt log |
| 3 | From changed page to candidate records | candidates in the run log |
| 4 | One pull request per activity | the review queue |
| 5 | The check pass and publish-on-merge | a two-minute review |
| 6 | The site a parent uses | filters, views, detail sheet, shareable pages |
| 7 | Corrections in | the Google Form loop |
| 8 | Freshness: the re-check quota and the event log | information that improves over time |
| 9 | The control panel | run now, and see what happened |
| 10 | The map | the Carte view |

**1\. The shape, a working site, and the tests.** Create the repo, the record shape, the builder, and the test harness. Enter ten activities by hand from the intake inventory, as real data files. Deploy to Pages. Nothing is crawled yet; the site is real. *Criteria seeds:* ten `data/activities/*.yml` files validate against the schema, including empty event logs; `make build` produces the site from data only; `make test` runs schema validation and the builder tests, and CI runs it on every PR; the deployed page lists all ten on a phone-width screen in the layout of §4; the *À propos* text comes from `content/about_fr.md` and appears in the footer and in the page description; the repo carries `.bureau.yml`, `CLAUDE.md`, and a README that says what it is, how to build it, and carries the mentions-légales check as an open pre-launch item.

**2\. The seed list and the daily Bureau job.** Put the inventory into `data/sources.yml`. A sweep script fetches each source, extracts text from HTML and PDF alike, writes hashes and timestamps into `state/`, keeps changed text in `snapshots/`, records every attempt, and commits. The job is declared in `~/bureau/jobs/wednesdays-sweep.md`. *Criteria seeds:* every URL in the intake inventory appears in `sources.yml` with an id and a kind; `hq jobs` lists the job and `hq run wednesdays-sweep` runs it; logs land in `~/bureau/var/runs/<date>/wednesdays-sweep/`; the run acquires a Governor slot and queues rather than spawning when the ceiling is reached; a run against unchanged sources produces no commit; a run after a page changes writes a new snapshot and pushes it; a PDF source produces a text snapshot on the same path as an HTML one; a 404, a timeout, and a `robots.txt` refusal are each recorded as an outcome in `state/` rather than skipped silently; a run missed while the machine was asleep happens on wake; requests are sequential and identify the project in the user agent.

**3\. From changed page to candidate records.** The extractor calls `claude -p` on snapshot text and returns candidate records, each with the quoted snippet supporting it, its tags, and a confidence. No PRs yet — candidates land in a local run directory. *Criteria seeds:* given a saved copy of the SOU des écoles page, the extractor returns at least one candidate with correct ages and Wednesday pattern; given a saved page of the Mikado season brochure PDF, it returns at least one candidate; a scanned PDF with no text layer fails loudly rather than producing empty candidates; every non-null field is accompanied by a snippet present in the source text; every tag is from `data/tags.yml`; a page with no children's activity returns zero candidates rather than a guess; a run refuses to extract more than a configured number of pages, so a mass layout change cannot become an all-night run; golden tests run the fixtures from recorded output in CI, and `make extract-live` reports drift; each run logs pages seen, pages changed, candidates produced.

**4\. One pull request per activity.** Candidates become branches and draft PRs, one per activity, with the source link and the snippets in the body. Slug deduplication, the tag shortlist, and the daily ceiling. *Criteria seeds:* two runs over the same changed page produce one PR, not two; a candidate whose slug exists produces an edit diff, not a new file; a candidate sharing commune and kind tags with existing entries causes only those to be read, and the shortlist size is logged; the same activity found on two sources produces one entry or one flagged PR, never two silent entries; an unsure match produces a `doublon?` label and a "doublon possible" section naming the entries; an unsure candidate with no PR opens an issue; the PR body contains the source URL, the fetch date, and the supporting snippets; with the ceiling set to 2, a run with 5 candidates opens 2 PRs and holds 3 in `state/queue/`, which the next run opens; PRs are labelled by organiser.

**5\. The check pass and publish-on-merge.** An independent pass re-reads each robot PR's cited source and judges its fields; a PR template carries the checks Bobby actually makes; merging sets `status`, `verified_on`, and writes the merge as an event, then builds and deploys. *Criteria seeds:* every robot PR receives a comment marking each field *supported*, *contradicted*, or *not found*, with the quoted text it found; the checker is given the diff and the source URL and not the extractor's output or reasoning; a PR with a contradicted field gets a `contradiction` label and is not auto-anything; merging a PR results in the activity appearing on the live site without further action; merging sets `verified_on` to the merge date without anyone typing it, and appends an event; closing a PR without merging records the rejection so the same candidate is not proposed again next week; a reviewer can see ages, when, price, the checker's verdict, and possible duplicates without leaving the diff.

**6\. The site a parent uses.** Filters (age, commune, moment, kind) client-side with the state in the URL; the Liste and Mercredi views; the detail sheet; one rendered page per activity with its own Open Graph tags; the index-plus-per-activity data split. *Criteria seeds:* filtering is instant at 500 entries and the index is under 100 KB; the URL reflects the filter and restores it on reload; switching between Liste and Mercredi keeps the same set of activities; the sheet shows address, phone, email, event log, and both links, and the phone number is tappable on a phone; contact details shown are the organiser's own published ones, and an organiser record with no published number shows no number rather than a guess; `/activite/<slug>` exists for every entry, shows the same content as the sheet, and renders as static HTML; pasting one of those URLs into WhatsApp shows the activity name and commune; entries whose age range is unknown are shown, marked, not hidden; a card's icon comes from its kind tag and loads no external request.

**7\. Corrections in.** The Google Form (wrong information / new activity / what we learned about an entry / I am the organiser), linked from every card and sheet, read daily from its published CSV. Specific responses are drafted into PRs; both intakes share the ceiling. Events are written into the data files here; slice 8 renders them. *Criteria seeds:* a new form response becomes a GitHub issue within one scheduled run; the same response never creates two issues, keyed by a hash of the row; at most 5 responses are processed per run and the rest wait; a response naming an existing entry and a concrete correction produces a draft PR linked from the issue; a "what we learned" response produces a PR appending a dated, attributed event to that entry; a merged correction writes a `correction` event automatically; a vague response produces an issue and no PR; drafted PRs count against the same daily ceiling as crawl PRs; the raw CSV row is never committed — the repo holds only the drafted diff; the form's own intro text and the contributing notes both carry the one-line rule (first names, facts about places, not someone else's phone number); the form link is present on every card, sheet, and in the footer.

**8\. Freshness: the re-check quota and the event log.** The event log on every entry, rendered on the sheet and as a one-line latest-news on the card; the daily re-check of the oldest entries; staleness marks and a refresh list. *Criteria seeds:* an event appended by hand to a data file appears on the site after the next build, newest first, with its date; events written by slice 7's correction merges appear the same way; a run re-reads the 5 entries with the oldest `verified_on` even when their sources are unchanged; a re-check finding nothing different appends a `crawl` event and opens no PR; a re-check finding a difference opens a correction PR naming the field and quoting both old and new; each card shows its `verified_on` date; an entry not verified for 60 days is visibly marked and sorts last; a monthly job opens one issue listing the twenty stalest entries with links; deleting an entry removes it from the site on the next build; a source that has failed to fetch three days running opens an issue; the footer shows the date of the last full sweep.

**9\. The control panel.** A local web page listing runs, logs, per-source attempt status, the held queue, and open PRs, with a *run now* button and a *pause*. *Criteria seeds:* one documented command starts it and it binds to localhost only; it lists the last 20 runs from `~/bureau/var/runs/` with status and duration, and opens each run's log; it shows every source with its last attempt and outcome, including `robots.txt` refusals; it shows the held candidate queue and the open PR count against the ceiling; *run now* triggers `hq run wednesdays-sweep` and the resulting run appears in the list; *pause* stops the next scheduled run and says so; the panel is read-only apart from those two buttons; it works with the daily job never having run.

**10\. The map.** `lat`/`lon` on the organiser record, the Carte view, one pin per organiser, honouring the current filters. *Criteria seeds:* every organiser record has coordinates or is visibly absent from the map rather than placed at 0,0; the schema rejects coordinates outside the agglomeration's bounding box; the map library and tiles load only when Carte is pressed; pins reflect the active filters; tapping a pin lists that organiser's matching activities with links to their sheets; the tile provider's usage policy has been read and recorded in the README; the list view is unaffected when the map fails to load.

## 8\. Risks and unknowns

| Risk | What I would check first |
| :---- | :---- |
| The LLM extracts a plausible wrong time or price and a human merges it without noticing. | The check pass (slice 5\) exists for this. Before slice 4, run the extractor over five sources and hand-check every field against its snippet; if ages or Wednesday pattern are wrong more than rarely, tighten the snippet rule before building the queue. |
| Sites change layout each September, exactly when the data matters most. | Three defences in the design: re-extraction on change, the re-check quota, and the `verified_on` date with the monthly refresh list. The check is whether change detection is too noisy (menus, cookie banners) and fills the queue with empty PRs. |
| The daily job depends on your laptop being awake and your subscription being usable from a script. | Before slice 2, run `claude -p` once from the Bureau job runner and confirm it completes unattended. If it cannot, fetching stays scheduled and extraction becomes a *run now* from the panel. |
| Polite crawling of municipal and association sites. | Read `robots.txt` for each seed host before slice 2; one request per source per day; identified user agent. Every attempt and refusal is recorded, so "we never crawled that one" is visible rather than forgotten. |
| Publishing organiser contact details, some of which are personal names and emails. | Decided: publish only what the structure publishes on its own page, link rather than copy, never a private individual's number, remove on request without argument. Check at review time; no extra machinery in v1. |
| Someone types a stranger's phone number, or a remark about a named person, into a form response. | Decided: no redaction pass in v1. Nothing reaches a data file without your merge, and the form asks for facts about places. The residual is the issue the run opens automatically, which is public before you read it (§9). Check after the first month how many responses needed editing at all; if it is more than a couple, add the cleansing pass to the drafting step. |
| A public anonymous form invites spam. | The ceilings in §6 bound the damage to a handful of issues a day; the escape hatches are stopping PR drafting and closing the form. Check after the first month whether any human response arrived at all. |
| Mentions légales: I do not know what a personal French site must carry. | Confirm before the site is shared beyond people you know. A pre-launch item in the README, not a blocker for building. |
| Map tiles may not be free to use for a public site. | Read the tile provider's usage policy during slice 10\. Fallback is a build-time static image with dots. |
| Nobody uses it, so nobody corrects it. | The rollout is closed beta then open (§7), and both the shareable pages (slice 6\) and the correction form (slice 7\) ship before either. What is still unknown is who the beta parents are; the check is whether a correction arrives from someone outside the household in the first month. |
| The aggregator sources list venues rather than programmes and will produce low-quality candidates. | Keep them marked `aggregator` in the seed list and, if slice 3 shows the noise, use them only to discover new organisers. |

## 9\. Open questions for Bobby

One, and it is the tail of dropping the redaction pass.

1. **The issue a form response opens is public before you read it.** The daily run opens a GitHub issue on a public repo carrying the response as typed, hours before you see it. Merges are gated; issues are not. Recommendation: leave it — the form asks for facts about places, and a bad issue is deleted in two clicks. Say no and the run writes new responses to a local file the panel shows, opening nothing until you press a button; that costs the "a correction becomes an issue within a day" line in §5.