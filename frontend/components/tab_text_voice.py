"""
Tab 2: Text + Voice
=====================
Type a message, get a text response that's also read aloud.
Uses gTTS (Google Text-to-Speech) to generate audio.
"""

import io

import httpx
import streamlit as st

from components.waveform import render_waveform_mini

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


def render_text_voice_tab(clm_url: str, clm_connected: bool, active_provider: str):
    """Render the Text -> Voice tab."""

    st.markdown("Type a message. The AI responds in text **and reads it aloud**.")

    # Provider badge
    _show_provider_badge(active_provider)

    if not GTTS_AVAILABLE:
        st.warning("**gTTS not installed.** Run: `pip install gTTS`")

    if not clm_connected:
        st.warning("**Server not running.** Open a terminal and run:\n\n"
                   "```\npython clm_server/server.py\n```")
        return

    # Initialize history
    if "tab2_history" not in st.session_state:
        st.session_state.tab2_history = []

    # Display chat history
    for msg in st.session_state.tab2_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                if "provider" in msg:
                    provider_label = "Claude" if msg["provider"] == "claude" else "ChatGPT"
                    st.caption(f"{provider_label}  ·  {msg.get('latency_ms', '?')}ms")
                # Play audio if available
                if msg.get("audio_bytes"):
                    render_waveform_mini("playing")
                    st.audio(msg["audio_bytes"], format="audio/mp3")

    # Input area
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Message",
            key="tab2_input",
            label_visibility="collapsed",
            placeholder="Type your message...",
        )
    with col2:
        send = st.button("Send", key="tab2_send", use_container_width=True)

    if send and user_input:
        # Add user message
        st.session_state.tab2_history.append({"role": "user", "content": user_input})

        # Call the CLM server
        with st.spinner("Thinking..."):
            try:
                with httpx.Client(timeout=30) as client:
                    resp = client.post(
                        f"{clm_url}/chat",
                        json={"message": user_input, "emotions": []},
                    )
                    result = resp.json()

                response_text = result["response"]
                provider = result.get("llm_provider", active_provider)
                latency = result.get("latency_ms")

                # Generate audio
                audio_bytes = _text_to_audio(response_text)

                st.session_state.tab2_history.append({
                    "role": "assistant",
                    "content": response_text,
                    "provider": provider,
                    "latency_ms": latency,
                    "audio_bytes": audio_bytes,
                })
            except Exception as e:
                st.session_state.tab2_history.append({
                    "role": "assistant",
                    "content": f"Error: {e}",
                    "provider": active_provider,
                    "audio_bytes": None,
                })

        # Cap history to prevent memory bloat
        if len(st.session_state.tab2_history) > 50:
            st.session_state.tab2_history = st.session_state.tab2_history[-50:]

        st.rerun()


def _text_to_audio(text: str) -> bytes | None:
    """Convert text to MP3 audio bytes using gTTS. Returns None on failure."""
    if not GTTS_AVAILABLE:
        return None
    try:
        tts = gTTS(text=text, lang="en")
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


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
