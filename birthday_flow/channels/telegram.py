"""Telegram channel — the first real delivery channel.

Uses the Telegram Bot API directly (no extra dependency beyond httpx, which
ships with Stagehand). Configure with the ``TELEGRAM_BOT_TOKEN`` env var; each
person's ``recipient`` is their Telegram chat id.
"""

from __future__ import annotations

import os

import httpx

from birthday_flow.channels.base import Channel, register_channel


@register_channel
class TelegramChannel(Channel):
    name = "telegram"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")

    def is_available(self) -> bool:
        return bool(self.token)

    async def send(self, recipient: str, message: str) -> None:
        if not self.token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is not set; cannot send via Telegram"
            )
        if not recipient:
            raise ValueError("telegram channel requires a recipient chat id")
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": recipient, "text": message}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"telegram send failed ({resp.status_code}): {resp.text}"
                )
