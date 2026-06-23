"""Channel package with auto-discovery.

Importing any module in this package that defines a ``@register_channel`` class
is enough to make that channel available. ``load_channels()`` imports every
submodule so dropping a new file here is all it takes to add a channel.
"""

from __future__ import annotations

import importlib
import pkgutil

_loaded = False


def load_channels() -> None:
    """Imports all channel submodules so they self-register. Idempotent."""
    global _loaded
    if _loaded:
        return
    for module in pkgutil.iter_modules(__path__):
        if module.name in {"base"}:
            continue
        importlib.import_module(f"{__name__}.{module.name}")
    _loaded = True
