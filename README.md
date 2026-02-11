# Hume EVI x Claude Voice Assistant

A real-time voice AI pipeline that composes **Hume EVI** (voice + emotion detection) with **Claude** (reasoning) through a custom language model server.

Built for the **Layer 2: Build Your Own App** assignment (Days 1-3).

## What This Demo Shows

- **API Composition** — Hume handles voice, Claude handles thinking, your server connects them
- **Emotion Detection** — Hume's prosody analysis detects emotions from voice tone
- **Pipeline Visualization** — See every step: Listening → Transcribed → Thinking → Speaking
- **Bring Your Own LLM** — The CLM architecture lets you swap Claude for any LLM

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys:
#   ANTHROPIC_API_KEY  — from https://console.anthropic.com/
#   HUME_API_KEY       — from https://platform.hume.ai/
#   HUME_CONFIG_ID     — from your Hume EVI configuration
```

### 3. Start the CLM Server

```bash
python clm_server/server.py
```

The server runs on `http://localhost:8000`. Visit `http://localhost:8000/docs` for the auto-generated API docs.

### 4. Start the Streamlit Frontend

```bash
streamlit run frontend/app.py
```

### 5. Test Without Voice

Use the "Test Chat" section in the Streamlit app, or hit the API directly:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! How are you?", "emotions": [{"name": "joy", "score": 0.8}]}'
```

### 6. Connect Hume EVI (Voice Mode)

```bash
# Expose your CLM server
ngrok http 8000

# Configure Hume EVI at https://platform.hume.ai/
# Set CLM URL to: wss://YOUR-NGROK-URL/ws/clm
```

## Project Structure

```
hume-voice-demo/
├── clm_server/
│   ├── server.py              # FastAPI server bridging Hume EVI ↔ Claude
│   └── requirements.txt
├── frontend/
│   ├── app.py                 # Streamlit dashboard
│   └── components/
│       ├── architecture_panel.py   # Educational architecture diagram
│       └── pipeline_display.py     # Real-time pipeline visualization
├── docs/
│   └── architecture.md        # Architecture documentation
├── .env.example               # Environment variable template
├── requirements.txt           # All dependencies
└── README.md
```

## Architecture

```
User Voice → Hume EVI → CLM Server → Claude API
User Voice ← Hume EVI ← CLM Server ← Claude API
                 │
          Emotion/Prosody
            Detection
```

See [docs/architecture.md](docs/architecture.md) for the full breakdown.
