"""
gemini_provider.py — Jarvis Core Engine
=========================================
Google Gemini API provider — uses the new official `google-genai` SDK.

Responsibilities:
  - Send prompts to the Gemini API and return clean text responses.
  - Apply a strict Turkish-language persona via system instruction.
  - Handle all possible failure modes gracefully (no crash, friendly messages).
  - Report request timing for observability.

Public API:
  GeminiProvider.generate(prompt: str) -> str
  GeminiProvider.health_check() -> bool

Dependencies:
  google-genai   (pip install google-genai)
  config.config  (internal — reads GEMINI_API_KEY, model, timeout, max_tokens)

Error handling matrix:
  ┌──────────────────────────┬──────────────────────────────────────────┐
  │ Failure                  │ Behaviour                                │
  ├──────────────────────────┼──────────────────────────────────────────┤
  │ API key missing          │ Friendly Turkish message, no crash       │
  │ No internet / timeout    │ Friendly Turkish message, no crash       │
  │ Invalid API key (403)    │ Friendly Turkish message, no crash       │
  │ Rate limit (429)         │ Friendly Turkish message, no crash       │
  │ Any other Gemini error   │ Friendly Turkish message, no crash       │
  └──────────────────────────┴──────────────────────────────────────────┘
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from config.config import (
    get_gemini_api_key,
    get_gemini_model,
    get_gemini_timeout,
    get_gemini_max_tokens,
    is_ai_enabled,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Jarvis personality / system instruction (Turkish)
# ---------------------------------------------------------------------------

_SYSTEM_INSTRUCTION = """
Sen Jarvis'sin — gelişmiş bir yapay zeka asistanı.

KİŞİLİK:
- Sakin, yardımsever ve profesyonelsin.
- Teknik konularda bilgilisin.
- Yapamayacağın şeyleri asla iddia etmezsin.
- Kısa ve öz cevaplar verirsin; detay istenirse genişletirsin.

DİL KURALI:
- HER ZAMAN Türkçe cevap ver.
- Kullanıcı açıkça İngilizce isterse İngilizce cevap verebilirsin.
- Diğer tüm durumlarda Türkçe kullan.

KAPSAM:
- Genel bilgi, sohbet, teknik sorular, tavsiye isteklerini karşıla.
- Gerçek zamanlı veri (anlık hisse fiyatı, hava durumu vb.) isteklerinde
  bunu yapamayacağını nazikçe belirt.
