"""
main.py — Jarvis Core Engine
==============================
Entry point and main event loop.

Bootstrap order:
  1. Configure logging
  2. Initialise EventBus
  3. Initialise IntentRouter (wired to bus)
  4. Initialise PluginLoader (wired to bus)
  5. Initialise GeminiProvider (Phase 2)
  6. Register plugins (AIPlugin if key set, UnknownPlugin otherwise)
  7. Run interactive console loop
  8. Graceful shutdown on exit

Architecture contract:
  - Core components (bus, router, loader) are created ONCE and injected.
  - Plugins are NEVER imported in core — only in main.py and plugin_loader.
  - All inter-component communication goes through the EventBus.
  - AI provider is injected into AIPlugin; core has no AI knowledge.
"""

from __future__ import annotations

import logging
import sys
import os
import io

# Force UTF-8 output on Windows terminals that default to legacy codepages
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Path setup — allow "python main.py" from the Backend directory
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,           # set to DEBUG for verbose output
    format="%(levelname)-8s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Core imports
# ---------------------------------------------------------------------------
from core.event_bus import EventBus
from core.intent_router import IntentRouter
from core.plugin_loader import PluginLoader

# ---------------------------------------------------------------------------
# Plugin imports — ONLY place plugins are imported
# ---------------------------------------------------------------------------
from plugins.time_plugin import TimePlugin
from plugins.hello_plugin import HelloPlugin
from plugins.help_plugin import HelpPlugin
from plugins.unknown_plugin import UnknownPlugin
from plugins.status_plugin import StatusPlugin
from plugins.ai_plugin import AIPlugin

# ---------------------------------------------------------------------------
# AI / Config imports
# ---------------------------------------------------------------------------
from ai.gemini_provider import GeminiProvider
from config.config import is_ai_enabled

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
BANNER = """
  +----------------------------------------------+
  |          J A R V I S  C O R E               |
  |           Engine v2.0.0  [AI Phase]          |
  +----------------------------------------------+
  'yardım' yazarak komutları görebilirsin.
  'çıkış' yazarak kapatabilirsin.
"""

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def bootstrap() -> tuple[EventBus, IntentRouter, PluginLoader, GeminiProvider]:
    """Initialise all core components, AI provider, and load plugins.

    Returns:
        Tuple of (EventBus, IntentRouter, PluginLoader, GeminiProvider).
        GeminiProvider is returned for use in health_check / status display.
    """
    bus = EventBus()
    router = IntentRouter(bus)
    loader = PluginLoader(bus)

    # ----------------------------------------------------------------
    # AI Provider — initialised once and injected into AIPlugin
    # ----------------------------------------------------------------
    provider = GeminiProvider()

    # ----------------------------------------------------------------
    # Core plugins (always loaded)
    # ----------------------------------------------------------------
    loader.load_all([
        TimePlugin,
        HelloPlugin,
        HelpPlugin,
    ])

    # ----------------------------------------------------------------
    # Fallback plugin — AIPlugin if key present, UnknownPlugin if not
    # ----------------------------------------------------------------
    if is_ai_enabled():
        ai_instance = AIPlugin(bus, provider)
        ai_instance.register()
        loader._plugins[ai_instance.name] = ai_instance  # noqa: SLF001
    else:
        loader.load_all([UnknownPlugin])

    # ----------------------------------------------------------------
    # StatusPlugin requires loader reference — register manually
    # ----------------------------------------------------------------
    status_instance = StatusPlugin(bus, loader)
    status_instance.register()
    loader._plugins[status_instance.name] = status_instance  # noqa: SLF001

    return bus, router, loader, provider


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_loop(router: IntentRouter, loader: PluginLoader, provider: GeminiProvider) -> None:
    """Interactive console input loop."""

    print(BANNER)

    # Show AI status on startup
    ai_status = "AKTIF" if is_ai_enabled() else "DEVRE DISI (GEMINI_API_KEY eksik)"
    print(f"  Yuklu eklentiler : {len(loader)}")
    print(f"  AI durumu        : {ai_status}")
    print()

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C or piped input ended
            print("\n  [Jarvis] Durduruldu. Kapatiliyor...\n")
            break

        if not raw:
            continue

        intent = router.route(raw)

        # Shutdown intent is handled here so the loop can exit cleanly
        if intent.event_type == "intent.shutdown":
            print("\n  Jarvis cevrimdisi. Gorusmek uzere.\n")
            break


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main() -> None:
    bus, router, loader, provider = bootstrap()
    try:
        run_loop(router, loader, provider)
    finally:
        loader.shutdown_all()


if __name__ == "__main__":
    main()
