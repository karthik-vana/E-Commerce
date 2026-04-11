"""
src/ui/components.py
─────────────────────────────────────────────────────────────────────
All Streamlit UI rendering lives here.
• Global CSS injection (premium dark theme with glassmorphism)
• Header with clear-chat top-right
• Sidebar settings with tabbed layout
• Chat history renderer with timestamps
• Quick-action chips
• Tools panel with presets, stats, word counter
• About section
"""

import time as _time
import streamlit as st
from config import AppConfig, GROQ_MODELS
from src.prompts.ecommerce_prompts import PERSONAS
from src.services.session_service import SessionService


LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Kannada",
    "Bengali", "Marathi", "Spanish", "French", "Arabic",
    "German", "Japanese", "Korean", "Portuguese",
]

RESPONSE_STYLES = {
    "detailed": "Detailed",
    "concise":  "Concise",
    "bullet":   "Bullet Points",
}

QUICK_ACTIONS = [
    ("Today's deals",        "flash-sale"),
    ("Track my order",        "tracking"),
    ("Return policy",         "returns"),
    ("Top rated products",    "top-rated"),
    ("Gift ideas under $50",  "gifts"),
    ("Payment methods",       "payments"),
    ("Compare products",      "compare"),
    ("Shipping info",         "shipping"),
]


