"""
event_bus.py — Jarvis Core Engine
===================================
A fully decoupled, synchronous event bus.

Responsibilities:
  - Allow any component to subscribe to named events.
  - Allow any component to emit events with arbitrary data payloads.
  - Core has zero knowledge of who listens or what they do.

Usage:
  bus = EventBus()
  bus.subscribe("intent.time", my_handler)
  bus.emit("intent.time", {"query": "What time is it?"})
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    """Central pub/sub event bus — the backbone of the entire system."""

    def __init__(self) -> None:
        # event_type -> list of callables
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, handler: Callable[[dict], Any]) -> None:
        """Register *handler* to be called whenever *event_type* is emitted.

        Args:
            event_type: Dot-separated string, e.g. "intent.time", "system.shutdown".
            handler: Any callable that accepts a single dict payload argument.
        """
        self._subscribers[event_type].append(handler)
        logger.debug("[EventBus] Subscribed: %s → %s", event_type, handler.__qualname__)

    def emit(self, event_type: str, data: dict | None = None) -> None:
        """Emit *event_type* and dispatch *data* to all registered handlers.

        Args:
            event_type: The event identifier to dispatch.
            data: Arbitrary payload delivered to each subscriber.
        """
        payload = data or {}
        handlers = self._subscribers.get(event_type, [])

        if not handlers:
            logger.debug("[EventBus] No subscribers for event: %s", event_type)
            return

        logger.debug("[EventBus] Emitting '%s' to %d subscriber(s)", event_type, len(handlers))

        for handler in handlers:
            try:
                handler(payload)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "[EventBus] Handler '%s' raised an exception for event '%s': %s",
                    handler.__qualname__,
                    event_type,
                    exc,
                    exc_info=True,
                )

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove a previously registered handler.

        Args:
            event_type: The event type the handler was subscribed to.
            handler: The exact callable to remove.
        """
        try:
            self._subscribers[event_type].remove(handler)
            logger.debug("[EventBus] Unsubscribed: %s → %s", event_type, handler.__qualname__)
        except ValueError:
            logger.warning(
                "[EventBus] Handler '%s' not found for event '%s'.",
                handler.__qualname__,
                event_type,
            )

    def subscribers(self, event_type: str) -> list[Callable]:
        """Return a copy of the handler list for inspection / testing."""
        return list(self._subscribers.get(event_type, []))
