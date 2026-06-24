"""Entry point: ``python -m birthday_flow``.

Reads configuration from the environment, runs the flow once, and prints a
short summary. Intended to be triggered locally (e.g. via cron) once a day.
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv
from stagehand import StdlibLogger

from birthday_flow.channels.base import available_channels
from birthday_flow.config import Config
from birthday_flow.flow import build_workflow


def main() -> None:
    load_dotenv()
    asyncio.run(_main())


async def _main() -> None:
    config = Config.from_env()
    print(
        f"birthday-flow | date={config.today} model={config.model} "
        f"dry_run={config.dry_run} channels={available_channels()}"
    )
    print(f"people file: {config.people_file}")

    builder = build_workflow(config).logger(StdlibLogger())
    run_id = await builder.run()
    print(f"done (run_id={run_id})")


if __name__ == "__main__":
    main()
