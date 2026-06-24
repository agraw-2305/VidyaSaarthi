"""
ShikshaAI — pages/pg_home.py
Home page: Centered Voice-First Classroom Hero view with suggestions.
"""

import streamlit as st
import os
from pages.shared import (
    init_state, load_css, render_header, render_sidebar_nav, process
)

init_state()
load_css()
render_header()

lang = st.session_state.language
mode = st.session_state.input_mode

# ── Handle suggestion card clicks via query params ────────────────────────────
if "ask" in st.query_params:
    q = st.query_params["ask"]
    st.query_params.clear()
    process(q)
    if st.session_state.get("quiz_active"):
        st.switch_page("pages/pg_quiz.py")
    else:
        st.switch_page("pages/pg_notes.py")

# ── Centered Greeting (Marker class activates centered flex styles) ───────────
st.markdown("""
<div class="home-page-marker"></div>
<div class="home-greeting">
    <div class="home-greeting-title">Namaste!</div>
    <div class="home-greeting-sub">I'm your AI Teaching Assistant</div>
</div>
""", unsafe_allow_html=True)

# ── Microphone Trigger HTML ───────────────────────────────────────────────────
mic_html = """
<div class="mic-container">
    <div class="mic-pulse r1"></div>
    <div class="mic-pulse r2"></div>
    <div class="mic-pulse r3"></div>
    <div class="mic-btn">
        <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/>
        </svg>
    </div>
</div>
"""

# Voice mode trigger block
st.markdown('<div class="mic-rec-container">', unsafe_allow_html=True)
st.markdown(mic_html, unsafe_allow_html=True)
try:
    from audiorecorder import audiorecorder
    rec = audiorecorder("🎤 Speak", "⏹ Stop & Process", key="audio_rec")
    if len(rec) > 0:
        in_path = "temp/input.wav"
        rec.export(in_path, format="wav")
        from speech.stt import speech_to_text
        with st.spinner("Transcribing..."):
            txt = speech_to_text(in_path)
        if txt.strip() and not txt.startswith("["):
            process(txt.strip())
            if st.session_state.get("quiz_active"):
                st.switch_page("pages/pg_quiz.py")
            else:
                st.switch_page("pages/pg_notes.py")
        else:
            st.warning("Could not recognize speech. Please try again.")
except Exception as e:
    st.error(f"Mic error: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# ── Tap To Speak Label & Languages Subtext ────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin-top: 1rem;">
    <div style="font-size: 1.3rem; font-weight: 700; color: #2563EB;">Tap To Speak</div>
    <div style="font-size: 0.95rem; color: #64748B; margin-top: 0.3rem; font-weight: 500;">Hindi • English • Hinglish</div>
</div>
""", unsafe_allow_html=True)

# Centered typing mode option
st.markdown('<div style="display: flex; justify-content: center; margin-top: 1rem;">', unsafe_allow_html=True)
if st.button("⌨️ Ask by Typing", key="home_ask_typing"):
    st.switch_page("pages/pg_type.py")
st.markdown('</div>', unsafe_allow_html=True)

# ── Suggestion Chips ──────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin-top: 2.8rem; width: 100%;">
    <div style="font-size: 1.1rem; font-weight: 600; color: #475569; margin-bottom: 1rem;">Try Asking:</div>
    <div class="suggestion-chips-container">
        <a href="?ask=Explain+TCP+Handshake" class="suggestion-chip" target="_self">Explain TCP Handshake</a>
        <a href="?ask=Explain+Photosynthesis" class="suggestion-chip" target="_self">Explain Photosynthesis</a>
        <a href="?ask=What+is+Solar+System%3F" class="suggestion-chip" target="_self">Show Solar System Diagram</a>
        <a href="?ask=Explain+Newton%27s+Laws" class="suggestion-chip" target="_self">Explain Newton's Laws</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar Nav ───────────────────────────────────────────────────────────────
render_sidebar_nav(__file__)
