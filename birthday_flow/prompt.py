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
