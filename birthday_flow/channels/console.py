"""Console channel — prints messages instead of sending them.

Handy for local testing and used automatically when ``BIRTHDAY_DRY_RUN`` is on.
It also demonstrates how little is needed to add a new channel: one file, one
class, one ``@register_channel``.
"""

from __future__ import annotations

from birthday_flow.channels.base import Channel, register_channel


@register_channel
class ConsoleChannel(Channel):
    name = "console"

    async def send(self, recipient: str, message: str) -> None:
        target = recipient or "(no recipient)"
        print(f"\n--- [console] to {target} ---\n{message}\n")