""".strip()

# ---------------------------------------------------------------------------
# Error messages (Turkish)
# ---------------------------------------------------------------------------

_ERR_NO_KEY = (
    "Üzgünüm, AI servisi şu anda yapılandırılmamış. "
    "Lütfen .env dosyasına GEMINI_API_KEY ekleyin."
)
_ERR_NO_INTERNET = (
    "Üzgünüm, AI servisine ulaşamıyorum. "
    "İnternet bağlantınızı kontrol edin ve tekrar deneyin."
)
_ERR_INVALID_KEY = (
    "Üzgünüm, API anahtarı geçersiz görünüyor. "
    "Lütfen .env dosyasındaki GEMINI_API_KEY değerini kontrol edin."
)
_ERR_RATE_LIMIT = (
    "Şu anda çok fazla istek var. "
    "Lütfen birkaç saniye bekleyip tekrar deneyin."
)
_ERR_GENERIC = (
    "Üzgünüm, şu anda bir sorun yaşıyorum ve cevap veremiyorum. "
    "Lütfen biraz sonra tekrar deneyin."
)


# ---------------------------------------------------------------------------
# GeminiProvider
# ---------------------------------------------------------------------------

class GeminiProvider:
    """Sends prompts to Google Gemini and returns Turkish text responses.

    Uses the new official `google-genai` SDK (google.genai).
    """

    def __init__(self) -> None:
        self._model_name: str = get_gemini_model()
        self._timeout: int = get_gemini_timeout()
        self._max_tokens: int = get_gemini_max_tokens()
        self._client: Optional[object] = None   # lazy-initialised on first use

        if is_ai_enabled():
            self._init_client()
        else:
            logger.warning(
                "[GeminiProvider] GEMINI_API_KEY not set — AI features disabled."
            )

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_client(self) -> None:
        """Initialise the new google-genai SDK client."""
        try:
            from google import genai                        # type: ignore[import]
            from google.genai import types as genai_types  # type: ignore[import]

            api_key = get_gemini_api_key()
            self._client = genai.Client(api_key=api_key)
            self._genai_types = genai_types

            logger.info(
                "[GeminiProvider] Client initialised — model: %s, max_tokens: %d, timeout: %ds",
                self._model_name,
                self._max_tokens,
                self._timeout,
            )

        except ImportError:
            logger.error(
                "[GeminiProvider] 'google-genai' package not installed. "
                "Run: pip install google-genai"
            )
            self._client = None
        except Exception as exc:  # noqa: BLE001
            logger.error("[GeminiProvider] Failed to initialise client: %s", exc)
            self._client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, prompt: str) -> str:
        """Send *prompt* to Gemini and return the text response.

        Args:
            prompt: The user's natural-language input.

        Returns:
            Clean text response (never raises — all errors return a message).
        """
        if not is_ai_enabled():
            return _ERR_NO_KEY

        if self._client is None:
            self._init_client()
            if self._client is None:
                return _ERR_GENERIC

        logger.info("[GeminiProvider] Request started — prompt length: %d chars", len(prompt))
        t_start = time.perf_counter()

        try:
            from google.genai import types as genai_types  # type: ignore[import]

            response = self._client.models.generate_content(  # type: ignore[union-attr]
                model=self._model_name,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=_SYSTEM_INSTRUCTION,
                    max_output_tokens=self._max_tokens,
                    temperature=0.7,
                ),
            )

            elapsed = time.perf_counter() - t_start
            logger.info("[GeminiProvider] Request completed — %.2fs", elapsed)

            return self._extract_text(response)

        except Exception as exc:  # noqa: BLE001
            elapsed = time.perf_counter() - t_start
            return self._handle_error(exc, elapsed)

    def health_check(self) -> bool:
        """Ping the Gemini API with a minimal request to verify connectivity.

        Returns:
            True if the API responded successfully, False otherwise.
        """
        if not is_ai_enabled():
            logger.warning("[GeminiProvider] health_check skipped — no API key.")
            return False

        logger.info("[GeminiProvider] Running health check...")
        try:
            response = self.generate("Merhaba")
            ok = bool(response) and response not in (
                _ERR_NO_KEY, _ERR_NO_INTERNET, _ERR_INVALID_KEY,
                _ERR_RATE_LIMIT, _ERR_GENERIC,
            )
            logger.info("[GeminiProvider] Health check: %s", "OK" if ok else "FAIL")
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.error("[GeminiProvider] Health check exception: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(response: object) -> str:
        """Safely extract text content from a Gemini response object."""
        try:
            text = response.text  # type: ignore[union-attr]
            if text:
                return text.strip()
        except (AttributeError, ValueError):
            pass

        try:
            return response.candidates[0].content.parts[0].text.strip()  # type: ignore[union-attr]
        except (AttributeError, IndexError, TypeError):
            pass

        return _ERR_GENERIC

    @staticmethod
    def _handle_error(exc: Exception, elapsed: float) -> str:
        """Map an exception to a friendly Turkish error message and log it."""
        exc_str = str(exc).lower()

        logger.error(
            "[GeminiProvider] Error after %.2fs: %s: %s",
            elapsed,
            type(exc).__name__,
            exc,
        )

        if "api_key" in exc_str or "api key" in exc_str or "403" in exc_str:
            return _ERR_INVALID_KEY

        if "429" in exc_str or "quota" in exc_str or "rate" in exc_str:
            return _ERR_RATE_LIMIT

        if (
            "timeout" in exc_str
            or "timed out" in exc_str
            or "connection" in exc_str
            or "network" in exc_str
            or "unreachable" in exc_str
            or "name resolution" in exc_str
        ):
            return _ERR_NO_INTERNET

        return _ERR_GENERIC
