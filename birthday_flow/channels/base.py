"""Channel abstraction + registry.

A *channel* is a way to deliver a message (Telegram, e-mail, SMS, ...). New
channels register themselves with ``@register_channel`` and are auto-discovered
at startup, so the core flow never has to change to support a new channel.
"""

from __future__ import annotations

import abc
from typing import Type


class Channel(abc.ABC):
    """Delivers a single text message to a recipient on one transport."""

    #: Unique channel key referenced by a person's ``channel`` field.
    name: str = ""

    @abc.abstractmethod
    async def send(self, recipient: str, message: str) -> None:
        """Delivers ``message`` to ``recipient``. Raises on failure."""

    def is_available(self) -> bool:
        """Whether this channel is configured well enough to actually send.

        Channels that need credentials override this; the default assumes ready.
        """
        return True


_REGISTRY: dict[str, Type[Channel]] = {}


def register_channel(cls: Type[Channel]) -> Type[Channel]:
    """Class decorator that registers a channel under its ``name``."""
    key = getattr(cls, "name", "")
    if not key:
        raise ValueError(f"channel {cls.__name__} must define a non-empty 'name'")
    if key in _REGISTRY and _REGISTRY[key] is not cls:
        raise ValueError(f"channel name {key!r} already registered")
    _REGISTRY[key] = cls
    return cls


def get_channel(name: str) -> Channel:
    """Instantiates the channel registered under ``name``."""
    from birthday_flow.channels import load_channels

    load_channels()
    if name not in _REGISTRY:
        raise KeyError(
            f"unknown channel {name!r}; available: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[name]()


def available_channels() -> list[str]:
    from birthday_flow.channels import load_channels

    load_channels()
    return sorted(_REGISTRY)
