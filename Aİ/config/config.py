"""
config.py — Jarvis Core Engine
================================
Centralised configuration loader.

Reads from a .env file in the project root using python-dotenv.
Never hardcodes secrets — all sensitive values come from environment variables.

Available settings (with defaults):
  GEMINI_API_KEY      (required for AI features, no default)
  GEMINI_MODEL        (default: "gemini-2.0-flash")
  GEMINI_TIMEOUT      (default: 30 seconds)
  GEMINI_MAX_TOKENS   (default: 1024)
  LOG_LEVEL           (default: "WARNING")
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from the project root (the directory containing main.py)
# ---------------------------------------------------------------------------

# __file__ → config/config.py  →  parent = config/  →  parent.parent = project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=_ENV_PATH, override=False)

logger = logging.getLogger(__name__)

if _ENV_PATH.exists():
    logger.debug("[Config] Loaded .env from: %s", _ENV_PATH)
else:
    logger.warning(
        "[Config] No .env file found at %s. "
        "AI features will be unavailable unless GEMINI_API_KEY is set as a system variable.",
        _ENV_PATH,
    )


# ---------------------------------------------------------------------------
# Public configuration accessors
# ---------------------------------------------------------------------------

def get_gemini_api_key() -> str | None:
    """Return the Gemini API key from the environment.

    Returns:
        The API key string, or None if not set.
        The value is NEVER logged or printed.
    """
    return os.getenv("GEMINI_API_KEY")


def get_gemini_model() -> str:
    """Return the Gemini model identifier to use.

    Defaults to 'gemini-2.0-flash' — fast and capable for assistant use cases.
    """
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def get_gemini_timeout() -> int:
    """Return the HTTP timeout (seconds) for Gemini API calls."""
    try:
        return int(os.getenv("GEMINI_TIMEOUT", "30"))
    except ValueError:
        logger.warning("[Config] Invalid GEMINI_TIMEOUT value; defaulting to 30s.")
        return 30


def get_gemini_max_tokens() -> int:
    """Return the maximum number of output tokens to request from Gemini."""
    try:
        return int(os.getenv("GEMINI_MAX_TOKENS", "1024"))
    except ValueError:
        logger.warning("[Config] Invalid GEMINI_MAX_TOKENS value; defaulting to 1024.")
        return 1024


def get_log_level() -> int:
    """Return the logging level as an integer constant."""
    level_name = os.getenv("LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    return level


def is_ai_enabled() -> bool:
    """Return True if a Gemini API key is present in the environment."""
    return bool(get_gemini_api_key())
