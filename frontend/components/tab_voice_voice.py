"""
Tab 3: Voice to Voice — Live Hume EVI  (Atmos theme)
======================================================
True real-time voice conversation powered by Hume EVI.
Browser connects directly to Hume's WebSocket for
mic capture, speech detection, TTS, and interruption.
"""

import base64
import os
import time

import httpx
import streamlit as st
import streamlit.components.v1 as components

from components.theme import PROVIDER_CONFIG, COLORS


# ---------------------------------------------------------------------------
# Hume OAuth2 token
# ---------------------------------------------------------------------------

def _get_hume_access_token() -> str | None:
    """Generate a Hume access token via OAuth2 client credentials.

    Caches in session_state for up to 25 minutes (tokens valid ~30 min).
    """
    cached = st.session_state.get("_hume_token")
    cached_time = st.session_state.get("_hume_token_time", 0)
    if cached and (time.time() - cached_time) < 25 * 60:
        return cached

    api_key = os.getenv("HUME_API_KEY", "")
    secret_key = os.getenv("HUME_SECRET_KEY", "")
    if not api_key or not secret_key:
        return None

    creds = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                "https://api.hume.ai/oauth2-cc/token",
                headers={
                    "Authorization": f"Basic {creds}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                content="grant_type=client_credentials",
            )
            resp.raise_for_status()
            token = resp.json().get("access_token")
    except Exception:
        return None

    if token:
        st.session_state["_hume_token"] = token
        st.session_state["_hume_token_time"] = time.time()
    return token


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render_voice_voice_tab(
    clm_url: str,
    clm_connected: bool,
    pipeline_state: dict,
    history: list[dict],
):
    """Render the live Voice-to-Voice tab powered by Hume EVI."""

    api_key = os.getenv("HUME_API_KEY", "")
    secret_key = os.getenv("HUME_SECRET_KEY", "")
    config_id = os.getenv("HUME_CONFIG_ID", "")

    if not all([api_key, secret_key, config_id]):
        st.warning(
            "**Hume EVI not configured.** Add `HUME_API_KEY`, "
            "`HUME_SECRET_KEY`, and `HUME_CONFIG_ID` to your `.env` file.\n\n"
            "Get credentials at [platform.hume.ai](https://platform.hume.ai/)"
        )
        return

    token = _get_hume_access_token()
    if not token:
        st.error("Failed to get Hume access token. Check your API key and secret key.")
        return

    provider = st.session_state.get("active_provider", "claude")
    cfg = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["claude"])

    html = _build_evi_html(
        access_token=token,
        config_id=config_id,
        provider_name=cfg["name"],
        provider_color=cfg["color"],
    )
    components.html(html, height=700, scrolling=False)


# ---------------------------------------------------------------------------
# HTML builder
# ---------------------------------------------------------------------------

def _build_evi_html(
    access_token: str,
    config_id: str,
    provider_name: str,
    provider_color: str,
) -> str:
    """Build the complete self-contained HTML/CSS/JS for the live EVI widget."""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Outfit:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:transparent; overflow:hidden; font-family:'Outfit',sans-serif; color:{COLORS['text']}; }}

#app {{
  display:flex; flex-direction:column; align-items:center;
  height:690px; padding:12px 20px 0 20px;
}}

/* ── Status bar ────────────────────────── */
#status-bar {{
  display:flex; align-items:center; justify-content:center; gap:10px;
  margin-bottom:8px; min-height:24px;
}}
#status-text {{
  font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
  letter-spacing:1.5px; text-transform:uppercase;
  color:{COLORS['text_muted']}; transition:color 0.3s;
}}
#provider-badge {{
  background:{provider_color}22; color:{provider_color};
  padding:2px 12px; border-radius:10px; font-size:0.7rem;
  font-weight:600; font-family:'IBM Plex Mono',monospace;
  letter-spacing:0.03em;
}}

