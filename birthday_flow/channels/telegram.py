"""Telegram channel — Telethon user API.

Sends messages as your own Telegram account (not as a bot), so recipients
do not need to have messaged you first.

Required env vars:
  TELEGRAM_API_ID    — from https://my.telegram.org
  TELEGRAM_API_HASH  — from https://my.telegram.org
  TELEGRAM_PHONE     — your phone number in international format, e.g. +4917612345678
  TELEGRAM_SESSION   — path to session file (default: telegram_session)

First run prompts for the SMS/app verification code interactively; subsequent
runs use the saved session file silently.
"""

from __future__ import annotations

import os

from telethon import TelegramClient

from birthday_flow.channels.base import Channel, register_channel


@register_channel
class TelegramChannel(Channel):
    name = "telegram"

    def __init__(
        self,
        api_id: str | None = None,
        api_hash: str | None = None,
        phone: str | None = None,
        session: str | None = None,
    ) -> None:
        self.api_id = api_id or os.environ.get("TELEGRAM_API_ID", "")
        self.api_hash = api_hash or os.environ.get("TELEGRAM_API_HASH", "")
        self.phone = phone or os.environ.get("TELEGRAM_PHONE", "")
        self.session = session or os.environ.get("TELEGRAM_SESSION", "telegram_session")

    def is_available(self) -> bool:
        return bool(self.api_id and self.api_hash and self.phone)

    async def send(self, recipient: str, message: str) -> None:
        if not self.is_available():
            raise RuntimeError(
                "Telegram not configured. Set TELEGRAM_API_ID, TELEGRAM_API_HASH, "
                "and TELEGRAM_PHONE. Get api_id/api_hash at https://my.telegram.org"
            )
        client = TelegramClient(self.session, int(self.api_id), self.api_hash)
        await client.start(phone=self.phone)
        try:
            await client.send_message(recipient, message)
        finally:
            await client.disconnect()
