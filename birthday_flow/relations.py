"""Mapping from a relationship to the tone/style the birthday message should use.

This is the one place that encodes "how do we talk to this kind of person".
Add or tweak relations here without touching the flow or the channels.
"""

from __future__ import annotations

# Each entry is a short instruction handed to the language model describing the
# desired tone for that relationship. Keep them in the message language (German
# by default, since the people file uses `language`).
RELATION_TONES: dict[str, str] = {
    "grandparent": (
        "Sehr herzlich, respektvoll und liebevoll. Bedanke dich fuer alles, "
        "wuensche vor allem Gesundheit. Eher klassisch und ruhig im Ton."
    ),
    "parent": (
        "Warm, dankbar und persoenlich. Zeige Naehe und Wertschaetzung, "
        "darf ruhig ein bisschen emotional sein."
    ),
    "sibling": (
        "Locker, vertraut und herzlich, mit einem kleinen Augenzwinkern. "
        "Geschwister-Humor ist erlaubt."
    ),
    "partner": (
        "Sehr liebevoll, romantisch und persoenlich. Zeige tiefe Zuneigung."
    ),
    "friend": (
        "Locker, humorvoll und freundschaftlich. Darf frech und verspielt sein."
    ),
    "colleague": (
        "Freundlich, aber hoeflich und etwas zurueckhaltend. "
        "Professionell und nicht zu privat."
    ),
    "default": (
        "Warm, freundlich und aufrichtig. Neutral genug fuer fast jeden Anlass."
    ),
}


def tone_for(relation: str | None) -> str:
    """Returns the tone instruction for a relation, falling back to default."""
    if not relation:
        return RELATION_TONES["default"]
    return RELATION_TONES.get(relation.strip().lower(), RELATION_TONES["default"])
