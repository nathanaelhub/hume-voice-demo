"""
Tab 4: Documentation
======================
All setup guides, architecture info, and technical details.
Keeps the other tabs clean.
"""

import streamlit as st


def render_docs_tab():
    """Render the documentation tab."""

    st.markdown("### Getting Started")
    st.markdown("""
**1. Clone and install**
```bash
git clone <repo-url>
cd hume-voice-demo
pip install -r requirements.txt
```

**2. Add your API keys**
```bash
cp .env.example .env
```
Then edit `.env` and paste your keys:
- `ANTHROPIC_API_KEY` — from [console.anthropic.com](https://console.anthropic.com/)
- `OPENAI_API_KEY` — from [platform.openai.com](https://platform.openai.com/)
- `HUME_API_KEY` — from [platform.hume.ai](https://platform.hume.ai/) (optional, for advanced voice)

**3. Run it**
```bash
# Terminal 1: start the AI server
python clm_server/server.py

# Terminal 2: start the app
streamlit run frontend/app.py
```
""")

    st.divider()

    st.markdown("### Architecture")
    st.markdown("""
```
You ──→ This App ──→ CLM Server ──→ Claude / ChatGPT
You ←── This App ←── CLM Server ←── Claude / ChatGPT
```

| Component | What it does |
|-----------|-------------|
| **This App** (Streamlit) | The interface you're looking at — handles text, voice, and display |
| **CLM Server** (FastAPI) | The "brain router" — receives your message and sends it to the AI |
| **Claude / ChatGPT** | The AI that generates the response |
| **Google STT** | Converts your voice recording to text (Tab 3) |
| **Google TTS** | Converts the AI's text response to audio (Tabs 2 & 3) |
""")

    st.divider()

    st.markdown("### How Each Tab Works")

    st.markdown("""
**Text Chat** — Simplest mode. You type, the AI responds in text.
The flow: Your text → CLM Server → Claude/ChatGPT → Text response

**Text + Voice** — You type, the AI responds in text AND speaks it aloud.
The flow: Your text → CLM Server → Claude/ChatGPT → Text + Google TTS audio

**Voice Pipeline** — Full voice experience. You speak, the AI speaks back.
The flow: Your voice → Google STT → CLM Server → Claude/ChatGPT → Google TTS → Audio playback
""")

    st.divider()

    st.markdown("### Swapping AI Brains")
    st.markdown("""
Use the toggle in the sidebar to switch between **Claude** (Anthropic) and **ChatGPT** (OpenAI).

The switch happens instantly — no restart needed. Try asking the same question to both and compare the answers!

| AI | Model | Style |
|----|-------|-------|
| **Claude** | claude-3-haiku | Concise, careful |
| **ChatGPT** | gpt-4o-mini | Conversational, detailed |
""")

    st.divider()

    st.markdown("### Advanced: Hume EVI (Real-Time Voice)")
    with st.expander("Hume EVI Setup (Optional)", expanded=False):
        st.markdown("""
For real-time streaming voice (no record button — just talk), you can connect Hume EVI:

**1.** Install ngrok: `brew install ngrok`

**2.** Expose your CLM server:
```bash
ngrok http 8000
```

**3.** Create a Hume EVI config at [platform.hume.ai](https://platform.hume.ai/):
- Language Model → Custom Language Model
- CLM URL → `wss://YOUR-NGROK-URL/ws/clm`

**4.** Add to `.env`:
```
HUME_API_KEY=your-key
HUME_CONFIG_ID=your-config-id
```

**5.** Connect:
```bash
python hume_connect.py
```

Hume adds **emotion detection from your voice tone** — it can tell if you sound happy, stressed, curious, etc. and the AI adjusts its response.
""")

    st.divider()

    st.markdown("### Links")
    st.markdown("""
- [Anthropic Console](https://console.anthropic.com/) — Claude API keys
- [OpenAI Platform](https://platform.openai.com/) — ChatGPT API keys
- [Hume AI](https://platform.hume.ai/) — Voice + emotion API
- [Streamlit Docs](https://docs.streamlit.io/) — Frontend framework
""")
