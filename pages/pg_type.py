"""
VidyaSaarthi — pages/pg_type.py
Text input mode: Type your question and get AI-generated explanations.
"""

import streamlit as st
import os
from pages.shared import (
    init_state, load_css, render_header, render_sidebar_nav, process
)

init_state()
load_css()
render_header()

st.markdown("""
<div class="sa-card">
    <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.5rem;">
        <div class="sa-chip chip-blue">⌨️</div>
        <div>
            <div class="sa-card-title">Type Your Question</div>
            <div class="sa-card-sub">Type any topic or question and get AI-powered explanations with visuals</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Text input
query = st.text_input(
    "Your question",
    placeholder="e.g. What is Photosynthesis? / Explain Newton's Laws / How does the heart work?",
    key="type_query_input",
    label_visibility="collapsed",
)

c1, c2 = st.columns([3, 1])
with c2:
    submitted = st.button("🚀 Get Answer", key="type_submit", use_container_width=True,
                          type="primary")

if submitted and query.strip():
    process(query.strip())
elif submitted:
    st.warning("Please type a question first.")

# ── Quick suggestions ─────────────────────────────────────────────────────────
st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
text_lang = st.session_state.text_language
audio_lang = st.session_state.audio_language
st.markdown('<div class="try-asking-title">💡 Quick suggestions</div>', unsafe_allow_html=True)
sc1, sc2 = st.columns(2)
with sc1:
    if st.button("🍃 Explain Photosynthesis", use_container_width=True, key="type_sug_1"):
        process("Explain Photosynthesis")
    if st.button("💧 Explain the Water Cycle", use_container_width=True, key="type_sug_3"):
        process("Explain the Water Cycle")
with sc2:
    if st.button("❤️ How does the Human Heart work?", use_container_width=True, key="type_sug_2"):
        process("How does the Human Heart work?")
    if st.button("🔬 What is Cell Structure?", use_container_width=True, key="type_sug_4"):
        process("What is Cell Structure?")

# ── Tip ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tip-bar">
    💡 <strong>Tip:</strong> Ask in Hindi, English or Hinglish. I will explain with simple words and visuals.
</div>
""", unsafe_allow_html=True)

render_sidebar_nav(__file__)
