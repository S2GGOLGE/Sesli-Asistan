"""
status_plugin.py — Jarvis Core Engine
========================================
Reports engine status and loaded plugins.

Listens to: intent.status
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus
    from core.plugin_loader import PluginLoader

logger = logging.getLogger(__name__)


class StatusPlugin(BasePlugin):
    """Reports live engine status when queried."""

    def __init__(self, bus: "EventBus", loader: "PluginLoader") -> None:
        super().__init__(bus)
        self._loader = loader

    @property
    def name(self) -> str:
        return "StatusPlugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Displays system health and list of loaded plugins."

    def register(self) -> None:
        self._bus.subscribe("intent.status", self._handle_status)
        logger.debug("[StatusPlugin] Subscribed to intent.status")

    def _handle_status(self, data: dict) -> None:
        plugins = self._loader.list_plugins()
        print(f"\n  🟢  Jarvis Core Engine — ONLINE")
        print(f"  🔌  Loaded plugins ({len(plugins)}):")
        for p in plugins:
            print(f"       • {p['name']} v{p['version']} — {p['description']}")
        print()
