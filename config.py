"""
config.py
─────────────────────────────────────────────────────────────────────
Central, config-driven setup. All tunable values live here.
Reads secrets from Streamlit Cloud (st.secrets) or environment / .env.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present (local dev only)


def _get_secret(key: str, default: str = "") -> str:
    """Read a secret from Streamlit Cloud first, then fall back to env vars."""
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)


# ── Available Groq Models ──────────────────────────────────────────────────────
GROQ_MODELS = {
    "llama-3.3-70b-versatile": {
        "label": "LLaMA 3.3 70B Versatile",
        "desc":  "Best overall — fast, smart, great for detailed answers",
        "ctx":   128000,
        "icon":  "",
    },
    "llama-3.1-8b-instant": {
        "label": "LLaMA 3.1 8B Instant",
        "desc":  "Ultra-fast responses, great for quick queries",
        "ctx":   131072,
        "icon":  "",
    },
    "qwen/qwen3-32b": {
        "label": "Qwen 3 32B",
        "desc":  "Alibaba's Qwen 3 — excellent reasoning and multilingual",
        "ctx":   32768,
        "icon":  "",
    },
    "openai/gpt-oss-safeguard-20b": {
        "label": "GPT OSS Safeguard 20B",
        "desc":  "OpenAI open-source — safety-focused, reliable responses",
        "ctx":   16384,
        "icon":  "",
    },
    "moonshotai/kimi-k2-instruct-0905": {
        "label": "Kimi K2 Instruct",
        "desc":  "Moonshot AI — strong instruction following and creativity",
        "ctx":   131072,
        "icon":  "",
    },
    "gemma2-9b-it": {
        "label": "Gemma 2 9B IT",
        "desc":  "Google Gemma — instruction-tuned, solid performance",
        "ctx":   8192,
        "icon":  "",
    },
    "mixtral-8x7b-32768": {
        "label": "Mixtral 8x7B",
        "desc":  "Mixture-of-Experts — balanced speed and quality",
        "ctx":   32768,
        "icon":  "",
    },
    "llama3-70b-8192": {
        "label": "LLaMA 3 70B",
        "desc":  "Powerful 70B model with 8K context",
        "ctx":   8192,
        "icon":  "",
    },
    "llama3-8b-8192": {
        "label": "LLaMA 3 8B",
        "desc":  "Lightweight and fast, good for simple queries",
        "ctx":   8192,
        "icon":  "",
    },
}


@dataclass
class AppConfig:
    APP_TITLE: str  = "ShopMind AI"
    APP_ICON:  str  = "sm"
    APP_DESC:  str  = "Your intelligent E-Commerce shopping assistant"
    BOT_NAME:  str  = "ShopMind"
    BOT_AVATAR: str = "assets/bot.svg"
    USER_AVATAR: str = "assets/user.svg"
    APP_VERSION: str = "2.1"

    # ── Groq API ───────────────────────────────────────────────────
    GROQ_API_KEY: str  = field(default_factory=lambda: _get_secret("GROQ_API_KEY", ""))
    GROQ_MODEL:   str  = field(default_factory=lambda: _get_secret("GROQ_MODEL", "llama-3.3-70b-versatile"))
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"

    # ── Generation defaults ─────────────────────────────────────────
    DEFAULT_TEMPERATURE:  float = 0.7
    DEFAULT_MAX_TOKENS:   int   = 1024
    DEFAULT_TOP_P:        float = 0.95

    # ── Memory / Session ────────────────────────────────────────────
    MAX_HISTORY_TURNS:   int = 20   # keep last N turns in context
    SESSION_TIMEOUT_MIN: int = 30

    # ── Retry / Resilience ──────────────────────────────────────────
    MAX_RETRIES:     int   = 3
    RETRY_DELAY_SEC: float = 1.0
    REQUEST_TIMEOUT: int   = 30

    # ── Logging ─────────────────────────────────────────────────────
    LOG_LEVEL: str = field(default_factory=lambda: _get_secret("LOG_LEVEL", "INFO"))
    LOG_DIR:   str = "logs"
    LOG_FILE:  str = "logs/app.log"

    # ── Security ────────────────────────────────────────────────────
    MAX_INPUT_LENGTH:   int  = 2000
    RATE_LIMIT_PER_MIN: int  = 30
    ENABLE_CONTENT_FILTER: bool = True

    # ── Domain keywords for relevance guardrail ─────────────────────
    ALLOWED_TOPICS: list = field(default_factory=lambda: [
        # Shopping actions
        "product", "price", "buy", "purchase", "order", "cart", "checkout",
        "shop", "sell", "cost", "worth", "spend", "afford", "budget",
        "recommend", "suggest", "find", "search", "look", "want", "need",
        # Logistics
        "shipping", "delivery", "return", "refund", "exchange", "replace",
        "track", "dispatch", "package", "parcel", "arrive", "deliver",
        # Deals & payments
        "discount", "coupon", "sale", "offer", "promo", "deal", "cashback",
        "payment", "pay", "invoice", "emi", "installment", "cod",
        # Product attributes
        "review", "rating", "recommendation", "brand", "size", "color",
        "model", "spec", "feature", "quality", "material", "weight",
        "availability", "stock", "warranty", "guarantee", "genuine",
        # Product categories
        "phone", "laptop", "tablet", "camera", "headphone", "earbuds",
        "speaker", "watch", "tv", "monitor", "keyboard", "mouse",
        "shoe", "shirt", "dress", "bag", "accessori", "jewel",
        "furniture", "appliance", "kitchen", "gadget", "electronic",
        "toy", "book", "game", "sport", "fitness", "beauty", "skin",
        # Shopping concepts
        "gift", "wishlist", "compare", "best", "top", "cheap", "premium",
        "popular", "trending", "new", "latest", "under", "above",
    ])

    def validate(self) -> None:
        """Raise early if critical config is missing."""
        if not self.GROQ_API_KEY:
            raise EnvironmentError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file or environment variables."
            )
