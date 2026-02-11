"""
Pipeline Display Component
============================
Real-time visualization of each step in the voice pipeline.
Shows: Listening → Transcribed → Thinking → Speaking
Plus emotion/prosody data visualization.
"""

import streamlit as st


# Stage display configuration
STAGE_CONFIG = {
    "idle": {
        "icon": "",
        "label": "Ready",
        "color": "#6B7280",
        "description": "Waiting for voice input...",
    },
    "listening": {
        "icon": "",
        "label": "Listening...",
        "color": "#3B82F6",
        "description": "Hume EVI is capturing your voice",
    },
    "transcribed": {
        "icon": "",
        "label": "Transcribed",
        "color": "#8B5CF6",
        "description": "Speech converted to text by Hume",
    },
    "thinking": {
        "icon": "",
        "label": "Claude Thinking...",
        "color": "#F59E0B",
        "description": "Claude API is generating a response",
    },
    "speaking": {
        "icon": "",
        "label": "Speaking",
        "color": "#10B981",
        "description": "Hume EVI is speaking the response",
    },
}


def render_pipeline_status(state: dict):
    """Render the current pipeline stage with a step indicator."""

    stage = state.get("stage", "idle")
    config = STAGE_CONFIG.get(stage, STAGE_CONFIG["idle"])

    # Stage progress bar
    stages = ["idle", "listening", "transcribed", "thinking", "speaking"]
    current_idx = stages.index(stage) if stage in stages else 0

    st.markdown("### Pipeline Status")

    # Render step indicators
    cols = st.columns(5)
    for i, (s, col) in enumerate(zip(stages, cols)):
        s_config = STAGE_CONFIG[s]
        if i < current_idx:
            status = "complete"
        elif i == current_idx:
            status = "active"
        else:
            status = "pending"

        with col:
            if status == "complete":
                st.markdown(f"**{s_config['label']}**")
            elif status == "active":
                st.markdown(
                    f"<div style='padding:8px; border-radius:8px; "
                    f"border: 2px solid {s_config['color']}; text-align:center;'>"
                    f"<strong>{s_config['icon']} {s_config['label']}</strong></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='color:#9CA3AF; text-align:center;'>"
                    f"{s_config['label']}</div>",
                    unsafe_allow_html=True,
                )

    # Current stage detail
    st.caption(config["description"])

    # Latency display
    if state.get("latency_ms"):
        st.metric("Claude Response Latency", f"{state['latency_ms']} ms")


def render_transcript_display(state: dict):
    """Show the current transcript and response."""

    transcript = state.get("transcript", "")
    response = state.get("response", "")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### You Said")
        if transcript:
            st.info(transcript)
        else:
            st.markdown("_Waiting for speech..._")

    with col2:
        st.markdown("#### Claude Responded")
        if response:
            st.success(response)
        else:
            st.markdown("_Waiting for response..._")


def render_emotion_display(state: dict):
    """Render the prosody/emotion detection data from Hume."""

    emotions = state.get("emotions", [])

    st.markdown("### Emotion / Prosody Detection")
    st.caption("Hume analyzes your voice tone to detect emotional signals — this goes beyond just words.")

    if not emotions:
        st.markdown("_No emotion data yet. Speak to see prosody analysis._")
        return

    # Sort by score descending and show top emotions
    sorted_emotions = sorted(emotions, key=lambda e: e.get("score", 0), reverse=True)

    # Top 3 as highlighted metrics
    top_3 = sorted_emotions[:3]
    cols = st.columns(3)
    for col, emotion in zip(cols, top_3):
        with col:
            st.metric(
                label=emotion["name"].replace("_", " ").title(),
                value=f"{emotion['score']:.1%}",
            )

    # Full emotion breakdown as a bar chart
    if len(sorted_emotions) > 3:
        with st.expander("All Detected Emotions", expanded=False):
            for emotion in sorted_emotions:
                score = emotion.get("score", 0)
                name = emotion["name"].replace("_", " ").title()
                bar_width = int(score * 100)
                st.markdown(
                    f"**{name}** ({score:.1%})"
                    f"<div style='background:#E5E7EB; border-radius:4px; height:8px; width:100%;'>"
                    f"<div style='background:#6366F1; border-radius:4px; height:8px; "
                    f"width:{bar_width}%;'></div></div>",
                    unsafe_allow_html=True,
                )


def render_interaction_history(history: list[dict]):
    """Render the history of all interactions in the session."""

    st.markdown("### Conversation History")

    if not history:
        st.markdown("_No interactions yet._")
        return

    for i, interaction in enumerate(reversed(history)):
        with st.container():
            cols = st.columns([3, 3, 1])
            with cols[0]:
                st.markdown(f"**You:** {interaction.get('transcript', '')}")
            with cols[1]:
                st.markdown(f"**Claude:** {interaction.get('response', '')}")
            with cols[2]:
                latency = interaction.get("latency_ms")
                if latency:
                    st.caption(f"{latency}ms")

            # Show top emotion for this interaction
            emotions = interaction.get("emotions", [])
            if emotions:
                top = sorted(emotions, key=lambda e: e.get("score", 0), reverse=True)[0]
                st.caption(f"Detected mood: {top['name'].replace('_', ' ').title()} ({top['score']:.0%})")

            st.divider()
