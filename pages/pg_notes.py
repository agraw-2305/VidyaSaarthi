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
    import html

    # Escape all parsed string values to prevent XSS
    topic    = html.escape(parsed.get("topic_title", "Concept Details"))
    learning_objs = [html.escape(x) for x in parsed.get("learning_objectives", [])]
    prereqs  = [html.escape(x) for x in parsed.get("prerequisites", [])]
    intro    = html.escape(parsed.get("notes_intro", ""))
    concepts = [html.escape(x) for x in parsed.get("notes_key_concepts", [])]
    points   = [html.escape(x) for x in parsed.get("notes_important_points", [])]
    examples = [html.escape(x) for x in parsed.get("notes_examples", [])]
    mistakes = [html.escape(x) for x in parsed.get("common_mistakes", [])]
    mem_tip  = html.escape(parsed.get("memory_tip", ""))
    fun_fact = html.escape(parsed.get("fun_fact", ""))
    real_life = [html.escape(x) for x in parsed.get("real_life_applications", [])]
    summary  = html.escape(parsed.get("notes_summary", ""))
    follow_up = [html.escape(x) for x in parsed.get("follow_up_questions", [])]
    visual   = st.session_state.visual

    # Two-column: sidebar + content
    col_sidebar, col_content = st.columns([1, 3], gap="medium")

    with col_sidebar:
        st.markdown('<div class="sa-card">', unsafe_allow_html=True)
        st.markdown('<div class="sa-card-title" style="margin-bottom:0.8rem;">Topics</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="topics-sidebar">', unsafe_allow_html=True)

        for t in st.session_state.recent_topics:
            is_active = t.lower() == topic.lower() or t.lower() in topic.lower()
            # If active, use primary button type for styling
            btn_type = "primary" if is_active else "secondary"
            if st.button(t, key=f"topic_btn_{t}", type=btn_type, use_container_width=True):
                process(t)
                st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

    with col_content:
        # Topic title
        st.markdown(f'<div class="notes-title">{topic}</div>', unsafe_allow_html=True)

        # Learning Objectives
        if learning_objs:
            st.markdown('<div class="learning-obj-container" style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:8px; margin-bottom:12px;">', unsafe_allow_html=True)
            st.markdown('<div style="color:#0F172A; font-weight:700; margin-bottom:8px;">🎯 Learning Objectives</div>', unsafe_allow_html=True)
            for lo in learning_objs:
                st.markdown(f'<div style="color:#475569; font-size:0.95rem; margin-bottom:4px;">• {lo}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Prerequisites
        if prereqs:
            st.markdown('<div class="prereq-container" style="background:#FFFBEB; border:1px solid #FDE68A; padding:12px; border-radius:8px; margin-bottom:16px;">', unsafe_allow_html=True)
            st.markdown('<div style="color:#B45309; font-weight:700; margin-bottom:8px;">📋 Prerequisites</div>', unsafe_allow_html=True)
            for pr in prereqs:
                st.markdown(f'<div style="color:#92400E; font-size:0.95rem; margin-bottom:4px;">• {pr}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

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

        # Common Mistakes
        if mistakes:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="key-points-title" style="color:#DC2626;">⚠️ Common Mistakes</div>', unsafe_allow_html=True)
            for m in mistakes:
                st.markdown(f"""
                <div class="key-point-item" style="background:#FEF2F2; border:1px solid #FECACA;">
                    <span class="key-point-check" style="color:#DC2626; background:transparent;">❌</span>
                    <span style="color:#991B1B;">{m}</span>
                </div>
                """, unsafe_allow_html=True)

        # Real Life Applications
        if real_life:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="key-points-title" style="color:#2563EB;">🌍 Real-Life Applications</div>', unsafe_allow_html=True)
            for r in real_life:
                st.markdown(f"""
                <div class="key-point-item" style="background:#EFF6FF; border:1px solid #BFDBFE;">
                    <span class="key-point-check" style="color:#2563EB; background:transparent;">🔹</span>
                    <span style="color:#1E3A8A;">{r}</span>
                </div>
                """, unsafe_allow_html=True)

        # Cards: Memory Tip & Fun Fact
        if mem_tip or fun_fact:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            c_mem, c_fun = st.columns(2)
            with c_mem:
                if mem_tip:
                    st.markdown(f"""
                    <div class="sa-card" style="background:#FDF4FF; border-color:#F5D0FE; height:100%;">
                        <div class="sa-card-title" style="color:#86198F;">🧠 Memory Tip</div>
                        <div class="sa-card-sub" style="color:#701A75; font-weight:500;">{mem_tip}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with c_fun:
                if fun_fact:
                    st.markdown(f"""
                    <div class="sa-card" style="background:#FFF1F2; border-color:#FECDD3; height:100%;">
                        <div class="sa-card-title" style="color:#BE123C;">🌟 Fun Fact</div>
                        <div class="sa-card-sub" style="color:#9F1239; font-weight:500;">{fun_fact}</div>
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

        # Follow-Up Questions
        if follow_up:
            st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="key-points-title" style="color:#4F46E5;">❓ Follow-Up Questions to Think About</div>', unsafe_allow_html=True)
            for f in follow_up:
                st.markdown(f"""
                <div class="key-point-item" style="background:#EEF2FF; border:1px solid #C7D2FE;">
                    <span class="key-point-check" style="color:#4F46E5; background:transparent;">🤔</span>
                    <span style="color:#3730A3; font-weight:500;">{f}</span>
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
