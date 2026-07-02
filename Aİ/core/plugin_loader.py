"""
plugin_loader.py — Jarvis Core Engine
========================================
Manual plugin registry and lifecycle manager.

Responsibilities:
  - Maintain a registry of all loaded plugins.
  - Call `plugin.register()` once per plugin.
  - Provide `load_all()` convenience method for bootstrap.
  - Provide `shutdown_all()` for clean teardown.
  - Enforce the BasePlugin contract (type check on registration).

This phase: manual registration only.
Future phase: auto-discovery via directory scan or entry-points.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Type

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)


class PluginLoader:
    """Registry and lifecycle manager for all Jarvis plugins."""

    def __init__(self, bus: "EventBus") -> None:
        self._bus = bus
        self._plugins: dict[str, BasePlugin] = {}   # name → instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, plugin_class: Type[BasePlugin]) -> None:
        """Instantiate *plugin_class*, call register(), add to registry.

        Args:
            plugin_class: A class that inherits from BasePlugin.

        Raises:
            TypeError: If plugin_class is not a BasePlugin subclass.
            ValueError: If a plugin with the same name is already registered.
        """
        if not (isinstance(plugin_class, type) and issubclass(plugin_class, BasePlugin)):
            raise TypeError(
                f"Expected a BasePlugin subclass, got: {plugin_class!r}"
            )

        # Instantiate first to get the name
        instance = plugin_class(self._bus)

        if instance.name in self._plugins:
            raise ValueError(
                f"Plugin '{instance.name}' is already registered. "
                "Duplicate names are not allowed."
            )

        instance.register()
        self._plugins[instance.name] = instance

        logger.info(
            "[PluginLoader] Loaded: %-20s v%s — %s",
            instance.name,
            instance.version,
            instance.description,
        )

    def load_all(self, plugin_classes: list[Type[BasePlugin]]) -> None:
        """Register a list of plugin classes in order.

        Args:
            plugin_classes: Ordered list of BasePlugin subclasses to load.
        """
        for cls in plugin_classes:
            try:
                self.register(cls)
            except Exception as exc:  # noqa: BLE001
                logger.error("[PluginLoader] Failed to load %s: %s", cls.__name__, exc)

    def shutdown_all(self) -> None:
        """Call shutdown() on every registered plugin in reverse load order."""
        for name, plugin in reversed(list(self._plugins.items())):
            try:
                plugin.shutdown()
                logger.info("[PluginLoader] Shutdown: %s", name)
            except Exception as exc:  # noqa: BLE001
                logger.error("[PluginLoader] Error during shutdown of '%s': %s", name, exc)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def list_plugins(self) -> list[dict]:
        """Return metadata for all loaded plugins."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
            }
            for p in self._plugins.values()
        ]

    def get(self, name: str) -> BasePlugin | None:
        """Retrieve a plugin instance by name."""
        return self._plugins.get(name)

    def __len__(self) -> int:
        return len(self._plugins)
