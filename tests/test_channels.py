import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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


def test_telegram_unavailable_without_credentials():
    channel = TelegramChannel(api_id="", api_hash="", phone="")
    assert not channel.is_available()


def test_telegram_available_with_credentials():
    channel = TelegramChannel(api_id="12345", api_hash="abc", phone="+491234567890")
    assert channel.is_available()


def test_telegram_send_raises_when_not_configured():
    channel = TelegramChannel(api_id="", api_hash="", phone="")
    with pytest.raises(RuntimeError, match="TELEGRAM_API_ID"):
        asyncio.run(channel.send("@someone", "hi"))


def test_telegram_send_calls_telethon():
    channel = TelegramChannel(
        api_id="12345", api_hash="abc", phone="+491234567890", session=":memory:"
    )
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.start = AsyncMock()
    mock_client.send_message = AsyncMock()
    mock_client.disconnect = AsyncMock()

    with patch("birthday_flow.channels.telegram.TelegramClient", return_value=mock_client):
        asyncio.run(channel.send("@someone", "Alles Gute!"))

    mock_client.start.assert_called_once_with(phone="+491234567890")
    mock_client.send_message.assert_called_once_with("@someone", "Alles Gute!")
    mock_client.disconnect.assert_called_once()
