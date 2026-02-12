"""
Tab 4: Documentation  (Atmos theme)
======================================
All setup guides, architecture info, and technical details.
Keeps the other tabs clean.
"""

import streamlit as st

from components.theme import COLORS


def _card(title: str, body: str):
    """Render a section inside a dark themed card."""
    st.markdown(
        f"""<div style="
            background:{COLORS['surface']};
            border:1px solid {COLORS['border']};
            border-radius:14px;
            padding:22px 26px;
            margin-bottom:16px;
        ">
            <h3 style="font-family:'Syne',sans-serif;font-weight:700;
                color:{COLORS['text']};margin:0 0 12px 0;font-size:1.15rem;">
                {title}</h3>
            <div style="font-family:'Outfit',sans-serif;color:{COLORS['text_secondary']};
                line-height:1.65;font-size:0.92rem;">
                {body}
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_docs_tab():
    """Render the documentation tab."""

    _card("Getting Started", """
<strong>1. Clone and install</strong>
<pre style="background:{bg};border:1px solid {bdr};border-radius:8px;padding:12px;
    font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:{txt};margin:8px 0;">
git clone &lt;repo-url&gt;
cd hume-voice-demo
pip install -r requirements.txt</pre>

<strong>2. Add your API keys</strong>
<pre style="background:{bg};border:1px solid {bdr};border-radius:8px;padding:12px;
    font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:{txt};margin:8px 0;">
cp .env.example .env</pre>
Then edit <code>.env</code> and paste your keys:
<ul style="margin:6px 0 6px 18px;color:{sec};">
    <li><code>ANTHROPIC_API_KEY</code> &mdash; from console.anthropic.com</li>
    <li><code>OPENAI_API_KEY</code> &mdash; from platform.openai.com</li>
    <li><code>HUME_API_KEY</code> &mdash; from platform.hume.ai (optional)</li>
</ul>

<strong>3. Run it</strong>
<pre style="background:{bg};border:1px solid {bdr};border-radius:8px;padding:12px;
    font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:{txt};margin:8px 0;">
# Terminal 1: start the AI server
python clm_server/server.py

# Terminal 2: start the app
streamlit run frontend/app.py</pre>
    """.format(bg=COLORS['bg'], bdr=COLORS['border'], txt=COLORS['text'], sec=COLORS['text_secondary']))

    _card("Architecture", """
<pre style="background:{bg};border:1px solid {bdr};border-radius:8px;padding:14px;
    font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:{txt};margin:8px 0;">
You  ──→  This App  ──→  CLM Server  ──→  Claude / ChatGPT
You  ←──  This App  ←──  CLM Server  ←──  Claude / ChatGPT</pre>

<table style="width:100%;border-collapse:collapse;margin-top:10px;">
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">This App (Streamlit)</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">The interface you're looking at &mdash; handles text, voice, and display</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">CLM Server (FastAPI)</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">The "brain router" &mdash; receives your message and sends it to the AI</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">Claude / ChatGPT</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">The AI that generates the response</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">Google STT</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Converts your voice recording to text (Tab 3)</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">Google TTS</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Converts the AI's text response to audio (Tabs 2 &amp; 3)</td>
    </tr>
</table>
    """.format(bg=COLORS['bg'], bdr=COLORS['border'], txt=COLORS['text'], sec=COLORS['text_secondary']))

    _card("How Each Tab Works", """
<p><strong style="color:{txt};">Text Chat</strong> &mdash; Simplest mode. You type, the AI responds in text.<br>
<span style="color:{muted};">Your text → CLM Server → Claude/ChatGPT → Text response</span></p>

<p><strong style="color:{txt};">Text + Voice</strong> &mdash; You type, the AI responds in text AND speaks it aloud.<br>
<span style="color:{muted};">Your text → CLM Server → Claude/ChatGPT → Text + Google TTS audio</span></p>

<p><strong style="color:{txt};">Voice Pipeline</strong> &mdash; Full voice experience. You speak, the AI speaks back.<br>
<span style="color:{muted};">Your voice → Google STT → CLM Server → Claude/ChatGPT → Google TTS → Audio playback</span></p>
    """.format(txt=COLORS['text'], muted=COLORS['text_muted']))

    _card("Swapping AI Brains", """
Use the toggle in the sidebar to switch between <strong>Claude</strong> (Anthropic)
and <strong>ChatGPT</strong> (OpenAI).

<p>The switch happens instantly &mdash; no restart needed. Try asking the same question to both and compare!</p>

<table style="width:100%;border-collapse:collapse;margin-top:10px;">
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:#E8622C;">Claude</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">claude-3-haiku</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Concise, careful</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:#00C9A7;">ChatGPT</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">gpt-4o-mini</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Conversational, detailed</td>
    </tr>
</table>
    """.format(bdr=COLORS['border'], sec=COLORS['text_secondary']))

    # Hume EVI section uses a native Streamlit expander so it remains interactive
    _card("Advanced: Hume EVI (Real-Time Voice)", "")
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

    _card("Links", """
<ul style="list-style:none;padding:0;margin:0;">
    <li style="margin-bottom:6px;"><a href="https://console.anthropic.com/" style="color:#E8622C;text-decoration:none;">Anthropic Console</a> &mdash; Claude API keys</li>
    <li style="margin-bottom:6px;"><a href="https://platform.openai.com/" style="color:#00C9A7;text-decoration:none;">OpenAI Platform</a> &mdash; ChatGPT API keys</li>
    <li style="margin-bottom:6px;"><a href="https://platform.hume.ai/" style="color:{sec};text-decoration:none;">Hume AI</a> &mdash; Voice + emotion API</li>
    <li><a href="https://docs.streamlit.io/" style="color:{sec};text-decoration:none;">Streamlit Docs</a> &mdash; Frontend framework</li>
</ul>
    """.format(sec=COLORS['text_secondary']))
