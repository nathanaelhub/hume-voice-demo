"""
CLM (Custom Language Model) Server
===================================
FastAPI server that acts as the bridge between Hume EVI and your LLM of choice.

Hume EVI sends transcribed user speech here. This server:
1. Receives the transcript + emotion/prosody data from Hume
2. Sends it to Claude or OpenAI for reasoning (swappable via LLM_PROVIDER env var)
3. Streams the response back to Hume for text-to-speech

Architecture:
  User Voice → Hume EVI → [this server] → Claude API / OpenAI API
  User Voice ← Hume EVI ← [this server] ← Claude API / OpenAI API
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import openai
except ImportError:
    openai = None

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# State shared with the Streamlit frontend via /status endpoint
# ---------------------------------------------------------------------------

class PipelineState:
    """Tracks the current state of the voice pipeline for UI display."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.stage: str = "idle"  # idle | listening | transcribed | thinking | speaking
        self.transcript: str = ""
        self.response: str = ""
        self.emotions: list[dict] = []
        self.timestamp: str = datetime.now().isoformat()
        self.latency_ms: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "transcript": self.transcript,
            "response": self.response,
            "emotions": self.emotions,
            "timestamp": self.timestamp,
            "latency_ms": self.latency_ms,
        }


pipeline_state = PipelineState()
# History of all interactions for the Streamlit UI
interaction_history: list[dict] = []

# ---------------------------------------------------------------------------
# LLM clients — set LLM_PROVIDER=claude or LLM_PROVIDER=openai in .env
# ---------------------------------------------------------------------------

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "claude")  # "claude" or "openai"

claude_client: Optional[anthropic.Anthropic] = None
openai_client: Optional["openai.OpenAI"] = None

SYSTEM_PROMPT = """You are a helpful, empathetic voice assistant. You are part of a \
voice pipeline demo that shows how AI systems compose together.

Keep your responses concise and conversational — they will be spoken aloud.
Aim for 1-3 sentences unless the user asks for detail.

You may receive emotion/prosody data detected from the user's voice. Use this \
context naturally — if someone sounds stressed, acknowledge it gently. If they \
sound excited, match their energy. Don't explicitly say "I detect you are feeling X" \
unless it's natural to do so."""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the selected LLM client on startup."""
    global claude_client, openai_client, LLM_PROVIDER

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude").lower()
    logger.info(f"LLM Provider: {LLM_PROVIDER}")

    if LLM_PROVIDER == "openai":
        if openai is None:
            logger.error("openai package not installed! Run: pip install openai")
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY not set!")
            else:
                openai_client = openai.OpenAI(api_key=api_key)
                logger.info(f"OpenAI client initialized (model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')})")
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not set!")
        else:
            claude_client = anthropic.Anthropic(api_key=api_key)
            logger.info("Claude client initialized successfully")

    yield
    logger.info("CLM server shutting down")


app = FastAPI(
    title="Hume EVI × Claude CLM Server",
    description="Custom Language Model server bridging Hume EVI and Claude API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Hume EVI CLM endpoint (WebSocket)
# ---------------------------------------------------------------------------

@app.websocket("/ws/clm")
async def clm_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for Hume EVI's Custom Language Model protocol.

    Hume sends JSON messages with the user's transcript and prosody data.
    We respond with Claude's generated text, streamed back to Hume.
    """
    await websocket.accept()
    logger.info("Hume EVI connected to CLM WebSocket")

    # Conversation history for multi-turn context
    conversation: list[dict] = []

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            logger.info(f"Received from Hume: {json.dumps(message, indent=2)[:500]}")

            # --- Extract transcript and emotions ---
            transcript = _extract_transcript(message)
            emotions = _extract_emotions(message)

            if not transcript:
                continue

            # Update pipeline state for UI
            pipeline_state.stage = "transcribed"
            pipeline_state.transcript = transcript
            pipeline_state.emotions = emotions
            pipeline_state.timestamp = datetime.now().isoformat()

            logger.info(f"Transcript: {transcript}")
            if emotions:
                top_emotions = sorted(emotions, key=lambda e: e.get("score", 0), reverse=True)[:3]
                logger.info(f"Top emotions: {top_emotions}")

            # --- Build Claude prompt with emotion context ---
            emotion_context = ""
            if emotions:
                top = sorted(emotions, key=lambda e: e.get("score", 0), reverse=True)[:5]
                emotion_str = ", ".join(f"{e['name']}: {e['score']:.2f}" for e in top)
                emotion_context = f"\n[Voice emotion analysis: {emotion_str}]"

            user_message = f"{transcript}{emotion_context}"
            conversation.append({"role": "user", "content": user_message})

            # --- Call Claude ---
            pipeline_state.stage = "thinking"
            start_time = time.time()

            response_text = await _call_llm(conversation)

            elapsed_ms = (time.time() - start_time) * 1000
            pipeline_state.latency_ms = round(elapsed_ms, 1)

            conversation.append({"role": "assistant", "content": response_text})

            # --- Update state and send response back to Hume ---
            pipeline_state.stage = "speaking"
            pipeline_state.response = response_text

            # Store in history
            interaction_history.append(pipeline_state.to_dict())

            # Send response in Hume CLM format
            clm_response = {
                "type": "assistant_input",
                "text": response_text,
            }
            await websocket.send_text(json.dumps(clm_response))
            logger.info(f"Sent to Hume: {response_text[:200]}")

            # Reset to idle after a brief pause
            await asyncio.sleep(0.5)
            pipeline_state.stage = "idle"

    except WebSocketDisconnect:
        logger.info("Hume EVI disconnected from CLM WebSocket")
        pipeline_state.reset()
    except Exception as e:
        logger.error(f"CLM WebSocket error: {e}", exc_info=True)
        pipeline_state.reset()


