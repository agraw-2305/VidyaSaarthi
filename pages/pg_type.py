"""
ShikshaAI — pages/pg_type.py
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
    if st.session_state.get("quiz_active"):
        st.switch_page("pages/pg_quiz.py")
    else:
        st.switch_page("pages/pg_notes.py")
elif submitted:
    st.warning("Please type a question first.")

# ── Quick suggestions ─────────────────────────────────────────────────────────
st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="try-asking-title">💡 Quick suggestions</div>
<div class="suggestion-grid">
    <a href="?ask=Explain+Photosynthesis" class="suggestion-card" target="_self">
        <span class="suggestion-icon">🍃</span>
        <span>Explain Photosynthesis</span>
    </a>
    <a href="?ask=How+does+the+Human+Heart+work%3F" class="suggestion-card" target="_self">
        <span class="suggestion-icon">❤️</span>
        <span>How does the Human Heart work?</span>
    </a>
    <a href="?ask=Explain+the+Water+Cycle" class="suggestion-card" target="_self">
        <span class="suggestion-icon">💧</span>
        <span>Explain the Water Cycle</span>
    </a>
    <a href="?ask=What+is+Cell+Structure%3F" class="suggestion-card" target="_self">
        <span class="suggestion-icon">🔬</span>
        <span>What is Cell Structure?</span>
    </a>
</div>
""", unsafe_allow_html=True)

# Handle suggestion clicks
if "ask" in st.query_params:
    q = st.query_params["ask"]
    st.query_params.clear()
    process(q)
    if st.session_state.get("quiz_active"):
        st.switch_page("pages/pg_quiz.py")
    else:
        st.switch_page("pages/pg_notes.py")

# ── Tip ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tip-bar">
    💡 <strong>Tip:</strong> Ask in Hindi, English or Hinglish. I will explain with simple words and visuals.
</div>
""", unsafe_allow_html=True)

render_sidebar_nav(__file__)
