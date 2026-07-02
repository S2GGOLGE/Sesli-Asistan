"""
unknown_plugin.py — Jarvis Core Engine
=========================================
Basic fallback handler for unrecognised input.

NOTE (Phase 2):
  This plugin is now only loaded when the Gemini AI is disabled
  (i.e. GEMINI_API_KEY is not set). When AI is active, AIPlugin
  handles intent.unknown events instead.

Listens to: intent.unknown
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class UnknownPlugin(BasePlugin):
    """Basic fallback handler — active only when AI is not configured."""

    @property
    def name(self) -> str:
        return "UnknownPlugin"

    @property
    def version(self) -> str:
        return "1.1.0"

    @property
    def description(self) -> str:
        return "Temel geri dönüş mesajı — AI devre dışıyken aktif."

    def register(self) -> None:
        self._bus.subscribe("intent.unknown", self._handle_unknown)
        logger.debug("[UnknownPlugin] Subscribed to intent.unknown (AI-disabled fallback)")

    def _handle_unknown(self, data: dict) -> None:
        raw = data.get("raw_input", "")
        print(
            f"\n  ❓  '{raw}' ifadesini anlayamadım.\n"
            f"      'yardım' yazarak yapabileceklerimi görebilirsin.\n"
        )
