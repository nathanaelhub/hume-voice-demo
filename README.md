# Voice AI Demo

A voice AI demo that combines **Hume AI** (voice and emotion) with **Claude** and **ChatGPT** (thinking). Talk to an AI by voice, switch between providers, and see how the pieces fit together.

## What This Demo Shows

- **Live Voice-to-Voice** — Talk naturally, get spoken responses, interrupt the AI anytime
- **Switch AI Providers** — Toggle between Claude and ChatGPT with one click
- **Emotion Detection** — Hume detects emotion from your tone of voice
- **Three Ways to Interact** — Text chat, text + voice response, and full voice-to-voice

## Tabs

| Tab | What It Does |
|-----|-------------|
| **Text Chat** | Type a message, get a text response |
| **Text + Voice** | Type a message, hear the response spoken aloud |
| **Voice to Voice** | Speak naturally, AI responds by voice in real time |
| **Documentation** | How the app works and what's under the hood |

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/nathanaelhub/hume-voice-demo.git
cd hume-voice-demo
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

| Key | Where to Get It | Required For |
|-----|----------------|--------------|
| `HUME_API_KEY` | [platform.hume.ai](https://platform.hume.ai/) | Voice-to-Voice tab |
| `HUME_SECRET_KEY` | Same Hume dashboard (API keys section) | Voice-to-Voice tab |
| `HUME_CONFIG_ID` | Hume EVI config page | Voice-to-Voice tab |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) | Claude provider |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/) | ChatGPT provider |

### 3. Run the App

```bash
# Start the backend server (handles AI requests)
python clm_server/server.py

# In another terminal, start the app
streamlit run frontend/app.py
```

Open **http://localhost:8501** in your browser.

## How It Works

```
Voice-to-Voice:
  You speak → Hume AI (handles voice + emotion) → Claude or ChatGPT (thinks) → You hear a response

Text tabs:
  You type → Claude or ChatGPT → You read the response
```

Hume AI handles everything about voice — listening, detecting when you're done talking, speaking the response, and reading your emotion from your tone. Claude or ChatGPT handles the actual thinking and answering.

## FAQ

### Do I need API keys?

Yes. You'll need keys for the AI providers you want to use (Claude, ChatGPT, or both). Your professor may share Hume voice credentials with the class — just paste them into your `.env` file.

### If my professor changes the AI voice, do I need to do anything?

No. Voice changes happen on Hume's website and take effect automatically the next time you click the mic button. You don't need to change any code or settings.

### How long can a voice conversation go?

As long as the mic is active, you can keep talking back and forth. Clicking the mic to stop and starting again begins a fresh conversation.

### What browser should I use?

Chrome works best. Firefox and Edge also work. Safari may have issues.

### The mic isn't working — what do I do?

Make sure you allowed microphone access when the browser asked. If you accidentally blocked it, click the lock icon in the address bar and allow microphone access, then refresh the page.

### Can I switch between Claude and ChatGPT?

Yes — use the toggle in the sidebar. It switches instantly on all tabs.
