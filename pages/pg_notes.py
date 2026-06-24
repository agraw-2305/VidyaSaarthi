"""
ShikshaAI — pages/pg_notes.py
Notes page: topics sidebar + structured notes content + visual diagram.
"""

import streamlit as st
import os
from pages.shared import (
    init_state, load_css, render_header, render_sidebar_nav, process, play
)

init_state()
load_css()
render_header()

parsed      = st.session_state.parsed
quiz_active = st.session_state.quiz_active
audio_path  = st.session_state.audio_path
autoplay    = st.session_state.autoplay

# ── Handle topic clicks via query params ──────────────────────────────────────
if "topic" in st.query_params:
    topic = st.query_params["topic"]
    st.query_params.clear()
    process(topic)
    st.rerun()

# ── Main Layout ───────────────────────────────────────────────────────────────
if parsed and not quiz_active:
    topic    = parsed.get("topic_title", "Concept Details")
    intro    = parsed.get("notes_intro", "")
    concepts = parsed.get("notes_key_concepts", [])
    points   = parsed.get("notes_important_points", [])
    examples = parsed.get("notes_examples", [])
    summary  = parsed.get("notes_summary", "")
    visual   = st.session_state.visual

    # Two-column: sidebar + content
    col_sidebar, col_content = st.columns([1, 3], gap="medium")

    with col_sidebar:
        st.markdown('<div class="sa-card">', unsafe_allow_html=True)
        st.markdown('<div class="sa-card-title" style="margin-bottom:0.8rem;">Topics</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="topics-sidebar">', unsafe_allow_html=True)

        for t in st.session_state.recent_topics:
            active_cls = "active-topic" if t.lower() == topic.lower() or t.lower() in topic.lower() else ""
            # Use query params for topic switching
            encoded = t.replace(" ", "+")
            st.markdown(
                f'<a href="?topic={encoded}" class="topic-pill {active_cls}" target="_self">{t}</a>',
                unsafe_allow_html=True
            )

        st.markdown('</div></div>', unsafe_allow_html=True)

    with col_content:
        # Topic title
        st.markdown(f'<div class="notes-title">{topic}</div>', unsafe_allow_html=True)

        # Intro text
        st.markdown(f'<div class="notes-intro">{intro}</div>', unsafe_allow_html=True)

        # Visual diagram
        if visual and visual.get("type") != "none":
            st.markdown('<div class="notes-visual-marker"></div>', unsafe_allow_html=True)
            from visuals.visual_manager import render_visual
            render_visual(visual)

        # Key Points
        if points:
            st.markdown('<div class="key-points-title">Key Points</div>', unsafe_allow_html=True)
            for p in points:
                st.markdown(f"""
                <div class="key-point-item">
                    <span class="key-point-check">✓</span>
                    <span>{p}</span>
                </div>
                """, unsafe_allow_html=True)

        # Key Concepts
        if concepts:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="key-points-title">Key Concepts</div>', unsafe_allow_html=True)
            for c in concepts:
                st.markdown(f"""
                <div class="key-point-item">
                    <span class="key-point-check">💡</span>
                    <span>{c}</span>
                </div>
                """, unsafe_allow_html=True)

        # Examples
        if examples:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="key-points-title">Examples</div>', unsafe_allow_html=True)
            for e in examples:
                st.markdown(f"""
                <div class="key-point-item">
                    <span class="key-point-check">📌</span>
                    <span>{e}</span>
                </div>
                """, unsafe_allow_html=True)

        # Summary
        if summary:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="sa-card" style="background:#F0FDF4; border-color:#BBF7D0;">
                <div class="sa-card-title" style="color:#166534;">📊 Summary</div>
                <div class="sa-card-sub" style="color:#15803D;">{summary}</div>
            </div>
            """, unsafe_allow_html=True)

        # Audio playback
        play(audio_path, autoplay)

else:
    # No content yet — show placeholder
    st.markdown("""
    <div class="visual-placeholder" style="padding:5rem 2rem; margin-top:2rem;">
        <span class="visual-ph-icon">📝</span>
        <div class="visual-ph-label">Study Notes Workspace</div>
        <div class="visual-ph-sub">No notes yet — ask a question on the Home page first.</div>
    </div>
    """, unsafe_allow_html=True)

render_sidebar_nav(__file__)
