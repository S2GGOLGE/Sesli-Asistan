"""
ai_plugin.py — Jarvis Core Engine
=====================================
AI fallback plugin powered by Google Gemini.

This plugin subscribes to 'intent.unknown' — the event emitted when no
other plugin could handle the user's input.  It forwards the raw text to
GeminiProvider and prints the response.

Design principle:
  - UnknownPlugin is now removed from the load list in main.py.
  - AIPlugin becomes the single handler for unrecognised intents.
  - If the API key is missing, it prints a Turkish message gracefully.

Listens to: intent.unknown
Depends on: GeminiProvider (injected at construction)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus
    from ai.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)


class AIPlugin(BasePlugin):
    """Forwards unrecognised intents to Gemini and prints the Turkish response."""

    def __init__(self, bus: "EventBus", provider: "GeminiProvider") -> None:
        super().__init__(bus)
        self._provider = provider

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return "AIPlugin"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def description(self) -> str:
        return "Gemini AI fallback — answers anything no plugin handles (Turkish)."

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def register(self) -> None:
        self._bus.subscribe("intent.unknown", self._handle_ai)
        logger.info("[AIPlugin] Subscribed to intent.unknown — Gemini AI active.")

    # ------------------------------------------------------------------
    # Handler
    # ------------------------------------------------------------------

    def _handle_ai(self, data: dict) -> None:
        """Call Gemini with the raw user input and print the response."""
        raw = data.get("raw_input", "").strip()

        if not raw:
            return

        logger.info("[AIPlugin] Routing to Gemini: '%s'", raw)

        # Blocking call — Phase 2 is synchronous; async in a future phase
        response = self._provider.generate(raw)

        print(f"\n  🤖  {response}\n")