/* ── Waveform ──────────────────────────── */
#waveform-wrap {{
  position:relative; width:100%; max-width:600px;
  background:{COLORS['surface']}; border:1px solid {COLORS['border_light']};
  border-radius:16px; padding:16px 20px;
  backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px);
  box-shadow:0 0 40px {provider_color}10, inset 0 0 60px {COLORS['bg']}40;
  transition:box-shadow 0.4s;
  margin-bottom:16px;
}}
#waveform-wrap.active {{
  box-shadow:0 0 50px {provider_color}25, 0 0 100px {provider_color}0a, inset 0 0 60px {COLORS['bg']}40;
}}
#waveform-glow {{
  position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
  width:320px; height:320px; border-radius:50%; pointer-events:none;
  background:radial-gradient(circle,{provider_color}0c,{provider_color}00);
  transition:all 0.5s;
}}
#waveform-wrap.active #waveform-glow {{
  width:400px; height:400px;
  background:radial-gradient(circle,{provider_color}28,{provider_color}00);
}}
canvas#waveform {{
  display:block; width:100%; height:150px; position:relative; z-index:1;
}}

/* ── Mic button ────────────────────────── */
#mic-area {{
  display:flex; flex-direction:column; align-items:center;
  margin-bottom:16px;
}}
#mic-btn {{
  width:80px; height:80px; border-radius:50%;
  background:transparent; border:2px solid {provider_color}44;
  cursor:pointer; position:relative;
  display:flex; align-items:center; justify-content:center;
  transition:all 0.3s ease; color:{COLORS['text_muted']};
  outline:none;
}}
#mic-btn:hover {{
  border-color:{provider_color}88;
  box-shadow:0 0 24px {provider_color}20;
  color:{COLORS['text']};
}}
#mic-btn svg {{ width:32px; height:32px; transition:color 0.3s; }}

/* Pulse ring behind mic when idle */
#mic-btn::before {{
  content:''; position:absolute; inset:-6px;
  border:2px solid {provider_color}30; border-radius:50%;
  animation:pulse-ring 2.5s ease-out infinite;
}}
@keyframes pulse-ring {{
  0% {{ transform:scale(1); opacity:0.7; }}
  100% {{ transform:scale(1.5); opacity:0; }}
}}

/* State-specific mic styles */
#mic-btn.connecting {{
  border-color:{provider_color}; color:{provider_color};
}}
#mic-btn.connecting::before {{ animation:none; opacity:0; }}

#mic-btn.listening {{
  border-color:{provider_color}; background:{provider_color}15;
  color:{provider_color}; box-shadow:0 0 30px {provider_color}25;
}}
#mic-btn.listening::before {{
  border-color:{provider_color}50;
  animation:pulse-ring 2s ease-out infinite;
}}

#mic-btn.thinking {{
  border-color:#F59E0B; background:#F59E0B15;
  color:#F59E0B; box-shadow:0 0 30px #F59E0B20;
}}
#mic-btn.thinking::before {{
  border-color:#F59E0B40;
  animation:pulse-ring 1.5s ease-out infinite;
}}

#mic-btn.speaking {{
  border-color:#10B981; background:#10B98115;
  color:#10B981; box-shadow:0 0 30px #10B98120;
}}
#mic-btn.speaking::before {{
  border-color:#10B98140;
  animation:pulse-ring 2s ease-out infinite;
}}

#mic-label {{
  font-family:'IBM Plex Mono',monospace; font-size:0.78rem;
  color:{COLORS['text_muted']}; margin-top:10px;
  letter-spacing:0.5px; transition:color 0.3s;
}}

/* ── Subtitles ─────────────────────────── */
#subtitles {{
  width:100%; max-width:600px; flex:1;
  overflow-y:auto; padding:4px 8px;
  scrollbar-width:thin; scrollbar-color:{COLORS['border_light']} transparent;
}}
#subtitles::-webkit-scrollbar {{ width:4px; }}
#subtitles::-webkit-scrollbar-thumb {{ background:{COLORS['border_light']}; border-radius:2px; }}

