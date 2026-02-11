"""
Animated Waveform Component
==============================
A CSS-animated audio waveform that reacts to pipeline state.
- Idle: flat bars, muted color
- Listening: gentle blue pulse (user speaking)
- Thinking: slow amber pulse (AI processing)
- Speaking: active green wave animation (AI talking)
"""

import streamlit as st


def render_waveform(stage: str = "idle", provider: str = "claude"):
    """Render an animated waveform bar that reacts to the current pipeline stage."""

    # Color and animation config per stage
    config = {
        "idle": {"color": "#9CA3AF", "speed": "0s", "label": "Ready"},
        "listening": {"color": "#3B82F6", "speed": "0.8s", "label": "Listening..."},
        "transcribed": {"color": "#8B5CF6", "speed": "0.6s", "label": "Transcribed"},
        "thinking": {"color": "#F59E0B", "speed": "1.2s", "label": "Thinking..."},
        "speaking": {"color": "#10B981", "speed": "0.4s", "label": "Speaking..."},
    }

    c = config.get(stage, config["idle"])
    color = c["color"]
    speed = c["speed"]
    label = c["label"]
    is_active = stage not in ("idle",)

    # Generate bar heights — different for each stage
    if stage == "idle":
        bars_html = _generate_bars(color, animate=False)
    elif stage == "listening":
        bars_html = _generate_bars(color, animate=True, intensity="low", speed=speed)
    elif stage == "thinking":
        bars_html = _generate_bars(color, animate=True, intensity="medium", speed=speed)
    elif stage == "speaking":
        bars_html = _generate_bars(color, animate=True, intensity="high", speed=speed)
    else:
        bars_html = _generate_bars(color, animate=True, intensity="low", speed=speed)

    # Provider indicator
    provider_color = "#7C3AED" if provider == "claude" else "#10A37F"
    provider_name = "Claude" if provider == "claude" else "ChatGPT"

    html = f"""
    <div style="
        background: #1a1a2e;
        border-radius: 16px;
        padding: 24px 32px;
        margin: 12px 0;
        text-align: center;
        position: relative;
        overflow: hidden;
    ">
        <!-- Subtle glow behind bars when active -->
        {"<div style='position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:200px; height:200px; background:radial-gradient(circle," + color + "22," + color + "00); border-radius:50%;'></div>" if is_active else ""}

        <!-- Status label -->
        <div style="
            color: {color};
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 16px;
            position: relative;
        ">
            {"<span style='display:inline-block; width:8px; height:8px; background:" + color + "; border-radius:50%; margin-right:8px; animation:glow 1s infinite;'></span>" if is_active else ""}
            {label}
        </div>

        <!-- Waveform bars -->
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 3px;
            height: 80px;
            position: relative;
        ">
            {bars_html}
        </div>

        <!-- Provider badge -->
        <div style="
            margin-top: 16px;
            display: inline-block;
            background: {provider_color}33;
            color: {provider_color};
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        ">
            {provider_name}
        </div>
    </div>

    <style>
        @keyframes glow {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
    </style>
    """

    st.markdown(html, unsafe_allow_html=True)


def _generate_bars(color: str, animate: bool = False, intensity: str = "low", speed: str = "0.8s") -> str:
    """Generate HTML for the waveform bars."""

    num_bars = 40

    # Base heights for each bar (creates a natural wave shape)
    import math
    bars = []

    for i in range(num_bars):
        # Create a bell-curve shape centered in the middle
        center = num_bars / 2
        dist = abs(i - center) / center
        base_height = max(4, int(60 * (1 - dist ** 1.5)))

        if not animate:
            # Idle — flat small bars
            height = max(3, int(base_height * 0.08))
            bars.append(
                f'<div style="'
                f'width:3px; height:{height}px; '
                f'background:{color}66; border-radius:2px; '
                f'transition: height 0.5s ease;'
                f'"></div>'
            )
        else:
            # Animated — different min/max based on intensity
            if intensity == "low":
                min_h = max(3, int(base_height * 0.1))
                max_h = max(8, int(base_height * 0.4))
            elif intensity == "medium":
                min_h = max(4, int(base_height * 0.15))
                max_h = max(12, int(base_height * 0.6))
            else:  # high
                min_h = max(5, int(base_height * 0.2))
                max_h = max(15, int(base_height * 0.95))

            # Stagger animation delay for wave effect
            delay = round((i / num_bars) * 0.8, 2)
            anim_name = f"wave_{i}"

            bars.append(
                f'<div style="'
                f'width:3px; min-height:{min_h}px; height:{max_h}px; '
                f'background:{color}; border-radius:2px; '
                f'animation: {anim_name} {speed} ease-in-out {delay}s infinite alternate;'
                f'"></div>'
                f'<style>@keyframes {anim_name} {{ '
                f'0% {{ height: {min_h}px; opacity: 0.6; }} '
                f'100% {{ height: {max_h}px; opacity: 1; }} '
                f'}}</style>'
            )

    return "\n".join(bars)


def render_waveform_mini(stage: str = "idle"):
    """A compact inline waveform for the Text+Voice tab audio playback."""

    config = {
        "idle": "#9CA3AF",
        "playing": "#10B981",
    }
    color = config.get(stage, config["idle"])
    is_active = stage == "playing"

    bars = []
    for i in range(12):
        if is_active:
            delay = round(i * 0.1, 2)
            bars.append(
                f'<div style="'
                f'width:2px; height:16px; background:{color}; border-radius:1px; '
                f'animation: miniwave_{i} 0.5s ease-in-out {delay}s infinite alternate;'
                f'"></div>'
                f'<style>@keyframes miniwave_{i} {{ '
                f'0% {{ height: 4px; }} 100% {{ height: 16px; }} }}</style>'
            )
        else:
            bars.append(
                f'<div style="width:2px; height:4px; background:{color}66; border-radius:1px;"></div>'
            )

    html = f"""
    <div style="display:flex; align-items:center; gap:2px; height:20px; margin:4px 0;">
        {"".join(bars)}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
