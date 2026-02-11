"""
Tab 1: Text Chat
==================
Simple text-to-text chat. Type a message, get a response.
Shows which LLM answered and how long it took.
"""

import httpx
import streamlit as st


def render_text_chat_tab(clm_url: str, clm_connected: bool, active_provider: str):
    """Render the Text -> Text chat tab."""

    st.markdown("Type a message and see how the AI responds.")

    # Provider badge
    _show_provider_badge(active_provider)

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
                provider_label = "Claude" if msg["provider"] == "claude" else "ChatGPT"
                st.caption(f"{provider_label}  ·  {msg.get('latency_ms', '?')}ms")

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


def _show_provider_badge(provider: str):
    if provider == "claude":
        st.markdown(
            'AI Brain: <span style="background:#7C3AED; color:white; '
            'padding:2px 10px; border-radius:10px; font-size:0.85rem; '
            'font-weight:600;">Claude</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            'AI Brain: <span style="background:#10A37F; color:white; '
            'padding:2px 10px; border-radius:10px; font-size:0.85rem; '
            'font-weight:600;">ChatGPT</span>',
            unsafe_allow_html=True,
        )