.sub {{
  opacity:0; transform:translateY(6px);
  transition:opacity 0.3s, transform 0.3s;
  margin-bottom:10px; padding:6px 0;
}}
.sub.show {{ opacity:1; transform:translateY(0); }}
.sub-label {{
  font-family:'IBM Plex Mono',monospace; font-size:0.63rem;
  letter-spacing:1px; text-transform:uppercase;
  color:{COLORS['text_muted']};
}}
.sub-text {{
  font-family:'Outfit',sans-serif; font-size:0.95rem;
  margin-top:2px; line-height:1.4;
}}
.sub-user {{ text-align:right; }}
.sub-user .sub-text {{ color:{COLORS['text']}; }}
.sub-ai {{ text-align:left; }}
.sub-ai .sub-text {{ color:{provider_color}; }}
.sub-divider {{
  height:1px; background:{COLORS['border']}; opacity:0.4;
  margin:4px 0 8px 0;
}}

/* ── Error overlay ─────────────────────── */
#error-overlay {{
  display:none; position:fixed; inset:0; z-index:100;
  background:rgba(6,7,13,0.85); backdrop-filter:blur(8px);
  flex-direction:column; align-items:center; justify-content:center;
  text-align:center; padding:30px;
}}
#error-overlay.show {{ display:flex; }}
#error-msg {{
  font-size:1rem; color:{COLORS['text']}; max-width:400px;
  margin-bottom:16px; line-height:1.5;
}}
#error-btn {{
  background:{COLORS['surface_alt']}; color:{COLORS['text']};
  border:1px solid {COLORS['border_light']}; border-radius:10px;
  padding:8px 24px; cursor:pointer; font-family:'Outfit',sans-serif;
  font-size:0.9rem; transition:all 0.2s;
}}
#error-btn:hover {{
  border-color:{provider_color}; box-shadow:0 0 12px {provider_color}20;
}}
</style>
</head>
<body>
<div id="app">
  <div id="status-bar">
    <span id="status-text">READY</span>
    <span id="provider-badge">{provider_name}</span>
  </div>

  <div id="waveform-wrap">
    <div id="waveform-glow"></div>
    <canvas id="waveform"></canvas>
  </div>

  <div id="mic-area">
    <button id="mic-btn" aria-label="Start voice conversation">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
      </svg>
    </button>
    <div id="mic-label">Tap to start</div>
  </div>

  <div id="subtitles"></div>
</div>

<div id="error-overlay">
  <div id="error-msg"></div>
  <button id="error-btn" onclick="dismissError()">Try Again</button>
</div>

<script>
// ── Config (injected by Python) ───────────────────────────
const ACCESS_TOKEN = "{access_token}";
const CONFIG_ID = "{config_id}";
const PROVIDER_NAME = "{provider_name}";
const PROVIDER_COLOR = "{provider_color}";

// ── State machine ─────────────────────────────────────────
const S = {{ IDLE:'idle', CONNECTING:'connecting', LISTENING:'listening',
             THINKING:'ai_thinking', SPEAKING:'ai_speaking' }};
let state = S.IDLE;

const micBtn   = document.getElementById('mic-btn');
const micLabel = document.getElementById('mic-label');
const statusEl = document.getElementById('status-text');
const wrapEl   = document.getElementById('waveform-wrap');
const subsEl   = document.getElementById('subtitles');

const labels = {{
  [S.IDLE]:       'Tap to start',
  [S.CONNECTING]: 'Connecting...',
  [S.LISTENING]:  'Listening...',
  [S.THINKING]:   'Thinking...',
  [S.SPEAKING]:   'Speaking...',
}};
const statusLabels = {{
  [S.IDLE]:       'READY',
  [S.CONNECTING]: 'CONNECTING',
  [S.LISTENING]:  'LISTENING',
  [S.THINKING]:   'PROCESSING',
  [S.SPEAKING]:   'RESPONDING',
}};
const btnClass = {{
  [S.IDLE]:       '',
  [S.CONNECTING]: 'connecting',
  [S.LISTENING]:  'listening',
  [S.THINKING]:   'thinking',
  [S.SPEAKING]:   'speaking',
}};

function setState(s) {{
  state = s;
  micBtn.className = btnClass[s] || '';
  micLabel.textContent = labels[s] || '';
  statusEl.textContent = statusLabels[s] || '';
  if (s === S.IDLE) {{
    wrapEl.classList.remove('active');
    statusEl.style.color = '';
  }} else {{
    wrapEl.classList.add('active');
  }}
}}

