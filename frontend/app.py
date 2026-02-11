"""
Voice AI Demo — Streamlit Frontend
=====================================
Three demo modes + documentation tab.
Designed for non-technical students.

Run with:
    streamlit run frontend/app.py
"""

import os

import httpx
import streamlit as st
from dotenv import load_dotenv

from components.llm_toggle import render_llm_toggle
from components.tab_text_chat import render_text_chat_tab
from components.tab_text_voice import render_text_voice_tab
from components.tab_voice_voice import render_voice_voice_tab
from components.tab_docs import render_docs_tab

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Voice AI Demo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .main-header { text-align: center; padding: 0.5rem 0 1rem 0; }
    .main-header h1 { font-size: 1.8rem; margin-bottom: 0.25rem; }
    .main-header p { color: #6B7280; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

defaults = {
    "clm_url": os.getenv("CLM_URL", "http://localhost:8000"),
    "active_provider": "claude",
    "tab1_history": [],
    "tab2_history": [],
    "tab3_history": [],
    "pipeline_state": {
        "stage": "idle", "transcript": "", "response": "",
        "emotions": [], "latency_ms": None,
    },
    "voice_history": [],
    "voice_stage": "idle",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------------------------
# Check CLM server
# ---------------------------------------------------------------------------

clm_url = st.session_state.clm_url
clm_connected = False
clm_info = {}
try:
    with httpx.Client(timeout=2) as client:
        resp = client.get(f"{clm_url}/")
        if resp.status_code == 200:
            clm_connected = True
            clm_info = resp.json()
except Exception:
    pass

current_provider = clm_info.get("llm_provider", st.session_state.active_provider)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## AI Brain")
    active_provider = render_llm_toggle(clm_url, current_provider)

    st.divider()

    st.markdown("## Server")
    if clm_connected:
        st.success("Connected")
    else:
        st.error("Offline")
        st.caption("Run: `python clm_server/server.py`")

    st.divider()

    if st.button("Clear All Chats", use_container_width=True):
        st.session_state.tab1_history = []
        st.session_state.tab2_history = []
        st.session_state.tab3_history = []
        st.session_state.voice_history = []
        try:
            with httpx.Client(timeout=2) as client:
                client.post(f"{clm_url}/reset")
        except Exception:
            pass
        st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="main-header">
    <h1>Voice AI Demo</h1>
    <p>Explore how AI understands and responds to language</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Text Chat",
    "Text + Voice",
    "Voice to Voice",
    "Documentation",
])

with tab1:
    render_text_chat_tab(clm_url, clm_connected, active_provider)

with tab2:
    render_text_voice_tab(clm_url, clm_connected, active_provider)

with tab3:
    render_voice_voice_tab(
        clm_url,
        clm_connected,
        st.session_state.pipeline_state,
        st.session_state.voice_history,
    )

with tab4:
    render_docs_tab()
