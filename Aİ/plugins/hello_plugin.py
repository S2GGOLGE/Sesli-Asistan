"""
hello_plugin.py — Jarvis Core Engine
=======================================
Greets the user when a greeting intent is detected.

Listens to: intent.hello
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from core.plugin_base import BasePlugin

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)

_RESPONSES = [
    "Hello! How can I assist you today?",
    "Hey there! Ready to help.",
    "Greetings. All systems operational.",
    "Hi! What do you need?",
    "Hello. Jarvis at your service.",
]


class HelloPlugin(BasePlugin):
    """Handles greeting intents."""

    @property
    def name(self) -> str:
        return "HelloPlugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Responds to user greetings with a randomised reply."

    def register(self) -> None:
        self._bus.subscribe("intent.hello", self._handle_hello)
        logger.debug("[HelloPlugin] Subscribed to intent.hello")

    def _handle_hello(self, data: dict) -> None:
        print(f"\n  👋  {random.choice(_RESPONSES)}\n")
