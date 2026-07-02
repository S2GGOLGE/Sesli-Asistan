"""
plugin_base.py — Jarvis Core Engine
=====================================
Abstract base class every plugin must inherit from.

Contract:
  - Every plugin receives the shared EventBus on construction.
  - `register()` is called once by the PluginLoader — this is where the plugin
    subscribes to events and sets itself up.
  - `name` and `version` are metadata properties used by the loader/registry.
  - Plugins must NEVER import from each other directly; communicate only via bus.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.event_bus import EventBus


class BasePlugin(ABC):
    """Abstract base class for all Jarvis plugins."""

    def __init__(self, bus: "EventBus") -> None:
        self._bus = bus

    # ------------------------------------------------------------------
    # Metadata — override in subclass
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable plugin name, e.g. 'TimePlugin'."""

    @property
    def version(self) -> str:
        """Semantic version string. Override in subclass."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """Short one-line description of what this plugin does."""
        return "(no description)"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def register(self) -> None:
        """Subscribe to events and initialise the plugin.

        Called exactly once by the PluginLoader after construction.
        All bus.subscribe() calls belong here.
        """

    def shutdown(self) -> None:
        """Optional teardown hook — override if the plugin holds resources."""
