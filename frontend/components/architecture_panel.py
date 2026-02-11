"""
Architecture Panel Component
==============================
Collapsible panel showing the voice pipeline architecture diagram.
Styled after the Bison Chat educational approach.
"""

import streamlit as st


def render_architecture_panel():
    """Render the collapsible architecture diagram panel."""

    with st.expander("Architecture: How the Voice Pipeline Works", expanded=False):
        st.markdown("""
### Voice AI Pipeline Architecture

This demo composes **three independent AI services** into a single voice experience.
Each component does one thing well — this is how production AI systems are built.

---
""")

        # Render the pipeline as columns
        cols = st.columns(4)

        with cols[0]:
            st.markdown("""
#### 1. User Voice
- You speak into your microphone
- Raw audio waveform is captured
- Sent to Hume via WebSocket
""")
            st.markdown("```\nAudio Stream →\n```")

        with cols[1]:
            st.markdown("""
#### 2. Hume EVI
- **Speech-to-Text**: Converts audio → transcript
- **Prosody Analysis**: Detects emotions from voice tone
- **Text-to-Speech**: Converts response → audio
""")
            st.markdown("```\nTranscript + Emotions →\n```")

        with cols[2]:
            st.markdown("""
#### 3. CLM Server
- Receives transcript + emotion data
- Enriches prompt with emotion context
- Routes to Claude API
- Returns response to Hume
""")
            st.markdown("```\nPrompt →\n```")

        with cols[3]:
            st.markdown("""
#### 4. Claude API
- Processes the enriched prompt
- Generates conversational response
- Considers emotional context
- Returns text to CLM server
""")
            st.markdown("```\n← Response\n```")

        st.markdown("---")

        st.markdown("""
### Key Concepts for Your Presentation

| Concept | What It Means | Why It Matters |
|---------|--------------|----------------|
| **API Composition** | Chaining multiple APIs together | No single API does everything — you compose capabilities |
| **Custom Language Model (CLM)** | Your server that wraps an LLM | You control the "brain" — swap Claude for GPT, Llama, etc. |
| **Prosody Analysis** | Reading emotion from voice tone | Goes beyond words — understands *how* something is said |
| **WebSocket** | Persistent bidirectional connection | Required for real-time streaming audio/text |
| **Modularity** | Each component is replaceable | Swap Hume for Deepgram, Claude for GPT — the architecture stays |

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────▶│  Hume EVI   │────▶│  Your CLM   │────▶│  Claude API │
│   Voice     │     │  (Speech→   │     │   Server    │     │  (Thinking) │
│             │◀────│   Text→     │◀────│             │◀────│             │
│             │     │   Speech)   │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │
                    Emotion/Prosody
                      Detection
```
""")


def render_tech_stack_panel():
    """Render a collapsible panel showing the tech stack details."""

    with st.expander("Tech Stack Details", expanded=False):
        st.markdown("""
| Component | Tool | Why |
|-----------|------|-----|
| **Frontend** | Streamlit | Fast prototyping, Python-native, real-time updates |
| **CLM Server** | FastAPI | Async Python, WebSocket support, auto-generated docs |
| **LLM** | Claude API (Anthropic) | Strong reasoning, safety-focused, your existing credits |
| **Voice AI** | Hume EVI | Speech + emotion detection in one API |
| **Tunnel** | ngrok | Exposes localhost so Hume can reach your CLM server |
""")

        st.markdown("""
### How to Set Up ngrok (for Hume to reach your CLM)

```bash
# Install ngrok
brew install ngrok

# Start your CLM server
python clm_server/server.py

# In another terminal, expose it
ngrok http 8000

# Copy the https://xxxx.ngrok.io URL into Hume's CLM config
```
""")
