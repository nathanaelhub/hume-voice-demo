"""
LLM Toggle Switch
===================
A light-switch style toggle to swap between Claude and ChatGPT.
"""

import httpx
import streamlit as st


def render_llm_toggle(clm_url: str, current_provider: str) -> str:
    """Render the Claude/ChatGPT toggle. Returns the active provider name."""

    if "active_provider" not in st.session_state:
        st.session_state.active_provider = current_provider

    use_chatgpt = st.toggle(
        "Use ChatGPT",
        value=(st.session_state.active_provider == "openai"),
        help="OFF = Claude (Anthropic)  |  ON = ChatGPT (OpenAI)",
    )

    desired = "openai" if use_chatgpt else "claude"

    # Only call the server if the toggle actually changed
    if desired != st.session_state.active_provider:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.post(f"{clm_url}/switch/{desired}")
                if resp.status_code == 200:
                    st.session_state.active_provider = desired
                    st.rerun()
        except Exception as e:
            st.error(f"Could not switch: {e}")

    # Visual badge
    provider = st.session_state.active_provider
    if provider == "claude":
        st.markdown(
            '<div style="background:#7C3AED; color:white; padding:8px 16px; '
            'border-radius:8px; text-align:center; font-weight:600; margin-top:4px;">'
            'Claude (Anthropic)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#10A37F; color:white; padding:8px 16px; '
            'border-radius:8px; text-align:center; font-weight:600; margin-top:4px;">'
            'ChatGPT (OpenAI)</div>',
            unsafe_allow_html=True,
        )

    return provider
