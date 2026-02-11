# Architecture: Hume EVI x Claude Voice Pipeline

## Overview

This project demonstrates **API composition** — chaining multiple specialized AI services
into a single voice assistant experience. No single API does everything; instead, each
component handles what it does best.

## Pipeline Flow

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

### Step-by-step

1. **User speaks** into their microphone
2. **Hume EVI** receives the audio stream via WebSocket
   - Converts speech to text (ASR)
   - Analyzes prosody to detect emotions (joy, sadness, anger, etc.)
   - Sends transcript + emotion data to your CLM server
3. **CLM Server (FastAPI)** receives the enriched message
   - Adds emotion context to the prompt
   - Calls Claude API with conversation history
   - Returns Claude's response to Hume
4. **Claude API** generates a conversational response
   - Considers the emotional context
   - Keeps responses concise (voice-friendly)
5. **Hume EVI** converts the response text to speech
   - Speaks the response to the user with natural prosody

## Components

### Hume EVI (Empathic Voice Interface)
- **Role**: Voice I/O + emotion detection
- **Key feature**: Prosody analysis detects *how* something is said, not just *what*
- **Protocol**: WebSocket for real-time streaming
- **Website**: https://hume.ai

### CLM Server (Custom Language Model)
- **Role**: Bridge between Hume and your LLM
- **Tech**: FastAPI (Python)
- **Why it exists**: Hume's CLM protocol lets you bring your own LLM
- **Endpoints**:
  - `ws://host/ws/clm` — WebSocket for Hume EVI
  - `GET /status` — Current pipeline state (for Streamlit)
  - `GET /history` — Interaction history
  - `POST /chat` — Direct test endpoint (no voice needed)

### Claude API
- **Role**: Language understanding and generation
- **Model**: claude-sonnet-4-5-20250514
- **Why Claude**: Strong reasoning, safety-focused, existing API credits
- **Could swap for**: GPT-4, Llama, Gemini — the architecture is modular

### Streamlit Frontend
- **Role**: Educational visualization
- **Shows**: Pipeline state, emotion data, conversation history
- **Style**: Bison Chat-inspired educational UI

## Key Concepts

### API Composition
Chaining `Hume (voice) → Your server (routing) → Claude (thinking)` demonstrates
how production AI systems are built from specialized components.

### Bring Your Own LLM (BYOLLM)
Hume's CLM protocol means you control the "brain." This is a real architectural
pattern — the voice layer and thinking layer are decoupled.

### Prosody Analysis
Traditional chatbots only see text. Hume's prosody analysis adds a dimension:
*how* something is said (tone, pace, pitch) reveals emotional state. This enables
more empathetic responses.

### WebSocket vs REST
- Voice streaming requires WebSockets (persistent, bidirectional)
- The Streamlit frontend uses REST polling (simpler, sufficient for UI updates)

## Running the Demo

```bash
# Terminal 1: Start the CLM server
python clm_server/server.py

# Terminal 2: Expose via ngrok
ngrok http 8000

# Terminal 3: Start the Streamlit frontend
streamlit run frontend/app.py

# Then configure Hume EVI to point to your ngrok URL
```
