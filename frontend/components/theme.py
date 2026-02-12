"""
Atmos Design System
=====================
Central source of truth for colors, fonts, provider configs, and all
CSS overrides. Every other frontend module imports from here.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

PROVIDER_CONFIG = {
    "claude": {
        "name": "Claude",
        "org": "Anthropic",
        "color": "#E8622C",
        "glow": "rgba(232, 98, 44, 0.12)",
        "model": "claude-3-haiku",
    },
    "openai": {
        "name": "ChatGPT",
        "org": "OpenAI",
        "color": "#00C9A7",
        "glow": "rgba(0, 201, 167, 0.12)",
        "model": "gpt-4o-mini",
    },
}

# ---------------------------------------------------------------------------
# Core palette
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#06070d",
    "surface": "#0d0f17",
    "surface_alt": "#111322",
    "border": "#1a1d2e",
    "border_light": "#252940",
    "text": "#e2e4ed",
    "text_secondary": "#8b8fa3",
    "text_muted": "#565a6e",
}

# ---------------------------------------------------------------------------
# Font imports (Google Fonts via @import inside <style>)
# ---------------------------------------------------------------------------

_FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Syne:wght@600;700;800&"
    "family=Outfit:wght@300;400;500;600&"
    "family=IBM+Plex+Mono:wght@400;500&"
    "display=swap');"
)

# ---------------------------------------------------------------------------
# inject_theme_css — call once after set_page_config
# ---------------------------------------------------------------------------

def inject_theme_css(provider: str = "claude"):
    """Inject the full Atmos theme into the Streamlit app."""
    cfg = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["claude"])
    accent = cfg["color"]
    glow = cfg["glow"]

    css = f"""
    <style>
    {_FONT_IMPORT}
    /* ── Base ──────────────────────────────────────────────── */
    .stApp {{
        background: {COLORS['bg']};
        color: {COLORS['text']};
        font-family: 'Outfit', sans-serif;
    }}

    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(
            ellipse 80% 60% at 50% 20%,
            {glow},
            transparent 70%
        );
        pointer-events: none;
        z-index: 0;
        transition: background 0.6s ease;
    }}

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: {COLORS['surface']} !important;
        border-right: 1px solid {COLORS['border']} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {COLORS['text']} !important;
    }}

    /* ── Tabs ─────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid {COLORS['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {COLORS['text_secondary']};
        border-radius: 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        padding: 8px 18px;
        border: none !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background: {COLORS['surface_alt']};
        color: {COLORS['text']};
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: {COLORS['surface_alt']} !important;
        color: {accent} !important;
        border: 1px solid {COLORS['border_light']} !important;
        box-shadow: 0 0 12px {glow};
    }}
    /* hide default tab underline */
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ── Chat messages ────────────────────────────────────── */
    [data-testid="stChatMessage"] {{
        background: {COLORS['surface']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 8px;
    }}

    /* ── Text input ───────────────────────────────────────── */
    .stTextInput > div > div {{
        background: {COLORS['surface']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 10px !important;
        color: {COLORS['text']} !important;
        font-family: 'Outfit', sans-serif !important;
    }}
    .stTextInput > div > div:focus-within {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 2px {glow} !important;
    }}
    .stTextInput input {{
        color: {COLORS['text']} !important;
    }}
    .stTextInput input::placeholder {{
        color: {COLORS['text_muted']} !important;
    }}

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button {{
        background: {COLORS['surface_alt']} !important;
        color: {COLORS['text']} !important;
        border: 1px solid {COLORS['border_light']} !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        background: {COLORS['border_light']} !important;
        border-color: {accent} !important;
        box-shadow: 0 0 12px {glow} !important;
    }}

    /* ── Audio input ──────────────────────────────────────── */
    [data-testid="stAudioInput"] {{
        background: {COLORS['surface']} !important;
        border: 2px solid {accent}44 !important;
        border-radius: 16px !important;
        padding: 12px 16px !important;
        max-width: 420px !important;
        margin: 0 auto !important;
        box-shadow: 0 0 24px {glow}, 0 0 48px {accent}08 !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }}
    [data-testid="stAudioInput"]:hover {{
        border-color: {accent}88 !important;
        box-shadow: 0 0 32px {glow}, 0 0 64px {accent}12 !important;
    }}

    /* ── Expander ─────────────────────────────────────────── */
    [data-testid="stExpander"] {{
        background: {COLORS['surface']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary {{
        color: {COLORS['text']} !important;
    }}

    /* ── Divider ──────────────────────────────────────────── */
    hr {{
        border-color: {COLORS['border']} !important;
        opacity: 0.5;
    }}

    /* ── Spinner / status ─────────────────────────────────── */
    [data-testid="stStatusWidget"] {{
        background: {COLORS['surface']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 10px !important;
    }}

    /* ── Caption / small text ─────────────────────────────── */
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {COLORS['text_muted']} !important;
    }}

    /* ── Markdown text inside main area ───────────────────── */
    .stMarkdown {{
        color: {COLORS['text']};
    }}

    /* ── Warning / error boxes ────────────────────────────── */
    [data-testid="stAlert"] {{
        background: {COLORS['surface']} !important;
        border-radius: 10px !important;
    }}

    /* ── Scrollbar ────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS['bg']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['border_light']};
        border-radius: 3px;
    }}

    /* ── Toggle switch ────────────────────────────────────── */
    [data-testid="stToggle"] label span {{
        color: {COLORS['text_secondary']} !important;
    }}

    /* ── Code blocks ──────────────────────────────────────── */
    code, pre {{
        background: {COLORS['surface_alt']} !important;
        color: {COLORS['text']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }}

    /* ── Tables ───────────────────────────────────────────── */
    table {{
        border-collapse: collapse;
    }}
    th {{
        background: {COLORS['surface_alt']} !important;
        color: {COLORS['text']} !important;
        border: 1px solid {COLORS['border']} !important;
        padding: 8px 12px !important;
    }}
    td {{
        background: {COLORS['surface']} !important;
        color: {COLORS['text_secondary']} !important;
        border: 1px solid {COLORS['border']} !important;
        padding: 8px 12px !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def hero_header_html() -> str:
    """Animated gradient hero title."""
    cfg_c = PROVIDER_CONFIG["claude"]
    cfg_o = PROVIDER_CONFIG["openai"]
    return f"""
    <div style="text-align:center; padding:1.2rem 0 1.5rem 0; position:relative; z-index:1;">
        <h1 style="
            font-family:'Syne',sans-serif;
            font-weight:800;
            font-size:2.4rem;
            letter-spacing:-0.02em;
            background:linear-gradient(135deg, {cfg_c['color']}, {cfg_o['color']});
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            background-clip:text;
            margin:0 0 6px 0;
            animation:atmos_shimmer 4s ease-in-out infinite alternate;
        ">Voice AI Demo</h1>
        <p style="
            font-family:'Outfit',sans-serif;
            color:{COLORS['text_secondary']};
            font-size:1.05rem;
            font-weight:300;
            margin:0;
            letter-spacing:0.01em;
        ">Explore how AI understands and responds to language</p>
    </div>
    <style>
    @keyframes atmos_shimmer {{
        0% {{ filter:brightness(1); }}
        50% {{ filter:brightness(1.15); }}
        100% {{ filter:brightness(1); }}
    }}
    </style>
    """


def provider_badge_html(provider: str) -> str:
    """Inline colored pill badge for use inside chat messages."""
    cfg = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["claude"])
    return (
        f'<span style="'
        f"background:{cfg['color']}22;"
        f"color:{cfg['color']};"
        f"padding:2px 10px;"
        f"border-radius:10px;"
        f"font-size:0.8rem;"
        f"font-weight:600;"
        f"font-family:'IBM Plex Mono',monospace;"
        f"letter-spacing:0.03em;"
        f'">{cfg["name"]}</span>'
    )


def provider_card_html(provider: str, active: bool = True) -> str:
    """Sidebar identity card for a provider — glowing if active, dimmed if not."""
    cfg = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["claude"])
    if active:
        border = f"1px solid {cfg['color']}55"
        bg = f"{cfg['color']}12"
        opacity = "1"
        shadow = f"0 0 20px {cfg['glow']}"
        name_color = cfg["color"]
    else:
        border = f"1px solid {COLORS['border']}"
        bg = COLORS["surface"]
        opacity = "0.45"
        shadow = "none"
        name_color = COLORS["text_muted"]

    return f"""
    <div style="
        background:{bg};
        border:{border};
        border-radius:12px;
        padding:10px 14px;
        margin-bottom:8px;
        opacity:{opacity};
        box-shadow:{shadow};
        transition:all 0.3s ease;
    ">
        <div style="
            font-family:'Syne',sans-serif;
            font-weight:700;
            font-size:1rem;
            color:{name_color};
        ">{cfg['name']}</div>
        <div style="
            font-family:'IBM Plex Mono',monospace;
            font-size:0.7rem;
            color:{COLORS['text_muted']};
            margin-top:2px;
        ">{cfg['org']} &middot; {cfg['model']}</div>
    </div>
    """


def status_dot_html(connected: bool) -> str:
    """Pulsing status indicator dot."""
    if connected:
        color = "#22c55e"
        label = "Connected"
        pulse = (
            "animation:atmos_pulse 2s ease-in-out infinite;"
        )
    else:
        color = "#ef4444"
        label = "Offline"
        pulse = ""

    return f"""
    <div style="display:flex;align-items:center;gap:8px;padding:4px 0;">
        <span style="
            display:inline-block;
            width:8px;height:8px;
            background:{color};
            border-radius:50%;
            {pulse}
        "></span>
        <span style="
            font-family:'IBM Plex Mono',monospace;
            font-size:0.78rem;
            color:{COLORS['text_secondary']};
        ">{label}</span>
    </div>
    <style>
    @keyframes atmos_pulse {{
        0%,100% {{ opacity:1; box-shadow:0 0 4px {color}; }}
        50% {{ opacity:0.5; box-shadow:0 0 8px {color}; }}
    }}
    </style>
    """
