"""
help_plugin.py — Jarvis Core Engine
======================================
Lists available commands when the user asks for help.

Listens to: intent.help
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)

_HELP_TEXT = """
  📖  Available commands:
  ─────────────────────────────────────────────
  time / saat / date     → Current time & date
  hello / merhaba        → Greet Jarvis
  status / durum         → Engine status
  help / yardım          → This help message
  quit / exit / kapat    → Shut down Jarvis
  ─────────────────────────────────────────────
"""


class HelpPlugin(BasePlugin):
    """Displays help text listing available intents."""

    @property
    def name(self) -> str:
        return "HelpPlugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Prints the list of available commands on intent.help."

    def register(self) -> None:
        self._bus.subscribe("intent.help", self._handle_help)
        logger.debug("[HelpPlugin] Subscribed to intent.help")

    def _handle_help(self, data: dict) -> None:
        print(_HELP_TEXT)
