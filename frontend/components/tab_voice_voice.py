"""
Tab 3: Voice to Voice
=======================
Record your voice → AI transcribes → thinks → speaks back.
Uses Streamlit's native audio input for reliable mic access,
Python SpeechRecognition for STT, and gTTS for TTS.
"""

import hashlib
import io

import httpx
import streamlit as st

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


def render_voice_voice_tab(
    clm_url: str,
    clm_connected: bool,
    pipeline_state: dict,
    history: list[dict],
):
    """Render the Voice to Voice tab."""

    if not clm_connected:
        st.warning("**Server not running.** Run: `python clm_server/server.py`")
        return

    if not SR_AVAILABLE:
        st.warning("**SpeechRecognition not installed.** Run: `pip install SpeechRecognition`")
        return

    provider = st.session_state.get("active_provider", "claude")
    provider_color = "#7C3AED" if provider == "claude" else "#10A37F"
    provider_name = "Claude" if provider == "claude" else "ChatGPT"

    stage = st.session_state.get("voice_stage", "idle")

    # ---- Waveform + status ----
    _render_waveform_header(stage, provider_name, provider_color)

    # ---- Record button ----
    st.markdown("")
    audio_data = st.audio_input(
        "Tap to record, tap again to stop",
        key="voice_recorder",
    )

    # ---- Process new recording ----
    if audio_data is not None:
        # Hash audio bytes to detect genuinely new recordings
        audio_data.seek(0)
        audio_hash = hashlib.md5(audio_data.read()).hexdigest()
        audio_data.seek(0)

        if audio_hash != st.session_state.get("_last_audio_hash"):
            st.session_state["_last_audio_hash"] = audio_hash
            _process_voice(audio_data, clm_url, provider_name, provider_color, history)

    # ---- Conversation subtitles ----
    _render_subtitles(history, provider_color)


# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------

def _process_voice(
    audio_data,
    clm_url: str,
    provider_name: str,
    provider_color: str,
    history: list[dict],
):
    """Pipeline: STT → CLM → TTS → playback, with live status updates."""

    with st.status("Processing your voice...", expanded=True) as status:

        # Step 1 — Transcribe
        st.write("Transcribing audio...")
        recognizer = sr.Recognizer()
        try:
            audio_data.seek(0)
            with sr.AudioFile(audio_data) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            status.update(label="Couldn't understand", state="error")
            st.warning("Couldn't understand the audio. Try speaking louder or closer to the mic.")
            return
        except sr.RequestError as e:
            status.update(label="STT service error", state="error")
            st.error(f"Speech recognition service error: {e}")
            return
        except Exception as e:
            status.update(label="Transcription failed", state="error")
            st.error(f"Transcription error: {e}")
            return

        st.write(f'You said: **"{text}"**')

        # Step 2 — Send to AI
        st.write(f"Asking {provider_name}...")
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{clm_url}/chat",
                    json={"message": text, "emotions": []},
                )
                data = resp.json()
        except Exception as e:
            status.update(label="Server error", state="error")
            st.error(f"Server error: {e}")
            history.append({"user": text, "ai": f"Error: {e}", "provider": provider_name, "latency_ms": 0})
            return

        response_text = data.get("response", "No response")
        latency = data.get("latency_ms", "?")
        st.write(f"{provider_name}: *{response_text}*")

        # Step 3 — Generate speech
        st.write("Generating speech...")
        audio_bytes = _text_to_audio(response_text)

        status.update(label="Done!", state="complete")

    # Save to history
    history.append({
        "user": text,
        "ai": response_text,
        "provider": provider_name,
        "latency_ms": latency,
        "audio": audio_bytes,
    })

    # Cap history
    if len(history) > 30:
        del history[:len(history) - 30]


def _text_to_audio(text: str) -> bytes | None:
    """Convert text to MP3 bytes via gTTS."""
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


# ---------------------------------------------------------------------------
# Subtitles display
# ---------------------------------------------------------------------------

