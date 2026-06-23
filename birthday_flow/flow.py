"""The birthday flow, built as a Stagehand workflow (a small DAG).

    find_birthdays  ->  compose (fan-out, one LLM call per person)  ->  dispatch

* ``find_birthdays`` (deterministic) loads people and keeps only today's.
* ``compose`` (agent, Ollama) writes one relation-aware message per person.
* ``dispatch`` (deterministic) sends each message via its channel.

The channels are decoupled: ``dispatch`` only looks them up in the registry, so
new channels need no change here.
"""

from __future__ import annotations

from typing import Any

from stagehand import RunContext, TaskResult, WorkflowBuilder
from stagehand.adapters.executor import OllamaExecutor

from birthday_flow.channels.base import get_channel
from birthday_flow.config import Config
from birthday_flow.people import birthdays_today, load_people
from birthday_flow.prompt import SYSTEM_PROMPT, TASK_PROMPT


def build_workflow(config: Config) -> WorkflowBuilder:
    """Assembles (but does not run) the workflow for the given config."""

    def find_birthdays(_ctx: RunContext) -> TaskResult:
        people = load_people(config.people_file)
        celebrants = birthdays_today(people, config.today)
        contexts = [p.to_context(config.today) for p in celebrants]
        names = ", ".join(c["name"] for c in contexts) or "niemand"
        return TaskResult(
            output=f"{len(contexts)} Geburtstag(e) heute: {names}",
            data=contexts,
        )

    def people_to_celebrate(ctx: RunContext) -> list[dict[str, Any]]:
        result = ctx.get_task_result("find_birthdays")
        return list(result.data or []) if result else []

    async def dispatch(ctx: RunContext) -> TaskResult:
        people = people_to_celebrate(ctx)
        compose = ctx.get_task_result("compose")
        messages = list(compose.data or []) if compose else []

        sent: list[str] = []
        for person, message in zip(people, messages):
            channel_name = "console" if config.dry_run else person["channel"]
            channel = get_channel(channel_name)
            await channel.send(person["recipient"], str(message).strip())
            sent.append(f"{person['name']} via {channel_name}")

        summary = "Nichts zu versenden." if not sent else "Versendet an: " + "; ".join(sent)
        return TaskResult(output=summary, data=sent)

    return (
        WorkflowBuilder("birthday-flow")
        .agent(
            "writer",
            OllamaExecutor(host=config.ollama_host),
            model=config.model,
            system_prompt=SYSTEM_PROMPT,
        )
        .state_dir(config.state_dir)
        .task("find_birthdays", fn=find_birthdays)
        .task(
            "compose",
            agent="writer",
            prompt=TASK_PROMPT,
            after=["find_birthdays"],
            over=people_to_celebrate,
        )
        .task("dispatch", fn=dispatch, after=["compose"])
    )


async def run_flow(config: Config | None = None) -> str:
    """Builds and runs the flow. Returns the Stagehand run id."""
    config = config or Config.from_env()
    return await build_workflow(config).run()
