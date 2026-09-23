"""Every French string the site shows that is not in data/ or content/.

The site is French-only, so these are not translations: they are the template's own
words. Copy that a reader might want to change without touching code lives in
content/; this is the furniture around it.
"""

from __future__ import annotations

SITE_TITLE = "On fait quoi mercredi ?"
PAGE_TITLE = "On fait quoi mercredi ? Les activités du mercredi autour d'Annecy"
ABOUT_HEADING = "À propos"

KIND_LABELS = {
    "accueil_de_loisirs": "Accueil de loisirs",
    "cirque": "Cirque",
    "sport": "Sport",
    "arts_plastiques": "Arts plastiques",
    "musique": "Musique",
    "danse": "Danse",
    "theatre": "Théâtre",
    "nature": "Nature",
}

MOMENT_LABELS = {
    "matin": "matin",
    "apres_midi": "après-midi",
    "journee": "journée",
}

AGES_LABEL = "Âge"
MOMENT_LABEL = "Mercredi"
PRICE_LABEL = "Tarif"

AGES_UNKNOWN = "non précisé par la source"
MOMENT_UNKNOWN = "horaire non précisé par la source"
PRICE_UNKNOWN = "non indiqué par la source"

SOURCE_LINK = "la source"

# Between the organiser and the commune on a card. It is text rather than a CSS
# ::before, so the two names still read apart when the page is rendered unstyled.
WHO_SEPARATOR = " · "


def count(number):
    """`23 activités`, the results band of the design's §4."""
    return "%d activité%s" % (number, "" if number < 2 else "s")


def ages(bounds):
    if not bounds:
        return AGES_UNKNOWN
    low, high = bounds
    if low == high:
        return "%d ans" % low
    return "de %d à %d ans" % (low, high)


def moments(values):
    """`matin, après-midi ou journée` - the Wednesday pattern, as a parent would say it."""
    if not values:
        return MOMENT_UNKNOWN
    labels = [MOMENT_LABELS[value] for value in values]
    if len(labels) == 1:
        return labels[0]
    return "%s ou %s" % (", ".join(labels[:-1]), labels[-1])


def date(iso):
    """2026-09-23 -> 23/09/2026. The site is French; the data stays ISO."""
    year, month, day = iso.split("-")
    return "%s/%s/%s" % (day, month, year)


def verified_on(iso):
    return "vérifié le %s" % date(iso)
