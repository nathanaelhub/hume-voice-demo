"""
Tab 3: Voice to Voice
=======================
Live continuous voice conversation with a centered waveform UI.
Uses the browser's Web Speech API for real-time STT/TTS
and a Canvas-based audio visualizer.
"""

import streamlit as st
import streamlit.components.v1 as components


def render_voice_voice_tab(
    clm_url: str,
    clm_connected: bool,
    pipeline_state: dict,
    history: list[dict],
):
    """Render the Voice to Voice tab with a live waveform interface."""

    if not clm_connected:
        st.warning("**Server not running.** Run: `python clm_server/server.py`")
        return

    provider = st.session_state.get("active_provider", "claude")
    provider_color = "#7C3AED" if provider == "claude" else "#10A37F"
    provider_name = "Claude" if provider == "claude" else "ChatGPT"

    # The entire voice UI is a single HTML component
    components.html(
        _build_voice_ui(clm_url, provider_name, provider_color),
        height=700,
        scrolling=False,
    )


def _build_voice_ui(clm_url: str, provider_name: str, provider_color: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background: #0a0a1a;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        overflow: hidden;
    }}

    .container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        max-width: 800px;
    }}

    /* Status text */
    .status {{
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 20px;
        color: #6B7280;
        transition: color 0.3s;
    }}
    .status.listening {{ color: #3B82F6; }}
    .status.thinking {{ color: #F59E0B; }}
    .status.speaking {{ color: #10B981; }}

    /* Canvas waveform */
    canvas {{
        width: 100%;
        height: 200px;
        border-radius: 16px;
    }}

    /* Mic button */
    .mic-btn {{
        width: 72px;
        height: 72px;
        border-radius: 50%;
        border: 3px solid #374151;
        background: #1a1a2e;
        color: #9CA3AF;
        font-size: 28px;
        cursor: pointer;
        margin-top: 24px;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .mic-btn:hover {{ border-color: #6366F1; color: #6366F1; }}
    .mic-btn.active {{
        border-color: #EF4444;
        color: #EF4444;
        box-shadow: 0 0 20px rgba(239,68,68,0.3);
        animation: pulse-ring 1.5s infinite;
    }}
    @keyframes pulse-ring {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(239,68,68,0.3); }}
        50% {{ box-shadow: 0 0 35px rgba(239,68,68,0.5); }}
    }}

    /* Provider badge */
    .provider {{
        margin-top: 16px;
        padding: 4px 14px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        background: {provider_color}33;
        color: {provider_color};
    }}

    /* Transcript area */
    .transcript-area {{
        width: 100%;
        margin-top: 20px;
        max-height: 180px;
        overflow-y: auto;
        padding: 0 20px;
    }}
    .msg {{
        padding: 8px 14px;
        border-radius: 12px;
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 1.4;
        max-width: 85%;
        word-wrap: break-word;
    }}
    .msg.user {{
        background: #1e293b;
        color: #94A3B8;
        margin-left: auto;
        text-align: right;
    }}
    .msg.ai {{
        background: {provider_color}22;
        color: #E2E8F0;
        border-left: 3px solid {provider_color};
    }}
    .msg .meta {{
        font-size: 11px;
        color: #6B7280;
        margin-top: 4px;
    }}

    /* Unsupported browser message */
    .unsupported {{
        text-align: center;
        padding: 40px;
        color: #9CA3AF;
    }}
    .unsupported h3 {{ color: #F59E0B; margin-bottom: 12px; }}
</style>
</head>
<body>

<div class="container" id="app">
    <div class="status" id="status">TAP MIC TO START</div>
    <canvas id="waveform" width="800" height="200"></canvas>
    <button class="mic-btn" id="micBtn" onclick="toggleMic()">&#x1f3a4;</button>
    <div class="provider">{provider_name}</div>
    <div class="transcript-area" id="transcript"></div>
</div>

<div class="unsupported" id="unsupported" style="display:none;">
    <h3>Browser Not Supported</h3>
    <p>Voice mode requires Chrome, Edge, or Safari.<br>
    Use the Text Chat or Text + Voice tabs instead.</p>
</div>

<script>
const CLM_URL = "{clm_url}";
const PROVIDER_COLOR = "{provider_color}";

// --- Check browser support ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {{
    document.getElementById('app').style.display = 'none';
    document.getElementById('unsupported').style.display = 'block';
}}

// --- State ---
let isListening = false;
let recognition = null;
let audioCtx = null;
let analyser = null;
let animFrame = null;
let micStream = null;

const canvas = document.getElementById('waveform');
const ctx = canvas.getContext('2d');
const statusEl = document.getElementById('status');
const micBtn = document.getElementById('micBtn');
const transcriptEl = document.getElementById('transcript');

// --- Canvas setup ---
function resizeCanvas() {{
    canvas.width = canvas.offsetWidth * 2;
    canvas.height = 400;
}}
resizeCanvas();

// --- Waveform rendering ---
function drawWaveform(dataArray, state) {{
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const bars = dataArray ? dataArray.length : 64;
    const barW = Math.max(2, (W / bars) - 2);
    const gap = 2;

    for (let i = 0; i < bars; i++) {{
        let value = dataArray ? dataArray[i] / 255 : 0;

        // Idle: tiny random flicker
        if (state === 'idle') {{
            value = 0.02 + Math.random() * 0.03;
        }}

        const barH = Math.max(2, value * H * 0.8);
        const x = i * (barW + gap);
        const y = (H - barH) / 2;

        // Color gradient based on state
        let gradient = ctx.createLinearGradient(x, y, x, y + barH);
        if (state === 'listening') {{
            gradient.addColorStop(0, '#818CF8');
            gradient.addColorStop(0.5, '#6366F1');
            gradient.addColorStop(1, '#4F46E5');
        }} else if (state === 'thinking') {{
            gradient.addColorStop(0, '#FCD34D');
            gradient.addColorStop(0.5, '#F59E0B');
            gradient.addColorStop(1, '#D97706');
        }} else if (state === 'speaking') {{
            gradient.addColorStop(0, '#34D399');
            gradient.addColorStop(0.5, '#10B981');
            gradient.addColorStop(1, '#059669');
        }} else {{
            gradient.addColorStop(0, '#374151');
            gradient.addColorStop(1, '#1F2937');
        }}

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(x, y, barW, barH, 2);
        ctx.fill();
    }}
}}

// --- Idle animation ---
function drawIdle() {{
    const fakeData = new Uint8Array(64);
    for (let i = 0; i < 64; i++) {{
        fakeData[i] = 5 + Math.sin(Date.now() / 500 + i * 0.3) * 3;
    }}
    drawWaveform(fakeData, 'idle');
    animFrame = requestAnimationFrame(drawIdle);
}}

// --- Live mic visualization ---
function drawLive() {{
    if (!analyser) return;
    const data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    drawWaveform(data, 'listening');
    animFrame = requestAnimationFrame(drawLive);
}}

// --- Thinking animation ---
function drawThinking() {{
    const fakeData = new Uint8Array(64);
    const t = Date.now() / 300;
    for (let i = 0; i < 64; i++) {{
        fakeData[i] = 30 + Math.sin(t + i * 0.2) * 25 + Math.sin(t * 1.5 + i * 0.1) * 15;
    }}
    drawWaveform(fakeData, 'thinking');
    animFrame = requestAnimationFrame(drawThinking);
}}

// --- Speaking animation ---
function drawSpeaking() {{
    const fakeData = new Uint8Array(64);
    const t = Date.now() / 200;
    for (let i = 0; i < 64; i++) {{
        const center = 32;
        const dist = Math.abs(i - center) / center;
        const base = (1 - dist * dist) * 200;
        fakeData[i] = base * (0.5 + Math.sin(t + i * 0.15) * 0.3 + Math.sin(t * 2.3 + i * 0.08) * 0.2);
    }}
    drawWaveform(fakeData, 'speaking');
    animFrame = requestAnimationFrame(drawSpeaking);
}}

// --- Set state ---
function setState(state, text) {{
    statusEl.textContent = text || state.toUpperCase();
    statusEl.className = 'status ' + state;
    cancelAnimationFrame(animFrame);
    if (state === 'idle') drawIdle();
    else if (state === 'listening') drawLive();
    else if (state === 'thinking') drawThinking();
    else if (state === 'speaking') drawSpeaking();
}}

// --- Add message to transcript ---
function addMessage(role, text, meta) {{
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.innerHTML = text + (meta ? '<div class="meta">' + meta + '</div>' : '');
    transcriptEl.appendChild(div);
    transcriptEl.scrollTop = transcriptEl.scrollHeight;
}}

// --- Toggle microphone ---
async function toggleMic() {{
    if (isListening) {{
        stopListening();
    }} else {{
        await startListening();
    }}
}}

async function startListening() {{
    try {{
        // Get mic stream for visualizer
        micStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioCtx.createMediaStreamSource(micStream);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 128;
        source.connect(analyser);

        // Start speech recognition
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = handleSpeechResult;
        recognition.onerror = (e) => {{
            if (e.error !== 'no-speech') {{
                console.error('Speech error:', e.error);
            }}
        }};
        recognition.onend = () => {{
            // Auto-restart if still in listening mode
            if (isListening) {{
                try {{ recognition.start(); }} catch(e) {{}}
            }}
        }};

        recognition.start();
        isListening = true;
        micBtn.classList.add('active');
        setState('listening', 'LISTENING...');
    }} catch (err) {{
        addMessage('ai', 'Microphone access denied. Please allow mic access and try again.', '');
    }}
}}

function stopListening() {{
    isListening = false;
    micBtn.classList.remove('active');
    if (recognition) {{
        recognition.stop();
        recognition = null;
    }}
    if (micStream) {{
        micStream.getTracks().forEach(t => t.stop());
        micStream = null;
    }}
    if (audioCtx) {{
        audioCtx.close();
        audioCtx = null;
        analyser = null;
    }}
    setState('idle', 'TAP MIC TO START');
}}

// --- Handle speech results ---
let speechTimeout = null;
let finalTranscript = '';

function handleSpeechResult(event) {{
    let interim = '';
    finalTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {{
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) {{
            finalTranscript += t;
        }} else {{
            interim += t;
        }}
    }}

    // Show interim text
    if (interim) {{
        statusEl.textContent = interim;
    }}

    // When we get a final result, send it
    if (finalTranscript.trim()) {{
        clearTimeout(speechTimeout);
        speechTimeout = setTimeout(() => {{
            sendToAI(finalTranscript.trim());
        }}, 500);
    }}
}}

// --- Send to CLM server and speak response ---
async function sendToAI(text) {{
    // Pause recognition while AI responds
    if (recognition) {{
        try {{ recognition.stop(); }} catch(e) {{}}
    }}

    addMessage('user', text);
    setState('thinking', 'THINKING...');

    try {{
        const resp = await fetch(CLM_URL + '/chat', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ message: text, emotions: [] }}),
        }});
        const data = await resp.json();
        const response = data.response;
        const provider = data.llm_provider || 'ai';
        const latency = data.latency_ms || '?';

        const providerLabel = provider === 'claude' ? 'Claude' : 'ChatGPT';
        addMessage('ai', response, providerLabel + ' · ' + latency + 'ms');

        // Speak the response
        setState('speaking', 'SPEAKING...');
        await speakText(response);

    }} catch (err) {{
        addMessage('ai', 'Error: Could not reach the server.', '');
    }}

    // Resume listening
    if (isListening) {{
        setState('listening', 'LISTENING...');
        try {{
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.onresult = handleSpeechResult;
            recognition.onend = () => {{
                if (isListening) {{
                    try {{ recognition.start(); }} catch(e) {{}}
                }}
            }};
            recognition.start();
        }} catch(e) {{}}
    }} else {{
        setState('idle', 'TAP MIC TO START');
    }}
}}

// --- Text-to-Speech ---
function speakText(text) {{
    return new Promise((resolve) => {{
        if (!window.speechSynthesis) {{
            resolve();
            return;
        }}
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.onend = resolve;
        utterance.onerror = resolve;
        window.speechSynthesis.speak(utterance);
    }});
}}

// --- Start idle animation ---
drawIdle();
</script>
</body>
</html>
"""
