"""Runtime configuration for the birthday flow.

Everything is driven by environment variables so the flow can run locally
without code changes. Sensible defaults keep it working out of the box with a
local Ollama instance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_PEOPLE_FILE = _PROJECT_ROOT / "data" / "people.json"
_EXAMPLE_PEOPLE_FILE = _PROJECT_ROOT / "data" / "people.example.json"


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    """Resolved configuration for a single flow run."""

    ollama_host: str
    model: str
    people_file: Path
    today: date
    dry_run: bool
    state_dir: str

    @classmethod
    def from_env(cls) -> "Config":
        people_file = os.environ.get("BIRTHDAY_PEOPLE_FILE")
        if people_file:
            resolved = Path(people_file)
        elif _DEFAULT_PEOPLE_FILE.exists():
            resolved = _DEFAULT_PEOPLE_FILE
        else:
            # Fall back to the bundled example so a fresh checkout runs.
            resolved = _EXAMPLE_PEOPLE_FILE

        date_override = os.environ.get("BIRTHDAY_DATE")
        today = date.fromisoformat(date_override) if date_override else date.today()

        return cls(
            ollama_host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            model=os.environ.get("BIRTHDAY_MODEL", "qwen2.5"),
            people_file=resolved,
            today=today,
            dry_run=_truthy(os.environ.get("BIRTHDAY_DRY_RUN")),
            state_dir=os.environ.get("BIRTHDAY_STATE_DIR", ".stagehand/runs"),
        )
