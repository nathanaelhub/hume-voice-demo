"""
Tab 4: Documentation  (Atmos theme)
======================================
Setup guides, how the app works, and helpful links.
Written for students who may not have a technical background.
"""

import streamlit as st

from components.theme import COLORS


def _card(title: str, body: str):
    """Render a section inside a dark themed card."""
    if not body.strip():
        return
    st.markdown(
        f'<div style="background:{COLORS["surface"]};border:1px solid {COLORS["border"]};'
        f'border-radius:14px;padding:22px 26px;margin-bottom:16px;">'
        f'<h3 style="font-family:\'Syne\',sans-serif;font-weight:700;'
        f'color:{COLORS["text"]};margin:0 0 12px 0;font-size:1.15rem;">{title}</h3>'
        f'<div style="font-family:\'Outfit\',sans-serif;color:{COLORS["text_secondary"]};'
        f'line-height:1.65;font-size:0.92rem;">{body}</div></div>',
        unsafe_allow_html=True,
    )


def render_docs_tab():
    """Render the documentation tab."""

    bg = COLORS['bg']
    bdr = COLORS['border']
    txt = COLORS['text']
    sec = COLORS['text_secondary']
    muted = COLORS['text_muted']

    # --- Getting Started ---
    _card("Getting Started", f"""
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
Then open the <code>.env</code> file and paste your keys:
<ul style="margin:6px 0 6px 18px;color:{sec};">
    <li><code>ANTHROPIC_API_KEY</code> &mdash; for Claude (from console.anthropic.com)</li>
    <li><code>OPENAI_API_KEY</code> &mdash; for ChatGPT (from platform.openai.com)</li>
    <li><code>HUME_API_KEY</code>, <code>HUME_SECRET_KEY</code>, <code>HUME_CONFIG_ID</code> &mdash; for the Voice-to-Voice tab (your professor may share these)</li>
</ul>

<strong>3. Run it</strong>
<pre style="background:{bg};border:1px solid {bdr};border-radius:8px;padding:12px;
    font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:{txt};margin:8px 0;">
# Terminal 1: start the backend server
python clm_server/server.py

# Terminal 2: start the app
streamlit run frontend/app.py</pre>
Then open <strong>http://localhost:8501</strong> in Chrome.
    """)

    # --- How It Works ---
    _card("How It Works", f"""
<pre style="background:{bg};border:1px solid {bdr};border-radius:8px;padding:14px;
    font-family:'IBM Plex Mono',monospace;font-size:0.82rem;color:{txt};margin:8px 0;">
Voice-to-Voice:
  You speak  &rarr;  Hume AI (voice + emotion)  &rarr;  Claude / ChatGPT  &rarr;  You hear it

Text tabs:
  You type  &rarr;  Claude / ChatGPT  &rarr;  You read the response</pre>

<table style="width:100%;border-collapse:collapse;margin-top:10px;">
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">Hume AI</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Handles voice &mdash; listens to you, detects emotion from your tone, speaks the response back</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">Claude / ChatGPT</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">The AI that does the thinking and generates the answer</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:{txt};">This App</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">The interface you're looking at &mdash; connects everything together</td>
    </tr>
</table>
    """)

    # --- How Each Tab Works ---
    _card("How Each Tab Works", f"""
<p><strong style="color:{txt};">Text Chat</strong> &mdash; The simplest mode. You type a message, the AI responds in text.</p>

<p><strong style="color:{txt};">Text + Voice</strong> &mdash; You type a message, the AI responds in text AND speaks it aloud.</p>

<p><strong style="color:{txt};">Voice to Voice</strong> &mdash; Live conversation. Click the mic, speak naturally, and the AI
talks back in real time. You can interrupt it at any time by speaking over it. This uses Hume AI
for the voice and emotion detection, with Claude or ChatGPT doing the thinking behind the scenes.</p>
    """)

    # --- Switching AIs ---
    _card("Switching Between Claude and ChatGPT", f"""
Use the toggle in the sidebar to switch between <strong style="color:#E8622C;">Claude</strong>
and <strong style="color:#00C9A7;">ChatGPT</strong>.

<p>The switch happens instantly &mdash; no restart needed. Try asking the same question to both and compare how they respond!</p>

<table style="width:100%;border-collapse:collapse;margin-top:10px;">
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:#E8622C;">Claude</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Made by Anthropic &mdash; tends to be concise and careful</td>
    </tr>
    <tr>
        <td style="padding:8px 12px;border:1px solid {bdr};font-weight:600;color:#00C9A7;">ChatGPT</td>
        <td style="padding:8px 12px;border:1px solid {bdr};color:{sec};">Made by OpenAI &mdash; tends to be conversational and detailed</td>
    </tr>
</table>
    """)

    # --- Why Streamlit ---
    _card("Why Streamlit?", f"""
<p>This app is built with <strong>Streamlit</strong>, a Python framework that turns Python scripts into
web apps. We chose it over tools like React or Next.js for a few reasons:</p>

<ul style="margin:8px 0 8px 18px;color:{sec};">
    <li><strong style="color:{txt};">Python only</strong> &mdash; no need to learn JavaScript, HTML, CSS, or Node.js</li>
    <li><strong style="color:{txt};">One command to run</strong> &mdash; <code>streamlit run app.py</code> and you have a working web app</li>
    <li><strong style="color:{txt};">The focus is the AI</strong> &mdash; Streamlit handles the UI so we can focus on Hume, Claude, and ChatGPT</li>
</ul>

<p>The tradeoff is that Streamlit is more limited than React for complex interfaces. That's why the
Voice-to-Voice tab uses custom JavaScript under the hood &mdash; Streamlit can't do live audio streaming
on its own. For a classroom demo, Streamlit gets you there much faster.</p>
    """)

    # --- Helpful Links ---
    _card("Helpful Links", f"""
<ul style="list-style:none;padding:0;margin:0;">
    <li style="margin-bottom:6px;"><a href="https://console.anthropic.com/" style="color:#E8622C;text-decoration:none;">Anthropic Console</a> &mdash; get a Claude API key</li>
    <li style="margin-bottom:6px;"><a href="https://platform.openai.com/" style="color:#00C9A7;text-decoration:none;">OpenAI Platform</a> &mdash; get a ChatGPT API key</li>
    <li style="margin-bottom:6px;"><a href="https://platform.hume.ai/" style="color:{sec};text-decoration:none;">Hume AI</a> &mdash; voice and emotion API</li>
    <li><a href="https://docs.streamlit.io/" style="color:{sec};text-decoration:none;">Streamlit Docs</a> &mdash; the framework this app is built with</li>
</ul>
    """)
