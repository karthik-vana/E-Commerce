"""
╔══════════════════════════════════════════════════════════════════╗
║        ShopMind AI — Production-Ready E-Commerce Chatbot         ║
║        Powered by Groq LPU Inference                             ║
╚══════════════════════════════════════════════════════════════════╝

Entry point for the Streamlit application.
All heavy logic is delegated to modular service layers.
"""

import time
import streamlit as st
from config import AppConfig
from src.services.session_service import SessionService
from src.services.chat_service import ChatService
from src.ui.components import UIComponents
from src.utils.logger import get_logger

# ─── Initialise ────────────────────────────────────────────────────────────────
logger = get_logger(__name__)
cfg    = AppConfig()

st.set_page_config(
    page_title=cfg.APP_TITLE,
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Bootstrap Services ────────────────────────────────────────────────────────
session_svc = SessionService()
chat_svc    = ChatService(cfg)
ui          = UIComponents(cfg)

# ─── Session State Init ────────────────────────────────────────────────────────
session_svc.init_session()

# ─── Inject CSS ────────────────────────────────────────────────────────────────
ui.inject_global_css()

# ─── Sidebar: Settings Panel ───────────────────────────────────────────────────
with st.sidebar:
    ui.render_sidebar(session_svc)

# ─── Main Chat Area ────────────────────────────────────────────────────────────
ui.render_header(session_svc)
ui.render_chat_history(st.session_state.messages)

# ─── Chat Input & Quick Actions ──────────────────────────────────────────────────
prompt = st.chat_input("Ask me about products, orders, returns…", key="chat_input")
if "_quick_action" in st.session_state and st.session_state["_quick_action"]:
    prompt = st.session_state["_quick_action"]
    st.session_state["_quick_action"] = None

if prompt:
    logger.info(f"User message received — session={st.session_state.session_id}")

    # Append user turn
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=cfg.USER_AVATAR):
        st.markdown(prompt)

    # Generate + stream assistant response with timing
    with st.chat_message("assistant", avatar=cfg.BOT_AVATAR):
        with st.spinner("ShopMind is thinking…"):
            start_time = time.time()
            response_text = chat_svc.get_response(
                user_message=prompt,
                history=st.session_state.messages[:-1],
                settings=st.session_state.settings,
            )
            elapsed = time.time() - start_time
            st.session_state.last_response_time = elapsed
        st.markdown(response_text)
        st.markdown(
            f'<div class="resp-time">⚡ {elapsed:.2f}s</div>',
            unsafe_allow_html=True,
        )

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    logger.info(f"Response delivered — {elapsed:.2f}s — tokens≈{len(response_text.split())}")
