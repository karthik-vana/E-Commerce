"""
src/services/session_service.py
─────────────────────────────────────────────────────────────────────
Handles Streamlit session-state lifecycle:
• Initialise on first load
• Unique session IDs
• Clean reset
• Settings persistence
"""

import copy
import uuid
import streamlit as st
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    """Manages all st.session_state keys for the chatbot."""

    DEFAULTS = {
        "messages":   [],
        "settings": {
            "model":          "llama-3.3-70b-versatile",
            "persona":        "friendly",
            "language":       "English",
            "response_style": "detailed",
            "temperature":    0.7,
            "max_tokens":     1024,
            "top_p":          0.95,
            "few_shot":       True,
            "store_name":     "ShopMind Store",
            "extra_context":  None,
        },
    }

    def init_session(self) -> None:
        """Called once on app load — sets defaults if not already set."""
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.started_at = datetime.utcnow().isoformat()
            logger.info(f"New session — id={st.session_state.session_id}")

        for key, value in self.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = copy.deepcopy(value)

    def reset(self) -> None:
        """Clear conversation history but preserve settings."""
        st.session_state.messages   = []
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.started_at = datetime.utcnow().isoformat()
        logger.info(f"Session reset — new id={st.session_state.session_id}")

    def update_setting(self, key: str, value) -> None:
        st.session_state.settings[key] = value

    def get_stats(self) -> dict:
        msgs  = st.session_state.messages
        turns = sum(1 for m in msgs if m["role"] == "user")
        words = sum(len(m["content"].split()) for m in msgs)
        return {
            "session_id":  st.session_state.get("session_id", "—"),
            "started_at":  st.session_state.get("started_at", "—"),
            "turns":       turns,
            "total_words": words,
        }
