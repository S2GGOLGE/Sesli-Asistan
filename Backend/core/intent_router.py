"""
intent_router.py — Jarvis Core Engine
=======================================
Translates raw text input into a structured Intent and emits it on the event bus.

Design principles:
  - Pure keyword-based matching (no ML, no external calls in this phase).
  - Each rule maps a set of trigger keywords to a named event type.
  - Unknown input emits "intent.unknown" so a plugin can still handle it gracefully.
  - Rules are data-driven and can be extended without touching the router logic.

Emitted events:
  intent.time         — user asked about the time or date
  intent.hello        — user greeted the assistant
  intent.status       — user asked for system status
  intent.help         — user asked for help / available commands
  intent.shutdown     — user wants to quit
  intent.unknown      — nothing matched
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Intent dataclass — structured result of routing
# ---------------------------------------------------------------------------

@dataclass
class Intent:
    """Structured representation of a recognised user intent."""

    event_type: str
    raw_input: str
    confidence: float = 1.0          # reserved for future probabilistic routing
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Routing rules — extend here to add new intents without touching router logic
# ---------------------------------------------------------------------------

_RULES: list[dict] = [
    {
        "event_type": "intent.time",
        "keywords": ["time", "saat", "clock", "date", "tarih", "today", "bugün"],
    },
    {
        "event_type": "intent.hello",
        "keywords": ["hello", "hi", "hey", "merhaba", "selam", "naber", "nasılsın"],
    },
    {
        "event_type": "intent.status",
        "keywords": ["status", "durum", "health", "alive", "çalışıyor", "online"],
    },
    {
        "event_type": "intent.help",
        "keywords": ["help", "yardım", "commands", "komutlar", "what can you do", "ne yapabilirsin"],
    },
    {
        "event_type": "intent.shutdown",
        "keywords": ["quit", "exit", "bye", "goodbye", "çıkış", "kapat", "dur", "shutdown"],
    },
]


# ---------------------------------------------------------------------------
# IntentRouter
# ---------------------------------------------------------------------------

class IntentRouter:
    """Routes raw text to an Intent and emits the result on the EventBus."""

    def __init__(self, bus: "EventBus") -> None:
        self._bus = bus
        logger.info("[IntentRouter] Initialised with %d rules.", len(_RULES))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(self, raw_text: str) -> Intent:
        """Parse *raw_text*, determine intent, emit on bus, return Intent.

        Args:
            raw_text: Raw string exactly as received from the input layer.

        Returns:
            The resolved Intent object.
        """
        text_lower = raw_text.strip().lower()

        intent = self._match(text_lower, raw_text)

        logger.debug(
            "[IntentRouter] '%s' → event_type='%s'",
            raw_text,
            intent.event_type,
        )

        self._bus.emit(
            intent.event_type,
            {
                "raw_input": raw_text,
                "intent": intent,
            },
        )

        return intent

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _match(self, text_lower: str, raw_text: str) -> Intent:
        """Return the first matching Intent or an 'intent.unknown' fallback."""
        for rule in _RULES:
            for keyword in rule["keywords"]:
                if keyword in text_lower:
                    return Intent(
                        event_type=rule["event_type"],
                        raw_input=raw_text,
                    )

        return Intent(
            event_type="intent.unknown",
            raw_input=raw_text,
            confidence=0.0,
        )

    def add_rule(self, event_type: str, keywords: list[str]) -> None:
        """Dynamically register a new routing rule at runtime.

        Plugins can call this to teach the router about new intents
        without modifying this file.

        Args:
            event_type: The event name to emit when a keyword matches.
            keywords: List of trigger words/phrases (case-insensitive).
        """
        _RULES.append({"event_type": event_type, "keywords": keywords})
        logger.info("[IntentRouter] New rule added: %s ← %s", event_type, keywords)
