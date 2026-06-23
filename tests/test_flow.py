import asyncio
import json
from datetime import date
from pathlib import Path

from stagehand.ports.executor import AgentExecutor, ExecutionRequest, ExecutionResult

import birthday_flow.flow as flow
from birthday_flow.config import Config


class FakeExecutor(AgentExecutor):
    """Stands in for Ollama: echoes the resolved prompt.

    Records every call on the class so tests can assert how many LLM steps ran
    across both agents (compose + tone_check).
    """

    calls: list[ExecutionRequest] = []

    def __init__(self, *args, **kwargs):
        pass

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        FakeExecutor.calls.append(request)
        # The prompt already has {{ item.* }} resolved by the scheduler.
        return ExecutionResult(output=f"FAKE-MSG[{request.prompt}]")


def _write_people(tmp_path: Path) -> Path:
    people = [
        {"name": "Oma", "birthday": "1948-06-23", "relation": "grandparent",
         "channel": "telegram", "recipient": "111"},
        {"name": "Lukas", "birthday": "06-23", "relation": "friend",
         "channel": "telegram", "recipient": "222"},
        {"name": "Mama", "birthday": "1965-03-12", "relation": "parent",
         "channel": "telegram", "recipient": "333"},
    ]
    path = tmp_path / "people.json"
    path.write_text(json.dumps(people), encoding="utf-8")
    return path


def _config(people_file: Path, today: date) -> Config:
    return Config(
        ollama_host="http://localhost:11434",
        model="qwen2.5",
        people_file=people_file,
        today=today,
        dry_run=True,  # routes everything to the console channel
        state_dir=str(people_file.parent / "runs"),
    )


def test_flow_sends_only_todays_birthdays(tmp_path, monkeypatch, capsys):
    FakeExecutor.calls = []
    monkeypatch.setattr(flow, "OllamaExecutor", FakeExecutor)
    config = _config(_write_people(tmp_path), date(2026, 6, 23))

    asyncio.run(flow.build_workflow(config).run())

    out = capsys.readouterr().out
    # Two people have a birthday on 06-23, one does not.
    assert "Oma" in out
    assert "Lukas" in out
    assert "Mama" not in out
    # Dry run routes to console, not telegram.
    assert "[console]" in out


def test_tone_check_runs_for_each_person(tmp_path, monkeypatch, capsys):
    FakeExecutor.calls = []
    monkeypatch.setattr(flow, "OllamaExecutor", FakeExecutor)
    config = _config(_write_people(tmp_path), date(2026, 6, 23))

    asyncio.run(flow.build_workflow(config).run())

    # 2 birthdays x (compose + tone_check) = 4 LLM calls.
    assert len(FakeExecutor.calls) == 4
    tone_check_calls = [c for c in FakeExecutor.calls if "Zu pruefender Entwurf" in c.prompt]
    assert len(tone_check_calls) == 2
    # The tone check sees the draft produced by compose.
    assert any("FAKE-MSG[" in c.prompt for c in tone_check_calls)


def test_flow_handles_no_birthdays(tmp_path, monkeypatch, capsys):
    FakeExecutor.calls = []
    monkeypatch.setattr(flow, "OllamaExecutor", FakeExecutor)
    config = _config(_write_people(tmp_path), date(2026, 1, 1))

    asyncio.run(flow.build_workflow(config).run())

    out = capsys.readouterr().out
    assert "[console]" not in out  # nothing sent
    assert FakeExecutor.calls == []  # no LLM work at all