// ── Audio contexts & nodes ────────────────────────────────
let micStream = null;
let mediaRecorder = null;
let audioCtx = null;
let micAnalyser = null;
let playCtx = null;
let playAnalyser = null;
let ws = null;
let audioQueue = [];
let isPlaying = false;

// ── Mic button click ──────────────────────────────────────
micBtn.addEventListener('click', async () => {{
  if (state === S.IDLE) {{
    await startSession();
  }} else {{
    stopSession();
  }}
}});

async function startSession() {{
  // Check browser support
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
    showError('Your browser does not support microphone access. Use Chrome, Firefox, or Edge.');
    return;
  }}

  setState(S.CONNECTING);

  // Get mic
  try {{
    micStream = await navigator.mediaDevices.getUserMedia({{
      audio: {{ echoCancellation:true, noiseSuppression:true, autoGainControl:true }}
    }});
  }} catch (e) {{
    showError('Microphone access was denied. Please allow mic access in your browser and try again.');
    setState(S.IDLE);
    return;
  }}

  // Audio context for mic analyser (waveform vis)
  try {{
    audioCtx = new AudioContext();
    const source = audioCtx.createMediaStreamSource(micStream);
    micAnalyser = audioCtx.createAnalyser();
    micAnalyser.fftSize = 256;
    source.connect(micAnalyser);
  }} catch (e) {{
    // Non-fatal: waveform just won't animate
  }}

  // MediaRecorder to chunk mic audio — send as binary frames
  try {{
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus' : 'audio/webm';
    mediaRecorder = new MediaRecorder(micStream, {{ mimeType }});
    mediaRecorder.ondataavailable = async (ev) => {{
      if (ev.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {{
        // Send raw binary audio — Hume expects binary WebSocket frames
        const arrayBuf = await ev.data.arrayBuffer();
        ws.send(arrayBuf);
      }}
    }};
  }} catch (e) {{
    showError('Could not set up audio recording. Try a different browser.');
    cleanup();
    return;
  }}

  // Connect WebSocket to Hume EVI
  try {{
    const url = `wss://api.hume.ai/v0/evi/chat?access_token=${{ACCESS_TOKEN}}&config_id=${{CONFIG_ID}}`;
    ws = new WebSocket(url);
    ws.binaryType = 'arraybuffer';
  }} catch (e) {{
    showError('Could not connect to Hume. Check your internet connection.');
    cleanup();
    return;
  }}

  ws.onopen = () => {{
    // Send session settings to configure the AI's behavior
    ws.send(JSON.stringify({{
      type: 'session_settings',
      system_prompt: 'You are a helpful, empathetic voice assistant. '
        + 'Listen carefully to the user\\'s question and respond directly to what they asked. '
        + 'Keep responses concise and conversational (1-3 sentences) since they will be spoken aloud. '
        + 'Never introduce yourself or give a generic greeting unless the user greets you first. '
        + 'If the user asks a question, answer it. If they make a statement, respond to it naturally.'
    }}));
    setState(S.LISTENING);
    mediaRecorder.start(100);
  }};

  ws.onmessage = (ev) => {{
    // Binary frames = audio output from Hume
    if (ev.data instanceof ArrayBuffer) {{
      if (state !== S.SPEAKING) setState(S.SPEAKING);
      // Convert to base64 for our enqueue function
      const bytes = new Uint8Array(ev.data);
      audioQueue.push(bytes.buffer);
      if (!isPlaying) playNext();
      return;
    }}
    // Text frames = JSON messages
    try {{ handleMsg(JSON.parse(ev.data)); }} catch(e) {{ console.error('msg parse error', e); }}
  }};

  ws.onerror = () => {{
    showError('Connection error. Please try again.');
    cleanup();
  }};

  ws.onclose = (ev) => {{
    if (state !== S.IDLE) {{
      if (ev.code === 1008 || ev.code === 4001 || ev.code === 4000) {{
        showError('Session expired or invalid config. Click Try Again to reconnect.');
      }}
      cleanup();
    }}
  }};
}}

function stopSession() {{
  cleanup();
}}