def _render_subtitles(history: list[dict], provider_color: str):
    """Render the conversation as subtitles below the waveform."""

    if not history:
        st.caption("Your conversation will appear here.")
        return

    for entry in history:
        # User message — right-aligned, blue
        st.markdown(
            f"""<div style="text-align:right; margin-bottom:4px;">
                <span style="font-size:0.7rem; color:#6B7280; text-transform:uppercase;
                    letter-spacing:1px;">You said</span><br>
                <span style="color:#93C5FD; font-size:1rem;">{entry['user']}</span>
            </div>""",
            unsafe_allow_html=True,
        )

        # AI response — left-aligned, provider color
        st.markdown(
            f"""<div style="text-align:left; margin-bottom:12px;">
                <span style="font-size:0.7rem; color:#6B7280; text-transform:uppercase;
                    letter-spacing:1px;">{entry['provider']} says</span><br>
                <span style="color:{provider_color}; font-size:1rem;">{entry['ai']}</span>
                <span style="font-size:0.7rem; color:#4B5563; margin-left:8px;">
                    {entry.get('latency_ms', '?')}ms</span>
            </div>""",
            unsafe_allow_html=True,
        )

        # Auto-play the latest response audio
        if entry.get("audio") and entry is history[-1]:
            st.audio(entry["audio"], format="audio/mp3", autoplay=True)


# ---------------------------------------------------------------------------
# Waveform header (CSS animated, no JS/iframe needed)
# ---------------------------------------------------------------------------

def _render_waveform_header(stage: str, provider_name: str, provider_color: str):
    """Render an animated waveform with stage-based colors."""

    stages = {
        "idle":         {"color": "#4B5563", "label": "TAP RECORD TO START", "speed": "0s"},
        "transcribing": {"color": "#3B82F6", "label": "TRANSCRIBING...",     "speed": "0.6s"},
        "thinking":     {"color": "#F59E0B", "label": "THINKING...",         "speed": "1.0s"},
        "speaking":     {"color": "#10B981", "label": "SPEAKING...",         "speed": "0.35s"},
    }
    cfg = stages.get(stage, stages["idle"])
    color = cfg["color"]
    label = cfg["label"]
    speed = cfg["speed"]
    active = stage != "idle"

    # Build bars
    num_bars = 48
    bars = []
    for i in range(num_bars):
        center = num_bars / 2
        dist = abs(i - center) / center
        base_h = max(4, int(70 * (1 - dist ** 1.4)))

        if not active:
            h = max(3, int(base_h * 0.06))
            bars.append(
                f'<div style="width:3px;height:{h}px;background:{color}55;'
                f'border-radius:2px;transition:height 0.5s;"></div>'
            )
        else:
            min_h = max(3, int(base_h * 0.12))
            max_h = max(10, int(base_h * 0.9))
            delay = round((i / num_bars) * 0.8, 2)
            bars.append(
                f'<div style="width:3px;height:{max_h}px;background:{color};'
                f'border-radius:2px;'
                f'animation:vb{i} {speed} ease-in-out {delay}s infinite alternate;"></div>'
                f'<style>@keyframes vb{i}{{0%{{height:{min_h}px;opacity:.5}}'
                f'100%{{height:{max_h}px;opacity:1}}}}</style>'
            )

    glow = (
        f'<div style="position:absolute;top:50%;left:50%;'
        f'transform:translate(-50%,-50%);width:220px;height:220px;'
        f'background:radial-gradient(circle,{color}22,{color}00);'
        f'border-radius:50%;pointer-events:none;"></div>'
        if active else ""
    )

    dot = (
        f'<span style="display:inline-block;width:8px;height:8px;'
        f'background:{color};border-radius:50%;margin-right:8px;'
        f'animation:gdot 1s infinite;"></span>'
        if active else ""
    )

    html = f"""
    <div style="background:#0f0f1f;border-radius:16px;padding:20px 28px;
        margin:0 0 8px 0;text-align:center;position:relative;overflow:hidden;">
        {glow}
        <div style="color:{color};font-size:0.8rem;font-weight:600;
            letter-spacing:2px;margin-bottom:14px;position:relative;">
            {dot}{label}
        </div>
        <div style="display:flex;align-items:center;justify-content:center;
            gap:2px;height:90px;position:relative;">
            {''.join(bars)}
        </div>
        <div style="margin-top:12px;display:inline-block;
            background:{provider_color}33;color:{provider_color};
            padding:3px 12px;border-radius:10px;font-size:0.72rem;
            font-weight:600;">
            {provider_name}
        </div>
    </div>
    <style>@keyframes gdot{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}</style>
    """
    st.markdown(html, unsafe_allow_html=True)
