"""Loading minimal people data and figuring out who has a birthday today."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from birthday_flow.relations import tone_for


@dataclass
class Person:
    """The minimal data we keep about a friend or relative."""

    name: str
    month: int
    day: int
    relation: str = "default"
    channel: str = "telegram"
    recipient: str = ""  # channel-specific address, e.g. a Telegram chat id
    language: str = "de"
    year: int | None = None  # optional birth year -> lets us mention the age

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Person":
        name = str(raw.get("name", "")).strip()
        if not name:
            raise ValueError("person entry is missing 'name'")
        month, day, year = _parse_birthday(raw.get("birthday"))
        return cls(
            name=name,
            month=month,
            day=day,
            year=year,
            relation=str(raw.get("relation", "default")).strip() or "default",
            channel=str(raw.get("channel", "telegram")).strip() or "telegram",
            recipient=str(raw.get("recipient", "")).strip(),
            language=str(raw.get("language", "de")).strip() or "de",
        )

    def has_birthday_on(self, today: date) -> bool:
        # Treat Feb 29 birthdays as Feb 28 in non-leap years.
        if self.month == 2 and self.day == 29 and not _is_leap(today.year):
            return today.month == 2 and today.day == 28
        return today.month == self.month and today.day == self.day

    def age_on(self, today: date) -> int | None:
        if self.year is None:
            return None
        return today.year - self.year

    def to_context(self, today: date) -> dict[str, Any]:
        """Flat dict consumed by the workflow (templating + dispatch)."""
        age = self.age_on(today)
        return {
            "name": self.name,
            "relation": self.relation,
            "channel": self.channel,
            "recipient": self.recipient,
            "language": self.language,
            "tone": tone_for(self.relation),
            "age": age,
            "age_hint": f" wird heute {age} Jahre alt" if age is not None else "",
        }


def _parse_birthday(value: Any) -> tuple[int, int, int | None]:
    """Accepts 'YYYY-MM-DD' or 'MM-DD' and returns (month, day, year|None)."""
    if not value or not isinstance(value, str):
        raise ValueError(f"invalid birthday: {value!r}")
    parts = value.split("-")
    if len(parts) == 3:
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    elif len(parts) == 2:
        year, month, day = None, int(parts[0]), int(parts[1])
    else:
        raise ValueError(f"invalid birthday format: {value!r} (use YYYY-MM-DD or MM-DD)")
    if not (1 <= month <= 12 and 1 <= day <= 31):
        raise ValueError(f"birthday out of range: {value!r}")
    return month, day, year


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def load_people(path: Path) -> list[Person]:
    """Reads the people file (JSON list of objects)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("people file must contain a JSON list")
    return [Person.from_dict(entry) for entry in data]


def birthdays_today(people: list[Person], today: date) -> list[Person]:
    return [p for p in people if p.has_birthday_on(today)]
