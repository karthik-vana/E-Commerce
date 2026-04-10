"""
src/api/gemini_client.py
─────────────────────────────────────────────────────────────────────
Low-level Gemini REST client.
• Structured request / response handling
• Timeout, retry & exponential back-off
• Fallback response on repeated failure
• Full logging at every stage
"""

import time
import requests
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

# ─── Response Schema ───────────────────────────────────────────────────────────

class GeminiResponse:
    """Typed wrapper around raw Gemini API JSON."""

    def __init__(self, raw: dict):
        self._raw = raw

    @property
    def text(self) -> str:
        try:
            return (
                self._raw["candidates"][0]["content"]["parts"][0]["text"]
            )
        except (KeyError, IndexError):
            return ""

    @property
    def finish_reason(self) -> str:
        try:
            return self._raw["candidates"][0].get("finishReason", "UNKNOWN")
        except (KeyError, IndexError):
            return "UNKNOWN"

    @property
    def usage(self) -> dict:
        return self._raw.get("usageMetadata", {})

    def is_valid(self) -> bool:
        return bool(self.text)


# ─── Client ───────────────────────────────────────────────────────────────────

class GeminiClient:
    """
    Wraps Google Gemini generateContent endpoint.

    Usage
    ─────
    client = GeminiClient(api_key="…", model="gemini-1.5-flash")
    resp   = client.generate(contents=[…], system_instruction="…")
    print(resp.text)
    """

    FALLBACK_MESSAGE = (
        "I'm having trouble connecting right now. "
        "Please try again in a moment, or contact our support team."
    )

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout: int       = 30,
        max_retries: int   = 3,
        retry_delay: float = 1.5,
    ):
        self.api_key     = api_key
        self.model       = model
        self.timeout     = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._endpoint   = (
            f"{base_url}/models/{model}:generateContent?key={api_key}"
        )

    # ── Public ────────────────────────────────────────────────────────────────

    def generate(
        self,
        contents: list[dict],
        system_instruction: Optional[str] = None,
        temperature: float  = 0.7,
        max_tokens:  int    = 1024,
        top_p:       float  = 0.95,
        top_k:       int    = 40,
    ) -> GeminiResponse:
        """
        Call Gemini and return a typed response.
        Retries up to `max_retries` times with exponential back-off.
        Returns a fallback GeminiResponse on total failure.
        """
        payload = self._build_payload(
            contents, system_instruction, temperature, max_tokens, top_p, top_k
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Gemini request — attempt {attempt}/{self.max_retries} "
                    f"model={self.model}"
                )
                raw = self._post(payload)
                resp = GeminiResponse(raw)

                if resp.is_valid():
                    tokens = resp.usage.get("totalTokenCount", "?")
                    logger.info(
                        f"Gemini success — finish={resp.finish_reason} tokens={tokens}"
                    )
                    return resp

                logger.warning(f"Empty response body on attempt {attempt}")

            except requests.Timeout:
                logger.error(f"Timeout on attempt {attempt}")
            except requests.HTTPError as exc:
                logger.error(f"HTTP {exc.response.status_code} on attempt {attempt}: {exc}")
                if exc.response.status_code in (400, 401, 403):
                    break   # Non-retryable
            except Exception as exc:
                logger.error(f"Unexpected error on attempt {attempt}: {exc}", exc_info=True)

            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.info(f"Retrying in {delay:.1f}s…")
                time.sleep(delay)

        logger.error("All Gemini retries exhausted — returning fallback")
        return GeminiResponse(
            {"candidates": [{"content": {"parts": [{"text": self.FALLBACK_MESSAGE}]}}]}
        )

    # ── Private ───────────────────────────────────────────────────────────────

    def _post(self, payload: dict) -> dict:
        resp = requests.post(
            self._endpoint,
            json=payload,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _build_payload(
        contents: list[dict],
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: int,
        top_p: float,
        top_k: int,
    ) -> dict:
        payload: dict = {
            "contents": contents,
            "generationConfig": {
                "temperature":    temperature,
                "maxOutputTokens": max_tokens,
                "topP":           top_p,
                "topK":           top_k,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        return payload
