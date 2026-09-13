"""Test preconditions: expose the hyphenated plugin dir and register the platform name.

Two things the tests need that Hermes provides for real at runtime:

1. **Imports.** Hermes loads plugins by file path, so a hyphenated directory name is
   fine there; Python imports are not. The package is registered here as ``yeoman_a2a``.

2. **``Platform("yeoman")``.** ``Platform`` is a closed enum with a ``_missing_`` hook
   that accepts an unknown name only when it is already registered — either as a
   bundled plugin platform or in ``gateway.platform_registry``. At runtime the plugin's
   ``register(ctx)`` runs ``ctx.register_platform(name="yeoman", ...)`` *before* the
   gateway builds the adapter, so the lookup succeeds. These tests build the adapter
   directly, so the name is registered here to reproduce that precondition.

Run from a Hermes install with the pinned contract package present:

    ~/.hermes/hermes-agent/venv/bin/python -m pytest yeoman-a2a/tests -q
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
PACKAGE = "yeoman_a2a"
PLATFORM_NAME = "yeoman"

if PACKAGE not in sys.modules:
    module = types.ModuleType(PACKAGE)
    module.__path__ = [str(PLUGIN_DIR)]  # type: ignore[attr-defined]
    module.__package__ = PACKAGE
    sys.modules[PACKAGE] = module


def _register_platform_name() -> None:
    from gateway.config import Platform

    try:
        Platform(PLATFORM_NAME)
    except ValueError:
        # Same call `Platform._missing_` makes once it has decided the name is known.
        Platform._add_pseudo_member(PLATFORM_NAME)


_register_platform_name()
