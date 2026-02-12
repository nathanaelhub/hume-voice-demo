"""
Tab 1: Text Chat  (Atmos theme)
==================================
Simple text-to-text chat. Type a message, get a response.
Shows which LLM answered and how long it took.
"""

import httpx
import streamlit as st

from components.theme import provider_badge_html, PROVIDER_CONFIG, COLORS


def render_text_chat_tab(clm_url: str, clm_connected: bool, active_provider: str):
    """Render the Text -> Text chat tab."""

    st.markdown(
        f'<p style="font-family:\'Outfit\',sans-serif;color:{COLORS["text_secondary"]};">'
        f'Type a message and see how the AI responds.</p>',
        unsafe_allow_html=True,
    )

    # Provider badge
    st.markdown(
        f'<div style="margin-bottom:12px;">AI Brain: {provider_badge_html(active_provider)}</div>',
        unsafe_allow_html=True,
    )

    if not clm_connected:
        st.warning("**Server not running.** Open a terminal and run:\n\n"
                   "```\npython clm_server/server.py\n```")
        return

    # Initialize history
    if "tab1_history" not in st.session_state:
        st.session_state.tab1_history = []

    # Display chat history
    for msg in st.session_state.tab1_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant" and "provider" in msg:
                badge = provider_badge_html(msg["provider"])
                latency = msg.get("latency_ms", "?")
                st.markdown(
                    f'{badge}'
                    f'<span style="font-family:\'IBM Plex Mono\',monospace;'
                    f'font-size:0.75rem;color:{COLORS["text_muted"]};'
                    f'margin-left:10px;">{latency}ms</span>',
                    unsafe_allow_html=True,
                )

    # Input area
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Message",
            key="tab1_input",
            label_visibility="collapsed",
            placeholder="Type your message...",
        )
    with col2:
        send = st.button("Send", key="tab1_send", use_container_width=True)

    if send and user_input:
        # Add user message to history
        st.session_state.tab1_history.append({"role": "user", "content": user_input})

        # Call the CLM server
        with st.spinner("Thinking..."):
            try:
                with httpx.Client(timeout=30) as client:
                    resp = client.post(
                        f"{clm_url}/chat",
                        json={"message": user_input, "emotions": []},
                    )
                    result = resp.json()

                st.session_state.tab1_history.append({
                    "role": "assistant",
                    "content": result["response"],
                    "provider": result.get("llm_provider", active_provider),
                    "latency_ms": result.get("latency_ms"),
                })
            except Exception as e:
                st.session_state.tab1_history.append({
                    "role": "assistant",
                    "content": f"Error: {e}",
                    "provider": active_provider,
                })

        st.rerun()
