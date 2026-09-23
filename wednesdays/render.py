"""The page, top to bottom, exactly as the design's §4 lays it out.

Slice 1 draws four of §4's bands: the header, the results count, the cards, and the
footer. The filter bar, the view toggle and the detail sheet belong to slice 6, and
nothing here should grow into them.

Every string that reaches the markup is escaped, and every value on a card comes from a
data file. The stylesheet and the icons are inlined so that the page makes no request of
anything, which is both a privacy promise and the reason it works offline.
"""

from __future__ import annotations

import html

from . import french


def page(dataset, about, icons, stylesheet):
    """The whole of site/index.html, as one string."""
    body = "\n".join(
        [
            _header(about),
            _results(dataset, icons),
            _footer(about),
        ]
    )
    return _document(about, stylesheet, body)


def _document(about, stylesheet, body):
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="fr">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % _escape(french.PAGE_TITLE),
            '<meta name="description" content="%s">' % _escape(about.text),
            '<meta property="og:title" content="%s">' % _escape(french.PAGE_TITLE),
            '<meta property="og:description" content="%s">' % _escape(about.text),
            '<meta property="og:type" content="website">',
            "<style>",
            stylesheet.strip(),
            "</style>",
            "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
            "",
        ]
    )


def _header(about):
    return "\n".join(
        [
            "<header class=\"site-header\">",
            "<h1>%s</h1>" % _escape(french.SITE_TITLE),
            "<p class=\"site-blurb\">%s</p>" % _escape(about.first_sentence),
            "</header>",
        ]
    )


def _results(dataset, icons):
    cards = "\n".join(_card(activity, dataset, icons) for activity in dataset.activities)
    return "\n".join(
        [
            "<main>",
            '<p class="count">%s</p>' % _escape(french.count(len(dataset.activities))),
            '<ul class="activities">',
            cards,
            "</ul>",
            "</main>",
        ]
    )


def _card(activity, dataset, icons):
    organiser = dataset.organiser_of(activity)
    kind = _kind_of(activity, dataset)
    return "\n".join(
        [
            '<li class="card">',
            '<p class="card-kind">%s</p>' % _icon(kind, icons),
            "<h2>%s</h2>" % _escape(activity["title_fr"]),
            '<p class="card-who">%s<span class="card-commune">%s</span></p>'
            % (_escape(organiser["name"]), _escape(activity["commune"])),
            '<dl class="card-facts">',
            _fact(french.AGES_LABEL, french.ages(activity.get("ages")), "ages" in activity),
            _fact(french.MOMENT_LABEL, french.moments(activity.get("when")), "when" in activity),
            _fact(
                french.PRICE_LABEL,
                activity.get("price_note", french.PRICE_UNKNOWN),
                "price_note" in activity,
            ),
            "</dl>",
            '<p class="card-verified">%s (<a href="%s">%s</a>)</p>'
            % (
                _escape(french.verified_on(activity["verified_on"])),
                _escape(activity["source_url"]),
                _escape(french.SOURCE_LINK),
            ),
            "</li>",
        ]
    )


def _fact(label, value, stated):
    """An unstated field is shown as unstated, never dropped and never guessed."""
    classes = "fact" if stated else "fact fact-unknown"
    return '<div class="%s"><dt>%s</dt><dd>%s</dd></div>' % (
        classes,
        _escape(label),
        _escape(value),
    )


def _kind_of(activity, dataset):
    kinds = set(dataset.tags.get("kind", ()))
    for tag in activity["tags"]:
        if tag in kinds:
            return tag
    raise KeyError("%s has no kind tag" % activity["slug"])  # the schema forbids this


def _icon(kind, icons):
    label = french.KIND_LABELS.get(kind, kind)
    return '<span class="icon" role="img" aria-label="%s">%s</span>' % (
        _escape(label),
        icons[kind].strip(),
    )


def _footer(about):
    return "\n".join(
        [
            '<footer class="site-footer">',
            "<h2>%s</h2>" % _escape(french.ABOUT_HEADING),
            about.html,
            "</footer>",
        ]
    )


def _escape(text):
    return html.escape(text, quote=True)
