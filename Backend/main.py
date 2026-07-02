"""
main.py — Jarvis Core Engine
==============================
Entry point and main event loop.

Bootstrap order:
  1. Configure logging
  2. Initialise EventBus
  3. Initialise IntentRouter (wired to bus)
  4. Initialise PluginLoader (wired to bus)
  5. Register all plugins
  6. Run interactive console loop
  7. Graceful shutdown on exit

Architecture contract:
  - Core components (bus, router, loader) are created ONCE and injected.
  - Plugins are NEVER imported in core — only in main.py and plugin_loader.
  - All inter-component communication goes through the EventBus.
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

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
BANNER = """
  +----------------------------------------------+
  |          J A R V I S  C O R E               |
  |               Engine v1.0.0                  |
  +----------------------------------------------+
  Type 'help' for commands. Type 'quit' to exit.
"""

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def bootstrap() -> tuple[EventBus, IntentRouter, PluginLoader]:
    """Initialise all core components and load plugins."""

    bus = EventBus()
    router = IntentRouter(bus)
    loader = PluginLoader(bus)

    # StatusPlugin needs a reference to loader (to list plugins dynamically)
    # We register it manually using a factory lambda so the loader can handle it.
    loader.load_all([
        TimePlugin,
        HelloPlugin,
        HelpPlugin,
        UnknownPlugin,
    ])

    # StatusPlugin requires an extra dependency — register manually
    status_instance = StatusPlugin(bus, loader)
    status_instance.register()
    # Inject into loader's registry directly for listing purposes
    loader._plugins[status_instance.name] = status_instance  # noqa: SLF001

    return bus, router, loader


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_loop(router: IntentRouter, loader: PluginLoader) -> None:
    """Interactive console input loop."""

    print(BANNER)
    print(f"  🔌  {len(loader)} plugin(s) loaded.\n")

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C or piped input ended
            print("\n  [Jarvis] Interrupted. Shutting down...\n")
            break

        if not raw:
            continue

        intent = router.route(raw)

        # Shutdown intent is handled here so the loop can exit cleanly
        if intent.event_type == "intent.shutdown":
            print("\n  🔴  Jarvis offline. Goodbye.\n")
            break


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main() -> None:
    bus, router, loader = bootstrap()
    try:
        run_loop(router, loader)
    finally:
        loader.shutdown_all()


if __name__ == "__main__":
    main()
