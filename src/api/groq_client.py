"""
src/api/groq_client.py
─────────────────────────────────────────────────────────────────────
Low-level Groq REST client (OpenAI-compatible endpoint).
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

class GroqResponse:
    """Typed wrapper around raw Groq API JSON."""

    def __init__(self, raw: dict):
        self._raw = raw

    @property
    def text(self) -> str:
        try:
            return self._raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return ""

    @property
    def finish_reason(self) -> str:
        try:
            return self._raw["choices"][0].get("finish_reason", "unknown")
        except (KeyError, IndexError):
            return "unknown"

    @property
    def usage(self) -> dict:
        return self._raw.get("usage", {})

    def is_valid(self) -> bool:
        return bool(self.text)


# ─── Client ───────────────────────────────────────────────────────────────────

class GroqClient:
    """
    Wraps the Groq chat completions endpoint (OpenAI-compatible).

    Usage
    ─────
    client = GroqClient(api_key="…", model="llama-3.3-70b-versatile")
    resp   = client.generate(messages=[…], system_prompt="…")
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
        retry_delay: float = 1.0,
    ):
        self.api_key     = api_key
        self.model       = model
        self.base_url    = base_url
        self.timeout     = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    # ── Public ────────────────────────────────────────────────────────────────

    def generate(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        temperature: float  = 0.7,
        max_tokens:  int    = 1024,
        top_p:       float  = 0.95,
    ) -> GroqResponse:
        """
        Call Groq and return a typed response.
        Retries up to `max_retries` times with exponential back-off.
        Returns a fallback GroqResponse on total failure.
        """
        payload = self._build_payload(
            self.model, messages, system_prompt, temperature, max_tokens, top_p
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Groq request — attempt {attempt}/{self.max_retries} "
                    f"model={self.model}"
                )
                raw = self._post(payload)
                resp = GroqResponse(raw)

                if resp.is_valid():
                    tokens = resp.usage.get("total_tokens", "?")
                    logger.info(
                        f"Groq success — finish={resp.finish_reason} tokens={tokens}"
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

        logger.error("All Groq retries exhausted — returning fallback")
        return GroqResponse(
            {"choices": [{"message": {"content": self.FALLBACK_MESSAGE}}]}
        )

    # ── Private ───────────────────────────────────────────────────────────────

    def _post(self, payload: dict) -> dict:
        resp = requests.post(
            self.base_url,
            json=payload,
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _build_payload(
        model: str,
        messages: list[dict],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        top_p: float,
    ) -> dict:
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        return {
            "model":       model,
            "messages":    all_messages,
            "temperature": temperature,
            "max_tokens":  max_tokens,
            "top_p":       top_p,
            "stream":      False,
        }