def _extract_transcript(message: dict) -> str:
    """Extract the user's transcript from a Hume EVI message."""
    # Hume EVI CLM message format
    if "messages" in message:
        for msg in reversed(message["messages"]):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content.strip()
                if isinstance(content, dict):
                    return content.get("text", "").strip()
    # Direct transcript field
    if "transcript" in message:
        return message["transcript"].strip()
    # Fallback: text field
    if "text" in message:
        return message["text"].strip()
    return ""


def _extract_emotions(message: dict) -> list[dict]:
    """Extract prosody/emotion data from a Hume EVI message."""
    emotions = []

    # Check for prosody models in the message
    if "models" in message:
        prosody = message["models"].get("prosody", {})
        if "predictions" in prosody:
            for pred in prosody["predictions"]:
                for emotion in pred.get("emotions", []):
                    emotions.append({
                        "name": emotion.get("name", "unknown"),
                        "score": emotion.get("score", 0.0),
                    })

    # Check in messages array
    if "messages" in message:
        for msg in message["messages"]:
            if "models" in msg:
                prosody = msg["models"].get("prosody", {})
                if "predictions" in prosody:
                    for pred in prosody["predictions"]:
                        for emotion in pred.get("emotions", []):
                            emotions.append({
                                "name": emotion.get("name", "unknown"),
                                "score": emotion.get("score", 0.0),
                            })

    # Check for emotion_features (alternative format)
    if "emotion_features" in message:
        for name, score in message["emotion_features"].items():
            emotions.append({"name": name, "score": float(score)})

    return emotions


async def _call_llm(conversation: list[dict]) -> str:
    """Route to the configured LLM provider and return the response."""
    if LLM_PROVIDER == "openai":
        return await _call_openai(conversation)
    return await _call_claude(conversation)


