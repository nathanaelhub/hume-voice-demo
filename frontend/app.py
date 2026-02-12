"""
Voice AI Demo — Streamlit Frontend  (Atmos theme)
====================================================
Three demo modes + documentation tab.
Designed for non-technical students.

Run with:
    streamlit run frontend/app.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv

from components.theme import (
    inject_theme_css,
    hero_header_html,
    provider_card_html,
    status_dot_html,
    COLORS,
)
from components.llm_toggle import render_llm_toggle
from components.tab_text_chat import render_text_chat_tab
from components.tab_text_voice import render_text_voice_tab
from components.tab_voice_voice import render_voice_voice_tab
from components.tab_docs import render_docs_tab

load_dotenv()


# ---------------------------------------------------------------------------
# Auto-start CLM server (needed for Streamlit Cloud — single process env)
# ---------------------------------------------------------------------------

def _ensure_clm_server(clm_url: str):
    """Start the CLM backend as a subprocess if it isn't already running."""
    # Check if it's already up
    try:
        with httpx.Client(timeout=2) as client:
            resp = client.get(f"{clm_url}/")
            if resp.status_code == 200:
                return  # already running
    except Exception:
        pass

    # Find the server script relative to this file
    server_path = Path(__file__).resolve().parent.parent / "clm_server" / "server.py"
    if not server_path.exists():
        return  # can't find it, user will see "Offline" in sidebar

    # Launch as a background subprocess
    subprocess.Popen(
        [sys.executable, str(server_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Give it a moment to start
    for _ in range(10):
        time.sleep(0.5)
        try:
            with httpx.Client(timeout=1) as client:
                resp = client.get(f"{clm_url}/")
                if resp.status_code == 200:
                    return
        except Exception:
            continue


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
# Check CLM server (auto-start if needed)
# ---------------------------------------------------------------------------

clm_url = st.session_state.clm_url
_ensure_clm_server(clm_url)

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
# Inject Atmos theme
# ---------------------------------------------------------------------------

inject_theme_css(current_provider)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        f'<div style="font-family:\'Syne\',sans-serif;font-weight:700;'
        f'font-size:1.1rem;color:{COLORS["text"]};margin-bottom:12px;">'
        f'AI Provider</div>',
        unsafe_allow_html=True,
    )

    active_provider = render_llm_toggle(clm_url, current_provider)

    # Show both provider cards — active one glows
    st.markdown(
        provider_card_html("claude", active=(active_provider == "claude")),
        unsafe_allow_html=True,
    )
    st.markdown(
        provider_card_html("openai", active=(active_provider == "openai")),
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="height:1px;background:{COLORS["border"]};margin:16px 0;"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="font-family:\'Syne\',sans-serif;font-weight:700;'
        f'font-size:1.1rem;color:{COLORS["text"]};margin-bottom:8px;">'
        f'Server</div>',
        unsafe_allow_html=True,
    )
    st.markdown(status_dot_html(clm_connected), unsafe_allow_html=True)
    if not clm_connected:
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;'
            f'color:{COLORS["text_muted"]};margin-top:4px;">'
            f'Run: python clm_server/server.py</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="height:1px;background:{COLORS["border"]};margin:16px 0;"></div>',
        unsafe_allow_html=True,
    )

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

st.markdown(hero_header_html(), unsafe_allow_html=True)

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
