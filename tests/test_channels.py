import asyncio

import pytest

from birthday_flow.channels.base import available_channels, get_channel
from birthday_flow.channels.telegram import TelegramChannel


def test_builtin_channels_are_discovered():
    channels = available_channels()
    assert "telegram" in channels
    assert "console" in channels


def test_get_unknown_channel_raises():
    with pytest.raises(KeyError):
        get_channel("carrier-pigeon")


def test_console_channel_prints(capsys):
    channel = get_channel("console")
    asyncio.run(channel.send("123", "Alles Gute!"))
    out = capsys.readouterr().out
    assert "Alles Gute!" in out
    assert "123" in out


def test_telegram_unavailable_without_token():
    channel = TelegramChannel(token="")
    assert not channel.is_available()
    with pytest.raises(RuntimeError):
        asyncio.run(channel.send("123", "hi"))


def test_telegram_available_with_token():
    assert TelegramChannel(token="abc").is_available()
