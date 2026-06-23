"""Prompt building for the message-writing agent.

The system prompt is fixed; the per-person tone is injected through the task
prompt via Stagehand template expressions (``{{ item.* }}``).
"""

from __future__ import annotations

SYSTEM_PROMPT = (
    "Du bist ein einfuehlsamer Texter, der kurze, persoenliche "
    "Geburtstagsnachrichten schreibt. Du schreibst ausschliesslich die "
    "fertige Nachricht, ohne Anfuehrungszeichen, ohne Betreff, ohne "
    "Erklaerungen oder Vor-/Nachbemerkungen. Die Nachricht ist 2-4 Saetze "
    "lang und klingt natuerlich, als haette sie ein Mensch geschrieben."
)

# Resolved once per fan-out item. ``item`` is the person context dict.
TASK_PROMPT = (
    "Schreibe eine Geburtstagsnachricht in der Sprache '{{ item.language }}'.\n"
    "Empfaenger: {{ item.name }}.\n"
    "Beziehung zu mir: {{ item.relation }}.\n"
    "Gewuenschter Ton: {{ item.tone }}\n"
    "Zusatzinfo:{{ item.age_hint }}\n"
    "Sprich die Person direkt mit Namen an. Gib nur die Nachricht aus."
)


# --- Tone check -----------------------------------------------------------
# Second LLM step: a guardrail that verifies the draft matches the intended
# tone for the relationship and corrects it if needed.
TONE_CHECK_SYSTEM_PROMPT = (
    "Du bist ein Lektor fuer Geburtstagsnachrichten. Du pruefst, ob eine "
    "Nachricht zum gewuenschten Ton und zur Beziehung passt. Passt sie, gibst "
    "du sie unveraendert zurueck. Passt sie nicht (falscher Ton, zu lang/kurz, "
    "unpassend, falscher Name, Meta-Text), schreibst du sie korrigiert neu. "
    "Du gibst IMMER nur die finale Nachricht aus - ohne Anfuehrungszeichen, "
    "ohne Erklaerung, ohne Bewertung."
)

# ``item`` carries the person context plus the draft to review.
TONE_CHECK_PROMPT = (
    "Beziehung: {{ item.relation }}.\n"
    "Empfaenger: {{ item.name }}.\n"
    "Gewuenschter Ton: {{ item.tone }}\n"
    "Sprache: {{ item.language }}.\n"
    "Zu pruefender Entwurf:\n{{ item.draft }}\n\n"
    "Gib die finale, zum Ton passende Geburtstagsnachricht aus - nur die "
    "Nachricht selbst."
)
