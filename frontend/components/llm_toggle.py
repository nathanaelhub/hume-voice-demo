"""
LLM Toggle Switch  (Atmos theme)
===================================
Side-by-side provider buttons to swap between Claude and ChatGPT.
"""

import httpx
import streamlit as st

from components.theme import PROVIDER_CONFIG, COLORS


def render_llm_toggle(clm_url: str, current_provider: str) -> str:
    """Render the Claude/ChatGPT toggle. Returns the active provider name."""

    if "active_provider" not in st.session_state:
        st.session_state.active_provider = current_provider

    active = st.session_state.active_provider
    cfg_c = PROVIDER_CONFIG["claude"]
    cfg_o = PROVIDER_CONFIG["openai"]

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            f"{'● ' if active == 'claude' else ''}{cfg_c['name']}",
            use_container_width=True,
            key="btn_claude",
        ):
            if active != "claude":
                _switch(clm_url, "claude")
    with col2:
        if st.button(
            f"{'● ' if active == 'openai' else ''}{cfg_o['name']}",
            use_container_width=True,
            key="btn_openai",
        ):
            if active != "openai":
                _switch(clm_url, "openai")

    return st.session_state.active_provider


def _switch(clm_url: str, provider: str):
    """Switch the backend provider and rerun."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.post(f"{clm_url}/switch/{provider}")
            if resp.status_code == 200:
                st.session_state.active_provider = provider
                st.session_state.pop("_hume_token", None)
                st.rerun()
    except Exception as e:
        st.error(f"Could not switch: {e}")