async def _call_claude(conversation: list[dict]) -> str:
    """Send conversation to Claude and return the response."""
    if not claude_client:
        return "Claude API not configured. Set ANTHROPIC_API_KEY in .env"

    try:
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        response = claude_client.messages.create(
            model=model,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=conversation,
        )
        return response.content[0].text
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return "I'm having trouble thinking right now. Could you try again?"


async def _call_openai(conversation: list[dict]) -> str:
    """Send conversation to OpenAI and return the response."""
    if not openai_client:
        return "OpenAI API not configured. Set OPENAI_API_KEY in .env"

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        # OpenAI uses a system message in the messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation
        response = openai_client.chat.completions.create(
            model=model,
            max_tokens=300,
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "I'm having trouble thinking right now. Could you try again?"


# ---------------------------------------------------------------------------
# REST endpoints for Streamlit frontend
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "service": "Hume EVI CLM Server",
        "status": "running",
        "llm_provider": LLM_PROVIDER,
        "websocket": "/ws/clm",
    }


@app.get("/status")
async def get_status():
    """Current pipeline state — polled by the Streamlit frontend."""
    data = pipeline_state.to_dict()
    data["llm_provider"] = LLM_PROVIDER
    return data


@app.post("/switch/{provider}")
async def switch_provider(provider: str):
    """
    Hot-swap the LLM provider at runtime.
    POST /switch/openai  or  POST /switch/claude
    """
    global LLM_PROVIDER, claude_client, openai_client

    provider = provider.lower()
    if provider not in ("claude", "openai"):
        return {"error": "Provider must be 'claude' or 'openai'"}

    if provider == "openai":
        if openai is None:
            return {"error": "openai package not installed. Run: pip install openai"}
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {"error": "OPENAI_API_KEY not set in .env"}
        openai_client = openai.OpenAI(api_key=api_key)
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {"error": "ANTHROPIC_API_KEY not set in .env"}
        claude_client = anthropic.Anthropic(api_key=api_key)

    LLM_PROVIDER = provider
    logger.info(f"Switched LLM provider to: {provider}")
    return {"status": "switched", "llm_provider": provider}


@app.get("/history")
async def get_history():
    """Full interaction history for the Streamlit UI."""
    return {"interactions": interaction_history}


@app.post("/reset")
async def reset_state():
    """Reset the pipeline state and history."""
    pipeline_state.reset()
    interaction_history.clear()
    return {"status": "reset"}


# ---------------------------------------------------------------------------
# Direct chat endpoint (for testing without Hume)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    emotions: list[dict] = []


@app.post("/chat")
async def direct_chat(request: ChatRequest):
    """
    Direct HTTP chat endpoint for testing the Claude integration
    without needing Hume EVI connected.
    """
    pipeline_state.stage = "transcribed"
    pipeline_state.transcript = request.message
    pipeline_state.emotions = request.emotions

    emotion_context = ""
    if request.emotions:
        top = sorted(request.emotions, key=lambda e: e.get("score", 0), reverse=True)[:5]
        emotion_str = ", ".join(f"{e['name']}: {e['score']:.2f}" for e in top)
        emotion_context = f"\n[Voice emotion analysis: {emotion_str}]"

    pipeline_state.stage = "thinking"
    start_time = time.time()

    conversation = [{"role": "user", "content": f"{request.message}{emotion_context}"}]
    response_text = await _call_llm(conversation)

    elapsed_ms = (time.time() - start_time) * 1000
    pipeline_state.latency_ms = round(elapsed_ms, 1)
    pipeline_state.stage = "speaking"
    pipeline_state.response = response_text

    interaction_history.append(pipeline_state.to_dict())

    await asyncio.sleep(0.3)
    pipeline_state.stage = "idle"

    return {
        "response": response_text,
        "latency_ms": pipeline_state.latency_ms,
        "emotions_detected": request.emotions,
        "llm_provider": LLM_PROVIDER,
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("CLM_HOST", "0.0.0.0")
    port = int(os.getenv("CLM_PORT", "8000"))
    logger.info(f"Starting CLM server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