class UIComponents:
    """All Streamlit render methods. Keeps app.py clean."""

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg

    # ══════════════════════════════════════════════════════════════════════════
    #  CSS — Premium Dark Theme
    # ══════════════════════════════════════════════════════════════════════════

    def inject_global_css(self) -> None:
        st.markdown("""
<style>
/* ── Google Fonts ──────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ──────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

/* ── App Background ────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0c0f1a 0%, #121829 25%, #0f172a 50%, #1a1040 75%, #0c0f1a 100%);
    background-size: 400% 400%;
    animation: gradientShift 20s ease infinite;
    background-attachment: fixed;
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Brand Header ──────────────────────────────── */
.brand-header {
    background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(168,85,247,0.08) 50%, rgba(59,130,246,0.06) 100%);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 20px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
}
.brand-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(99,102,241,0.05) 0%, transparent 60%);
    animation: headerGlow 8s ease-in-out infinite;
}
@keyframes headerGlow {
    0%, 100% { transform: translate(0, 0); }
    50%      { transform: translate(10%, 10%); }
}
.shop-header {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.4rem;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin: 0;
    line-height: 1.2;
    position: relative;
    z-index: 1;
}
.shop-sub {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 4px;
    letter-spacing: 0.3px;
    font-weight: 300;
    position: relative;
    z-index: 1;
}
.shop-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    color: #a5b4fc;
    font-weight: 500;
    margin-top: 8px;
    position: relative;
    z-index: 1;
}

/* ── Clear Chat Floating Button ────────────────── */
.clear-btn-wrap {
    position: relative;
    z-index: 10;
    text-align: right;
}

/* ── Status Pill ───────────────────────────────── */
.status-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 20px; padding: 5px 14px;
    font-size: 0.78rem; color: #10b981; font-weight: 500;
}
.status-dot {
    width: 7px; height: 7px;
    background: #10b981; border-radius: 50%;
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    50%      { opacity: 0.6; box-shadow: 0 0 0 6px rgba(16,185,129,0); }
}

/* ── Chat messages ──────────────────────────────── */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.5rem !important;
    margin-bottom: 0.8rem !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    backdrop-filter: blur(16px);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
[data-testid="stChatMessage"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
    border-color: rgba(99, 102, 241, 0.12) !important;
}

/* ── Input box ──────────────────────────────────── */
[data-testid="stChatInputContainer"] {
    background: rgba(30, 41, 59, 0.85) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-radius: 16px !important;
    padding: 8px 12px !important;
    backdrop-filter: blur(14px);
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
}

/* ── Sidebar ────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(12,15,26,0.98) 0%, rgba(15,23,42,0.98) 100%) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.1) !important;
    backdrop-filter: blur(24px);
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem !important; }

/* ── Metric cards ───────────────────────────────── */
[data-testid="metric-container"] {
    background: rgba(99, 102, 241, 0.06) !important;
    border: 1px solid rgba(99, 102, 241, 0.12) !important;
    border-radius: 12px !important;
    padding: 0.8rem !important;
    transition: all 0.3s ease;
}
[data-testid="metric-container"]:hover {
    background: rgba(99, 102, 241, 0.1) !important;
}

/* ── Buttons ────────────────────────────────────── */
.stButton > button {
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1px solid rgba(99, 102, 241, 0.18) !important;
    border-radius: 12px !important;
    color: #c7d2fe !important;
    font-size: 0.82rem !important;
    padding: 10px 16px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-family: 'Inter', sans-serif !important;
    width: 100% !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border-color: #6366f1 !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3) !important;
}

/* ── Sliders & selects ──────────────────────────── */
[data-testid="stSlider"] [data-testid="stThumbValue"] { color: #a5b4fc !important; }
.stSelectbox [data-baseweb="select"] {
    background: rgba(15, 23, 42, 0.85) !important;
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}

/* ── Expander / Tabs ────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: rgba(255, 255, 255, 0.02);
    border-radius: 12px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; color: #94a3b8 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important; padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.15) !important;
    color: #a5b4fc !important;
}

/* ── Dividers & Scrollbar ──────────────────────── */
hr { border-color: rgba(99, 102, 241, 0.08) !important; margin: 1.2rem 0 !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.4); }

/* ── Sidebar section headers ───────────────────── */
.sidebar-heading {
    font-family: 'Outfit', sans-serif; font-weight: 600;
    color: #e2e8f0; font-size: 1.15rem; margin-bottom: 0.3rem; letter-spacing: 0.5px;
}
.sidebar-section {
    font-family: 'Outfit', sans-serif; font-weight: 500;
    color: #a5b4fc; font-size: 0.82rem; margin-bottom: 0.3rem;
    letter-spacing: 0.6px; text-transform: uppercase;
}
.sidebar-divider {
    border: none; border-top: 1px solid rgba(99, 102, 241, 0.1); margin: 0.8rem 0;
}

/* ── Model info card ───────────────────────────── */
.model-card {
    background: rgba(99, 102, 241, 0.06);
    border: 1px solid rgba(99, 102, 241, 0.15);
    border-radius: 12px; padding: 0.7rem 1rem; margin-top: 0.4rem;
}
.model-name {
    color: #c7d2fe; font-weight: 600; font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
}
.model-desc {
    color: #94a3b8; font-size: 0.75rem; margin-top: 2px;
}

/* ── About section ─────────────────────────────── */
.about-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(168,85,247,0.05) 100%);
    border: 1px solid rgba(99, 102, 241, 0.12);
    border-radius: 16px; padding: 1.3rem; margin-top: 0.4rem;
}
.about-title {
    font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.2rem;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
}
.about-text {
    color: #94a3b8; font-size: 0.85rem; line-height: 1.65;
}
.about-text strong { color: #c7d2fe; }
.feature-chip {
    display: inline-block;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.72rem; color: #a5b4fc;
    margin: 2px 3px 2px 0; font-weight: 500;
}
.tech-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: 6px; padding: 2px 8px;
    font-size: 0.7rem; color: #6ee7b7;
    margin: 2px 3px 2px 0;
    font-family: 'JetBrains Mono', monospace; font-weight: 500;
}

/* ── Welcome screen ─────────────────────────────── */
.welcome-container { text-align: center; padding: 2.5rem 0 1.5rem 0; }
.welcome-icon {
    font-size: 3.5rem; margin-bottom: 0.8rem; display: inline-block;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%      { transform: translateY(-8px); }
}
.welcome-title {
    font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
}
.welcome-sub { color: #94a3b8; font-size: 1rem; margin-bottom: 1.5rem; }
.welcome-grid {
    display: grid; grid-template-columns: repeat(2, 1fr);
    gap: 10px; max-width: 480px; margin: 0 auto;
}
.welcome-card {
    background: rgba(99, 102, 241, 0.06);
    border: 1px solid rgba(99, 102, 241, 0.12);
    border-radius: 14px; padding: 1rem; text-align: left;
    transition: all 0.3s ease;
}
.welcome-card:hover {
    background: rgba(99, 102, 241, 0.1);
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.25);
}
.wc-icon { font-size: 1.3rem; margin-bottom: 4px; }
.wc-title { color: #c7d2fe; font-weight: 600; font-size: 0.88rem; margin-bottom: 3px; }
.wc-desc { color: #64748b; font-size: 0.75rem; }

/* ── Response time badge ───────────────────────── */
.resp-time {
    display: inline-flex; align-items: center; gap: 4px;
    color: #64748b; font-size: 0.7rem; margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Sidebar footer ─────────────────────────────── */
.sidebar-footer {
    text-align: center; color: #475569; font-size: 0.72rem;
    margin-top: 1.5rem; padding: 0.8rem;
    border-top: 1px solid rgba(99, 102, 241, 0.08);
}
.sidebar-footer strong { color: #6366f1; font-family: 'Outfit', sans-serif; }
</style>
""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  Header — with Clear Chat top-right
    # ══════════════════════════════════════════════════════════════════════════

    def render_header(self, session_svc: SessionService) -> None:
        # ── Top bar: Status + Clear Chat button ────────────────────
        top_left, top_right = st.columns([5, 1])
        with top_left:
            st.markdown(f"""
<div class="brand-header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.8rem;">
    <div>
      <h1 class="shop-header">ShopMind AI</h1>
      <p class="shop-sub">Your intelligent E-Commerce shopping assistant</p>
      <div class="shop-badge">Powered by Groq LPU &middot; v{self.cfg.APP_VERSION}</div>
    </div>
    <div style="padding-top:0.3rem;">
      <span class="status-pill"><span class="status-dot"></span>Online</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        with top_right:
            st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
            if st.button("Clear Chat", key="top_clear_chat", use_container_width=True):
                session_svc.reset()
                st.rerun()

        # ── Active model indicator ─────────────────────────────────
        current_model = st.session_state.settings.get("model", self.cfg.GROQ_MODEL)
        model_info = GROQ_MODELS.get(current_model, {})
        model_icon = model_info.get("icon", "🤖")
        model_label = model_info.get("label", current_model)
        st.caption(f"{model_icon} Active model: **{model_label}**")

        # ── Quick-action chips ─────────────────────────────────────
        st.markdown("---")
        cols = st.columns(4)
        for i, (action, _key) in enumerate(QUICK_ACTIONS):
            with cols[i % 4]:
                if st.button(action, key=f"qa_{i}", use_container_width=True):
                    st.session_state["_quick_action"] = action

    # ══════════════════════════════════════════════════════════════════════════
    #  Sidebar — Tabbed Layout
    # ══════════════════════════════════════════════════════════════════════════

    def render_sidebar(self, session_svc: SessionService) -> None:
        st.markdown(
            '<div class="sidebar-heading">ShopMind AI</div>',
            unsafe_allow_html=True,
        )
        st.caption("Configure your shopping assistant")
        st.divider()

        tab_settings, tab_tools, tab_about = st.tabs(["Settings", "Tools", "About"])

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        #  TAB 1: Settings
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        with tab_settings:
            # ── Model Selection ────────────────────────────────────
            st.markdown('<div class="sidebar-section">AI Model</div>', unsafe_allow_html=True)
            model_keys = list(GROQ_MODELS.keys())
            current_model = st.session_state.settings.get("model", self.cfg.GROQ_MODEL)
            if current_model not in model_keys:
                current_model = model_keys[0]

            selected_model = st.selectbox(
                "Select Model",
                options=model_keys,
                format_func=lambda k: f"{GROQ_MODELS[k]['icon']} {GROQ_MODELS[k]['label']}",
                index=model_keys.index(current_model),
                key="model_selector",
            )
            session_svc.update_setting("model", selected_model)

            model_info = GROQ_MODELS[selected_model]
            st.markdown(f"""
<div class="model-card">
    <div class="model-name">{model_info["icon"]} {selected_model}</div>
    <div class="model-desc">{model_info["desc"]} &middot; {model_info["ctx"]//1000}K ctx</div>
</div>
""", unsafe_allow_html=True)

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── Persona & Language ─────────────────────────────────
            st.markdown('<div class="sidebar-section">Persona & Language</div>', unsafe_allow_html=True)
            persona_key = st.selectbox(
                "Bot Persona",
                options=list(PERSONAS.keys()),
                format_func=lambda k: f"{PERSONAS[k]['icon']} {PERSONAS[k]['label']}",
                index=list(PERSONAS.keys()).index(
                    st.session_state.settings.get("persona", "friendly")
                ),
            )
            session_svc.update_setting("persona", persona_key)
            st.caption(f"_{PERSONAS[persona_key]['tone'][:80]}..._")

            language = st.selectbox(
                "Response Language",
                LANGUAGES,
                index=LANGUAGES.index(
                    st.session_state.settings.get("language", "English")
                ),
            )
            session_svc.update_setting("language", language)

            response_style = st.selectbox(
                "Response Style",
                options=list(RESPONSE_STYLES.keys()),
                format_func=lambda k: RESPONSE_STYLES[k],
                index=list(RESPONSE_STYLES.keys()).index(
                    st.session_state.settings.get("response_style", "detailed")
                ),
            )
            session_svc.update_setting("response_style", response_style)

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── Store Branding ─────────────────────────────────────
            st.markdown('<div class="sidebar-section">Store Identity</div>', unsafe_allow_html=True)
            store_name = st.text_input(
                "Store Name",
                value=st.session_state.settings.get("store_name", "ShopMind Store"),
            )
            session_svc.update_setting("store_name", store_name)

            extra_ctx = st.text_area(
                "Extra Store Context (optional)",
                value=st.session_state.settings.get("extra_context") or "",
                placeholder="e.g. We sell electronics in India. No COD.",
                height=70,
            )
            session_svc.update_setting("extra_context", extra_ctx or None)

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── Generation Parameters ──────────────────────────────
            with st.expander("Advanced Parameters", expanded=False):
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0, max_value=2.0,
                    value=float(st.session_state.settings.get("temperature", 0.7)),
                    step=0.05,
                    help="Higher = more creative; Lower = more factual",
                )
                session_svc.update_setting("temperature", temperature)

                max_tokens = st.slider(
                    "Max Output Tokens",
                    min_value=128, max_value=4096,
                    value=int(st.session_state.settings.get("max_tokens", 1024)),
                    step=128,
                    help="Max length of the AI response",
                )
                session_svc.update_setting("max_tokens", max_tokens)

                top_p = st.slider(
                    "Top-P (Nucleus Sampling)",
                    min_value=0.1, max_value=1.0,
                    value=float(st.session_state.settings.get("top_p", 0.95)),
                    step=0.05,
                )
                session_svc.update_setting("top_p", top_p)

            # ── Safety & Memory ────────────────────────────────────
            with st.expander("Safety & Memory", expanded=False):
                few_shot = st.toggle(
                    "Few-shot examples",
                    value=st.session_state.settings.get("few_shot", True),
                    help="Prepend example Q&A to improve response quality",
                )
                session_svc.update_setting("few_shot", few_shot)

                content_filter_status = "Active" if self.cfg.ENABLE_CONTENT_FILTER else "Disabled"
                st.caption(f"Content filter: **{content_filter_status}**")
                st.caption(f"Max history turns: **{self.cfg.MAX_HISTORY_TURNS}**")
                st.caption(f"Rate limit: **{self.cfg.RATE_LIMIT_PER_MIN} req/min**")

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        #  TAB 2: Tools
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        with tab_tools:
            # ── Session Stats ──────────────────────────────────────
            st.markdown('<div class="sidebar-section">Session Statistics</div>', unsafe_allow_html=True)
            stats = session_svc.get_stats()
            c1, c2, c3 = st.columns(3)
            c1.metric("Turns", stats["turns"])
            c2.metric("Words", stats["total_words"])
            c3.metric("Session", stats["session_id"])

            # ── Response Time ──────────────────────────────────────
            if "last_response_time" in st.session_state:
                rt = st.session_state.last_response_time
                st.markdown(
                    f'<div class="resp-time">Last response: {rt:.2f}s</div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── Actions ────────────────────────────────────────────
            st.markdown('<div class="sidebar-section">🛠️ Actions</div>', unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Clear Chat", use_container_width=True, key="btn_clear"):
                    session_svc.reset()
                    st.rerun()
            with col_b:
                if st.button("Export Chat", use_container_width=True, key="btn_export"):
                    self._export_chat()

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── Visual Search ──────────────────────────────────────────────
            st.markdown('<div class="sidebar-section">Visual Search</div>', unsafe_allow_html=True)
            st.caption("Upload a product image to find matches")
            uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"], key="visual_search")
            if uploaded_file is not None:
                st.success("Visual search indexing soon...")

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── Quick Presets ──────────────────────────────────────
            st.markdown('<div class="sidebar-section">Quick Presets</div>', unsafe_allow_html=True)
            st.caption("Apply optimised settings instantly")

            preset_cols = st.columns(2)
            with preset_cols[0]:
                if st.button("Fast", use_container_width=True, key="preset_fast"):
                    session_svc.update_setting("model", "llama-3.1-8b-instant")
                    session_svc.update_setting("temperature", 0.5)
                    session_svc.update_setting("max_tokens", 512)
                    session_svc.update_setting("response_style", "concise")
                    st.rerun()
            with preset_cols[1]:
                if st.button("Quality", use_container_width=True, key="preset_quality"):
                    session_svc.update_setting("model", "llama-3.3-70b-versatile")
                    session_svc.update_setting("temperature", 0.7)
                    session_svc.update_setting("max_tokens", 2048)
                    session_svc.update_setting("response_style", "detailed")
                    st.rerun()

            preset_cols2 = st.columns(2)
            with preset_cols2[0]:
                if st.button("Expert", use_container_width=True, key="preset_expert"):
                    session_svc.update_setting("model", "llama-3.3-70b-versatile")
                    session_svc.update_setting("persona", "expert")
                    session_svc.update_setting("temperature", 0.4)
                    session_svc.update_setting("max_tokens", 2048)
                    st.rerun()
            with preset_cols2[1]:
                if st.button("Qwen", use_container_width=True, key="preset_qwen"):
                    session_svc.update_setting("model", "qwen/qwen3-32b")
                    session_svc.update_setting("persona", "qwen")
                    session_svc.update_setting("temperature", 0.6)
                    session_svc.update_setting("max_tokens", 1536)
                    st.rerun()

            preset_cols3 = st.columns(2)
            with preset_cols3[0]:
                if st.button("Creative", use_container_width=True, key="preset_creative"):
                    session_svc.update_setting("model", "mixtral-8x7b-32768")
                    session_svc.update_setting("persona", "friendly")
                    session_svc.update_setting("temperature", 1.2)
                    session_svc.update_setting("max_tokens", 1024)
                    st.rerun()
            with preset_cols3[1]:
                if st.button("Safe", use_container_width=True, key="preset_safe"):
                    session_svc.update_setting("model", "openai/gpt-oss-safeguard-20b")
                    session_svc.update_setting("persona", "professional")
                    session_svc.update_setting("temperature", 0.3)
                    session_svc.update_setting("max_tokens", 1024)
                    st.rerun()

            st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

            # ── All Models Reference ───────────────────────────────
            st.markdown('<div class="sidebar-section">Available Models</div>', unsafe_allow_html=True)
            for model_id, info in GROQ_MODELS.items():
                is_active = st.session_state.settings.get("model", self.cfg.GROQ_MODEL) == model_id
                indicator = "●" if is_active else "○"
                color = "#a5b4fc" if is_active else "#64748b"
                st.markdown(
                    f'<div style="color:{color};font-size:0.78rem;margin-bottom:5px;">'
                    f'{indicator} {info["icon"]} <strong>{info["label"]}</strong>'
                    f'<br/><span style="color:#475569;font-size:0.7rem;margin-left:1.4rem;">'
                    f'{info["desc"]}</span></div>',
                    unsafe_allow_html=True,
                )

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        #  TAB 3: About
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        with tab_about:
            st.markdown("""
<div class="about-card">
    <div class="about-title">About ShopMind AI</div>
    <div class="about-text">
        <strong>ShopMind AI</strong> is a production-grade, AI-powered e-commerce
        chatbot built to transform online shopping experiences. It uses a modular,
        service-oriented architecture to deliver intelligent product recommendations,
        instant order tracking, policy guidance, and personalised assistance.
        <br/><br/>
        Powered by <strong>Groq's LPU Inference Engine</strong> — the world's fastest
        AI inference platform — with access to <strong>9 state-of-the-art models</strong>
        including LLaMA 3.3, Qwen 3, Kimi K2, GPT OSS, Gemma 2, and Mixtral.
    </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("")

            st.markdown('<div class="sidebar-section">Key Features</div>', unsafe_allow_html=True)
            st.markdown("""
<div>
    <span class="feature-chip">Product Discovery</span>
    <span class="feature-chip">Order Tracking</span>
    <span class="feature-chip">Returns & Refunds</span>
    <span class="feature-chip">Price Comparison</span>
    <span class="feature-chip">14 Languages</span>
    <span class="feature-chip">6 Personas</span>
    <span class="feature-chip">9 AI Models</span>
    <span class="feature-chip">Quick Presets</span>
    <span class="feature-chip">Chat Export</span>
    <span class="feature-chip">Content Safety</span>
    <span class="feature-chip">Response Timer</span>
    <span class="feature-chip">Session Stats</span>
    <span class="feature-chip">Qwen Mode</span>
    <span class="feature-chip">Quick Clear</span>
</div>
""", unsafe_allow_html=True)

            st.markdown("")

            st.markdown('<div class="sidebar-section">Tech Stack</div>', unsafe_allow_html=True)
            st.markdown("""
<div>
    <span class="tech-badge">Python 3.11+</span>
    <span class="tech-badge">Streamlit</span>
    <span class="tech-badge">Groq API</span>
    <span class="tech-badge">LLaMA 3.3</span>
    <span class="tech-badge">Qwen 3</span>
    <span class="tech-badge">Kimi K2</span>
    <span class="tech-badge">Mixtral 8x7B</span>
    <span class="tech-badge">Gemma 2</span>
</div>
""", unsafe_allow_html=True)

            st.markdown("")

            st.markdown('<div class="sidebar-section">🏗️ Architecture</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="about-text" style="font-size:0.8rem;">
    <strong>Modular Design</strong> — Clean separation across service layers,
    API clients, prompt engineering, UI components, security, and logging.<br/><br/>
    <strong>Security</strong> — Input sanitisation, prompt injection defence,
    rate limiting, and domain-scoped content filtering.<br/><br/>
    <strong>Resilience</strong> — Exponential retry with back-off, graceful
    fallbacks, and structured error handling.<br/><br/>
    <strong>Performance</strong> — Client caching, minimal re-renders,
    dynamic model switching, and Groq LPU for sub-second inference.
</div>
""", unsafe_allow_html=True)

            st.markdown("")

            st.markdown('<div class="sidebar-section">Credits</div>', unsafe_allow_html=True)
            st.markdown("""
<div class="about-text" style="font-size:0.8rem;">
    A full-stack GenAI project showcasing modern conversational AI,
    advanced prompt engineering, multi-model orchestration, and
    production-ready deployment practices.
</div>
""", unsafe_allow_html=True)

        # ── Sidebar Footer ─────────────────────────────────────────
        st.markdown(
            '<div class="sidebar-footer">'
            '<strong>ShopMind AI</strong> v2.1<br/>'
            'Powered by Groq LPU Inference'
            '</div>',
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  Chat History
    # ══════════════════════════════════════════════════════════════════════════

    def render_chat_history(self, messages: list[dict]) -> None:
        if not messages:
            st.markdown("""
<div class="welcome-container">
  <div class="welcome-icon">🛒</div>
  <div class="welcome-title">Welcome to ShopMind AI</div>
  <div class="welcome-sub">Ask me anything about products, orders, deals, or returns</div>
  <div class="welcome-grid">
    <div class="welcome-card">
      <div class="wc-icon">🔍</div>
      <div class="wc-title">Product Discovery</div>
      <div class="wc-desc">Find the perfect product with smart recommendations</div>
    </div>
    <div class="welcome-card">
      <div class="wc-icon">📦</div>
      <div class="wc-title">Order Tracking</div>
      <div class="wc-desc">Get real-time updates on your purchases</div>
    </div>
    <div class="welcome-card">
      <div class="wc-icon">⚖️</div>
      <div class="wc-title">Price Comparison</div>
      <div class="wc-desc">Compare products side-by-side effortlessly</div>
    </div>
    <div class="welcome-card">
      <div class="wc-icon">↩️</div>
      <div class="wc-title">Returns & Refunds</div>
      <div class="wc-desc">Hassle-free guidance for returns and refunds</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
            return

        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # ══════════════════════════════════════════════════════════════════════════
    #  Export
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _export_chat() -> None:
        msgs = st.session_state.get("messages", [])
        if not msgs:
            st.warning("No messages to export.")
            return
        lines = []
        for m in msgs:
            prefix = "You" if m["role"] == "user" else "ShopMind"
            lines.append(f"[{prefix}]\n{m['content']}\n")
        st.download_button(
            label="Download .txt",
            data="\n".join(lines),
            file_name="shopmind_chat.txt",
            mime="text/plain",
        )
