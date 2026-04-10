"""
src/utils/security.py
─────────────────────────────────────────────────────────────────────
Input sanitisation and basic rate-limiting utilities.
"""

import re
import time
import streamlit as st
from config import AppConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SecurityUtils:
    """Lightweight security layer — sanitise + rate-limit."""

    # Patterns to strip from user input
    _STRIP_PATTERNS = [
        r"<[^>]+>",                   # HTML tags
        r"javascript:[^\s]*",         # JS injection
        r"(?i)(ignore previous|forget all instructions|jailbreak)",  # Prompt injection
    ]

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg

    # ── Input Sanitisation ────────────────────────────────────────────────────

    def sanitise(self, text: str) -> str:
        """Strip dangerous patterns and normalise whitespace."""
        for pattern in self._STRIP_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        # Collapse excess whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ── Rate Limiting ─────────────────────────────────────────────────────────

    def check_rate_limit(self) -> bool:
        """
        Simple in-session rate limiter.
        Returns True if the request is allowed, False if throttled.
        """
        now = time.time()
        window = 60  # 1-minute rolling window

        if "rate_timestamps" not in st.session_state:
            st.session_state.rate_timestamps = []

        # Purge timestamps outside the window
        st.session_state.rate_timestamps = [
            t for t in st.session_state.rate_timestamps if now - t < window
        ]

        if len(st.session_state.rate_timestamps) >= self.cfg.RATE_LIMIT_PER_MIN:
            logger.warning("Rate limit exceeded")
            return False

        st.session_state.rate_timestamps.append(now)
        return True

    # ── API Key Masking (for display / logs) ──────────────────────────────────

    @staticmethod
    def mask_key(key: str) -> str:
        if not key or len(key) < 8:
            return "***"
        return key[:4] + "…" + key[-4:]