function cleanup() {{
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {{
    try {{ mediaRecorder.stop(); }} catch(e) {{}}
  }}
  mediaRecorder = null;
  if (micStream) {{
    micStream.getTracks().forEach(t => t.stop());
    micStream = null;
  }}
  if (ws) {{
    try {{ ws.close(); }} catch(e) {{}}
    ws = null;
  }}
  stopPlayback();
  if (audioCtx) {{
    try {{ audioCtx.close(); }} catch(e) {{}}
    audioCtx = null;
    micAnalyser = null;
  }}
  setState(S.IDLE);
}}

// ── Message handler ───────────────────────────────────────
function handleMsg(msg) {{
  switch (msg.type) {{
    case 'user_message':
      if (msg.message && msg.message.content) {{
        addSub('user', msg.message.content);
      }}
      setState(S.THINKING);
      break;

    case 'assistant_message':
      if (msg.message && msg.message.content) {{
        addSub('ai', msg.message.content);
      }}
      break;

    case 'audio_output':
      if (state !== S.SPEAKING) setState(S.SPEAKING);
      if (msg.data) enqueueAudio(msg.data);
      break;

    case 'user_interruption':
      stopPlayback();
      setState(S.LISTENING);
      break;

    case 'assistant_end':
      waitForDrain();
      break;

    case 'error':
      console.error('Hume error:', msg);
      break;

    default:
      // chat_metadata, system messages, etc — ignore
      break;
  }}
}}

// ── Audio playback ────────────────────────────────────────
function enqueueAudio(b64) {{
  const raw = atob(b64);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  audioQueue.push(bytes.buffer);
  if (!isPlaying) playNext();
}}

function ensurePlayCtx() {{
  if (!playCtx || playCtx.state === 'closed') {{
    playCtx = new AudioContext();
    playAnalyser = playCtx.createAnalyser();
    playAnalyser.fftSize = 256;
    playAnalyser.connect(playCtx.destination);
  }}
  if (playCtx.state === 'suspended') playCtx.resume();
}}

async function playNext() {{
  if (audioQueue.length === 0) {{ isPlaying = false; return; }}
  isPlaying = true;
  ensurePlayCtx();

  const buf = audioQueue.shift();
  try {{
    // Try decodeAudioData first (handles mp3, wav, opus, etc.)
    const decoded = await playCtx.decodeAudioData(buf.slice(0));
    const src = playCtx.createBufferSource();
    src.buffer = decoded;
    src.connect(playAnalyser);
    src.onended = () => playNext();
    src.start();
  }} catch (e) {{
    // Fallback: treat as raw Linear16 PCM at 24kHz
    try {{
      const int16 = new Int16Array(buf);
      const float32 = new Float32Array(int16.length);
      for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768.0;
      const ab = playCtx.createBuffer(1, float32.length, 24000);
      ab.getChannelData(0).set(float32);
      const src = playCtx.createBufferSource();
      src.buffer = ab;
      src.connect(playAnalyser);
      src.onended = () => playNext();
      src.start();
    }} catch (e2) {{
      console.error('playback error', e2);
      playNext();
    }}
  }}
}}

function stopPlayback() {{
  audioQueue = [];
  isPlaying = false;
  if (playCtx) {{
    try {{ playCtx.close(); }} catch(e) {{}}
    playCtx = null;
    playAnalyser = null;
  }}
}}

function waitForDrain() {{
  const check = setInterval(() => {{
    if (!isPlaying && audioQueue.length === 0) {{
      clearInterval(check);
      if (state === S.SPEAKING) setState(S.LISTENING);
    }}
  }}, 100);
}}

// ── Helpers ───────────────────────────────────────────────
function blobToBase64(blob) {{
  return new Promise(resolve => {{
    const r = new FileReader();
    r.onloadend = () => resolve(r.result.split(',')[1]);
    r.readAsDataURL(blob);
  }});
}}

// ── Subtitles ─────────────────────────────────────────────
function addSub(role, text) {{
  const d = document.createElement('div');
  d.className = 'sub sub-' + role;

  const lbl = document.createElement('span');
  lbl.className = 'sub-label';
  lbl.textContent = role === 'user' ? 'YOU' : PROVIDER_NAME;

  const txt = document.createElement('div');
  txt.className = 'sub-text';
  txt.textContent = text;

  d.appendChild(lbl);
  d.appendChild(txt);

  // Divider before new entry (if not first)
  if (subsEl.children.length > 0) {{
    const div = document.createElement('div');
    div.className = 'sub-divider';
    subsEl.appendChild(div);
  }}

  subsEl.appendChild(d);
  requestAnimationFrame(() => d.classList.add('show'));
  subsEl.scrollTop = subsEl.scrollHeight;
}}

