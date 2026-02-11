"""
Hume EVI Connection Script
============================
Connects to Hume EVI using the Python SDK.
This handles the voice input/output — Hume will route
the "thinking" through your CLM server automatically.

Usage:
    python hume_connect.py

Prerequisites:
    1. CLM server running (python clm_server/server.py)
    2. ngrok exposing CLM server (ngrok http 8000)
    3. Hume EVI config pointing to your ngrok CLM URL
    4. HUME_API_KEY and HUME_CONFIG_ID set in .env
"""

import asyncio
import os

from dotenv import load_dotenv
from hume.client import AsyncHumeClient

load_dotenv()


async def main():
    api_key = os.getenv("HUME_API_KEY")
    config_id = os.getenv("HUME_CONFIG_ID")

    if not api_key:
        print("Error: HUME_API_KEY not set in .env")
        print("Get your key at https://platform.hume.ai/")
        return

    if not config_id:
        print("Error: HUME_CONFIG_ID not set in .env")
        print("Create an EVI config at https://platform.hume.ai/")
        print("Make sure to set your CLM URL to your ngrok WebSocket URL")
        return

    print("Connecting to Hume EVI...")
    print(f"  Config ID: {config_id}")
    print(f"  API Key:   {api_key[:8]}...")
    print()

    client = AsyncHumeClient(api_key=api_key)

    async with client.empathic_voice.chat.connect(config_id=config_id) as socket:
        print("Connected! Speak into your microphone.")
        print("(Hume will transcribe → send to your CLM → Claude responds → Hume speaks)")
        print("Press Ctrl+C to disconnect.\n")

        async for message in socket:
            # Log messages for debugging
            msg_type = getattr(message, "type", "unknown")

            if msg_type == "user_message":
                transcript = getattr(message, "message", {})
                if hasattr(transcript, "content"):
                    print(f"  You: {transcript.content}")

                # Log emotions if available
                models = getattr(message, "models", None)
                if models:
                    prosody = getattr(models, "prosody", None)
                    if prosody and hasattr(prosody, "scores"):
                        top_emotions = sorted(
                            prosody.scores.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )[:3]
                        emotion_str = ", ".join(
                            f"{name}: {score:.0%}" for name, score in top_emotions
                        )
                        print(f"  Emotions: {emotion_str}")

            elif msg_type == "assistant_message":
                content = getattr(message, "message", {})
                if hasattr(content, "content"):
                    print(f"  Claude: {content.content}")

            elif msg_type == "audio_output":
                pass  # Audio is played by the SDK

            elif msg_type == "error":
                print(f"  Error: {message}")

            else:
                # Debug: print unknown message types
                print(f"  [{msg_type}]: {str(message)[:200]}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnected from Hume EVI.")
