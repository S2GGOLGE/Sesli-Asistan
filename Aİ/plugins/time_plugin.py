"""
time_plugin.py — Jarvis Core Engine
======================================
Returns current time and date when the user asks.

Listens to: intent.time
Responds via: print() — replaced with bus event in future phases.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class TimePlugin(BasePlugin):
    """Handles time/date queries."""

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return "TimePlugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Returns current local time and date on intent.time events."

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def register(self) -> None:
        self._bus.subscribe("intent.time", self._handle_time)
        logger.debug("[TimePlugin] Subscribed to intent.time")

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _handle_time(self, data: dict) -> None:
        now = datetime.now()

        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %d %B %Y")

        print(f"\n  🕐  Time  : {time_str}")
        print(f"  📅  Date  : {date_str}\n")

        logger.debug("[TimePlugin] Responded with time=%s date=%s", time_str, date_str)