// ── Waveform (canvas) ─────────────────────────────────────
const canvas = document.getElementById('waveform');
const ctx2d = canvas.getContext('2d');
const BAR_COUNT = 64;
const BAR_W = 4;
let animId = null;

function initCanvas() {{
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx2d.scale(dpr, dpr);
  return {{ w: rect.width, h: rect.height }};
}}

function drawFrame() {{
  animId = requestAnimationFrame(drawFrame);
  const {{ w, h }} = {{ w: canvas.getBoundingClientRect().width, h: canvas.getBoundingClientRect().height }};
  ctx2d.clearRect(0, 0, w * 2, h * 2);

  const gap = Math.max(1, (w - BAR_COUNT * BAR_W) / (BAR_COUNT - 1));

  // Pick data source
  let analyser = null;
  let barColor = PROVIDER_COLOR;

  if ((state === S.LISTENING) && micAnalyser) {{
    analyser = micAnalyser;
    barColor = PROVIDER_COLOR;
  }} else if (state === S.SPEAKING && playAnalyser) {{
    analyser = playAnalyser;
    barColor = '#10B981';
  }} else if (state === S.THINKING) {{
    drawIdleBars(w, h, gap, '#F59E0B', 0.5);
    return;
  }} else if (state === S.CONNECTING) {{
    drawIdleBars(w, h, gap, PROVIDER_COLOR, 0.3);
    return;
  }}

  if (analyser) {{
    const bufLen = analyser.frequencyBinCount;
    const data = new Uint8Array(bufLen);
    analyser.getByteFrequencyData(data);

    for (let i = 0; i < BAR_COUNT; i++) {{
      const di = Math.floor((i / BAR_COUNT) * bufLen);
      const val = data[di] / 255;
      const center = BAR_COUNT / 2;
      const dist = Math.abs(i - center) / center;
      const env = 1 - Math.pow(dist, 1.4);
      const bh = Math.max(3, val * h * 0.85 * env);
      const x = i * (BAR_W + gap);
      const y = (h - bh) / 2;

      const grad = ctx2d.createLinearGradient(x, y + bh, x, y);
      grad.addColorStop(0, barColor + '60');
      grad.addColorStop(1, barColor);
      ctx2d.fillStyle = grad;
      ctx2d.beginPath();
      ctx2d.roundRect(x, y, BAR_W, bh, 2);
      ctx2d.fill();
    }}
  }} else {{
    drawIdleBars(w, h, gap, PROVIDER_COLOR, 0.2);
  }}
}}

function drawIdleBars(w, h, gap, color, intensity) {{
  const t = Date.now();
  for (let i = 0; i < BAR_COUNT; i++) {{
    const center = BAR_COUNT / 2;
    const dist = Math.abs(i - center) / center;
    const env = 1 - Math.pow(dist, 1.4);
    const phase = (i / BAR_COUNT) * Math.PI * 2;
    const breathe = 0.5 + 0.5 * Math.sin(t / 2000 + phase);
    const maxH = 22 * env;
    const bh = Math.max(3, maxH * (0.3 + 0.7 * breathe * intensity));
    const x = i * (BAR_W + gap);
    const y = (h - bh) / 2;
    ctx2d.fillStyle = color + '30';
    ctx2d.beginPath();
    ctx2d.roundRect(x, y, BAR_W, bh, 2);
    ctx2d.fill();
  }}
}}

// ── Error overlay ─────────────────────────────────────────
function showError(msg) {{
  document.getElementById('error-msg').textContent = msg;
  document.getElementById('error-overlay').classList.add('show');
}}
function dismissError() {{
  document.getElementById('error-overlay').classList.remove('show');
  cleanup();
}}

// ── Boot ──────────────────────────────────────────────────
initCanvas();
drawFrame();

window.addEventListener('resize', () => {{
  initCanvas();
}});
</script>
</body></html>"""
