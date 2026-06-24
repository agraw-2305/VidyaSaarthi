"""
ShikshaAI — pages/pg_quiz.py
Quiz page: quiz type selection → active quiz interface → score screen.
"""

import streamlit as st
import os
from pages.shared import (
    init_state, load_css, render_header, render_sidebar_nav, process, play
)
from speech.tts import text_to_speech

init_state()
load_css()
render_header()

lang        = st.session_state.language
quiz_active = st.session_state.quiz_active
quiz_data   = st.session_state.quiz_data
audio_path  = st.session_state.audio_path
autoplay    = st.session_state.autoplay

# ══════════════════════════════════════════════════════════════════════════════
# CASE 1: Quiz in progress
# ══════════════════════════════════════════════════════════════════════════════
if quiz_active and quiz_data:
    qs    = quiz_data.get("questions", [])
    q_idx = st.session_state.q_idx
    total = len(qs)

    # Navigation buttons
    nav1, nav2, nav_spacer = st.columns([1, 1, 3])
    with nav1:
        if st.button("🏠 Home", key="quiz_home", use_container_width=True):
            st.session_state.update({
                "quiz_active": False, "quiz_data": None, "q_idx": 0,
                "selected": None, "score": 0, "history": [],
                "fb_audio": None, "fb_play": False,
            })
            st.switch_page("pages/pg_home.py")
    with nav2:
        if st.button("❌ Exit Quiz", key="quiz_exit", use_container_width=True):
            st.session_state.update({
                "quiz_active": False, "quiz_data": None, "q_idx": 0,
                "selected": None, "score": 0, "history": [],
                "fb_audio": None, "fb_play": False,
            })
            st.rerun()

    if q_idx < total:
        current_q       = qs[q_idx]
        opt             = current_q.get("options", {})
        correct         = current_q.get("correct_option", "A")
        selected_choice = st.session_state.selected

        # ── Quiz header bar ───────────────────────────────────────────────
        st.markdown(f"""
        <div class="quiz-header-bar">
            <span class="quiz-badge">{quiz_data.get("quiz_title", "Quiz")}</span>
            <span class="quiz-q-info">Question {q_idx + 1} of {total}</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Progress dots ─────────────────────────────────────────────────
        dots_html = ""
        for i in range(total):
            if i < len(st.session_state.history):
                status = st.session_state.history[i]
                cls = "answered" if status == "correct" else "incorrect"
            elif i == q_idx:
                cls = "current"
            else:
                cls = ""
            dots_html += f'<div class="progress-dot {cls}">{i + 1}</div>'

        st.markdown(f"""
        <div class="quiz-progress">{dots_html}</div>
        """, unsafe_allow_html=True)

        # ── Two columns: Question + Visual ────────────────────────────────
        col_question, col_visual = st.columns([3, 2], gap="large")

        with col_question:
            # Question text
            st.markdown(f"""
            <div class="quiz-question">{current_q.get("question_text", "")}</div>
            """, unsafe_allow_html=True)

            # Add quiz type marker for button styling
            q_type = st.session_state.question_type
            if q_type == "MCQ":
                st.markdown('<div class="quiz-marker-mcq"></div>', unsafe_allow_html=True)
            elif q_type in ("Fill in the Blank", "Fill in the Blanks"):
                st.markdown('<div class="quiz-marker-fill"></div>', unsafe_allow_html=True)
            elif q_type in ("True/False", "True / False"):
                st.markdown('<div class="quiz-marker-tf"></div>', unsafe_allow_html=True)

            # Verbal Question Announcement
            play(audio_path, autoplay)

            # Options
            if selected_choice is None:
                for k, v in opt.items():
                    if st.button(f"{k}   {v}", key=f"opt_{q_idx}_{k}",
                                 use_container_width=True):
                        st.session_state.selected = k
                        if k == correct:
                            st.session_state.score += 1
                            st.session_state.history.append("correct")
                            verbal = "Waah! Bilkul sahi jawab!"
                        else:
                            st.session_state.history.append("incorrect")
                            verbal = f"Oh! Yeh galat hai. Sahi jawab hai option {correct}."
                        with st.spinner("Processing feedback..."):
                            st.session_state.fb_audio = text_to_speech(
                                f"{verbal} {current_q.get('explanation', '')}", language=lang
                            )
                        st.session_state.fb_play = True
                        st.rerun()
            else:
                # Show results
                for k, v in opt.items():
                    if k == correct:
                        st.markdown(f"""
                        <div class="quiz-opt correct">
                            <span class="opt-letter">{k}</span>
                            <span style="flex:1">{v}</span>
                            <span style="font-weight:700; color:#059669;">✓ Correct</span>
                        </div>""", unsafe_allow_html=True)
                    elif k == selected_choice:
                        st.markdown(f"""
                        <div class="quiz-opt incorrect">
                            <span class="opt-letter">{k}</span>
                            <span style="flex:1">{v}</span>
                            <span style="font-weight:700; color:#DC2626;">✗ Wrong</span>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="quiz-opt">
                            <span class="opt-letter">{k}</span>
                            <span style="flex:1">{v}</span>
                        </div>""", unsafe_allow_html=True)

                # Feedback card
                is_ok      = selected_choice == correct
                card_title = "🎉 Correct Answer!" if is_ok else "❌ Incorrect!"
                card_cls   = "fb-card-correct"    if is_ok else "fb-card-incorrect"
                card_color = "#059669"             if is_ok else "#DC2626"

                st.markdown(f"""
                <div class="{card_cls}">
                    <div class="fb-head" style="color:{card_color};">{card_title}</div>
                    <div style="font-size:0.9rem; font-weight:600; color:{card_color}; margin-bottom:0.3rem;">
                        Correct Answer: Option {correct}
                    </div>
                    <div class="fb-exp">{current_q.get("explanation", "")}</div>
                </div>
                """, unsafe_allow_html=True)

                # Audio feedback
                if st.session_state.fb_audio and st.session_state.fb_play:
                    st.audio(st.session_state.fb_audio, autoplay=True)
                    st.session_state.fb_play = False
                elif st.session_state.fb_audio:
                    st.audio(st.session_state.fb_audio)

                # Navigation buttons
                btn1, btn2 = st.columns(2)
                with btn1:
                    if st.button("🔊 Listen Explanation", key=f"replay_{q_idx}",
                                 use_container_width=True):
                        st.session_state.fb_play = True
                        st.rerun()
                with btn2:
                    lbl = "Next Question →" if q_idx < total - 1 else "Finish Quiz 🏁"
                    if st.button(lbl, key=f"next_{q_idx}", use_container_width=True,
                                 type="primary"):
                        st.session_state.selected = None
                        st.session_state.fb_audio = None
                        st.session_state.fb_play  = False
                        st.session_state.q_idx   += 1
                        ni = st.session_state.q_idx
                        if ni < total:
                            with st.spinner("Preparing next question..."):
                                st.session_state.audio_path = text_to_speech(
                                    qs[ni].get("audio_script", ""), language=lang
                                )
                            st.session_state.autoplay = True
                        else:
                            st.session_state.quiz_active = False
                        st.rerun()

        with col_visual:
            # Visual Explanation panel
            visual = st.session_state.visual
            st.markdown('<div class="visual-explanation-title">Visual Aid</div>', unsafe_allow_html=True)
            st.markdown('<div class="quiz-visual-marker"></div>', unsafe_allow_html=True)
            if visual and visual.get("type") != "none":
                from visuals.visual_manager import render_visual
                render_visual(visual)
            else:
                st.markdown("""
                <div class="visual-placeholder" style="padding:2rem;">
                    <span class="visual-ph-icon">📊</span>
                    <div class="visual-ph-label">Visual Aid</div>
                    <div class="visual-ph-sub">Visual explanation will appear here when available.</div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.session_state.quiz_active = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CASE 2: Quiz finished — score screen
# ══════════════════════════════════════════════════════════════════════════════
elif not quiz_active and quiz_data:
    qs  = quiz_data.get("questions", [])
    sc  = st.session_state.score
    tot = len(qs)
    msg = "Outstanding! Perfect score! 🌟" if sc == tot else "Great effort! Keep learning! 👍"

    st.markdown(f"""
    <div class="quiz-finish">
        <div class="quiz-finish-lbl">🏆 Quiz Finished!</div>
        <div class="quiz-finish-score">{sc} / {tot}</div>
        <div class="quiz-finish-desc">
            You scored <b>{sc}</b> correct answers out of <b>{tot}</b>.<br>{msg}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.audio(text_to_speech(f"Quiz completed! Score is {sc} out of {tot}.", language=lang),
             autoplay=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Go Home", key="finish_home", use_container_width=True):
            st.session_state.update({
                "quiz_active": False, "quiz_data": None, "q_idx": 0,
                "selected": None, "score": 0, "history": [],
                "fb_audio": None, "fb_play": False,
            })
            st.switch_page("pages/pg_home.py")
    with c2:
        if st.button("🔄 Restart Quiz", key="restart_quiz", use_container_width=True,
                     type="primary"):
            st.session_state.update({
                "q_idx": 0, "selected": None, "score": 0,
                "history": [], "fb_audio": None, "fb_play": False,
                "quiz_active": True,
            })
            if qs:
                with st.spinner("Generating voice..."):
                    st.session_state.audio_path = text_to_speech(
                        qs[0].get("audio_script", ""), language=lang
                    )
                st.session_state.autoplay = True
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CASE 3: Quiz type selection
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="quiz-selection-title">Quiz Time! 🎯</div>
    <div class="quiz-selection-sub">Choose how you want to take the quiz</div>
    """, unsafe_allow_html=True)

    # Topic input
    topic_box = st.text_input(
        "Quiz Topic",
        placeholder="Enter any school topic — e.g. Water Cycle, Human Heart, Gravity...",
        key="quiz_topic_inp",
    )

    # Three quiz type cards
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown("""
        <div class="quiz-type-card">
            <span class="quiz-type-icon">📝</span>
            <div class="quiz-type-label">MCQ Quiz</div>
            <div class="quiz-type-desc">Multiple Choice Questions</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start MCQ Quiz", key="start_mcq", use_container_width=True,
                     type="primary"):
            if topic_box.strip():
                process(f"Quiz on '{topic_box.strip()}'", num_q=10, q_type="MCQ")
                st.rerun()
            else:
                st.warning("Please enter a topic first.")

    with c2:
        st.markdown("""
        <div class="quiz-type-card">
            <span class="quiz-type-icon">✏️</span>
            <div class="quiz-type-label">Fill in the Blanks</div>
            <div class="quiz-type-desc">Complete the missing words</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Fill in the Blanks", key="start_fill", use_container_width=True):
            if topic_box.strip():
                process(f"Quiz on '{topic_box.strip()}'", num_q=10,
                       q_type="Fill in the Blank")
                st.rerun()
            else:
                st.warning("Please enter a topic first.")

    with c3:
        st.markdown("""
        <div class="quiz-type-card">
            <span class="quiz-type-icon">✅</span>
            <div class="quiz-type-label">True / False</div>
            <div class="quiz-type-desc">Decide whether the statement is True or False</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start True / False Quiz", key="start_tf", use_container_width=True):
            if topic_box.strip():
                process(f"Quiz on '{topic_box.strip()}'", num_q=10,
                       q_type="True/False")
                st.rerun()
            else:
                st.warning("Please enter a topic first.")

    # Difficulty selector
    st.markdown('<div class="sa-divider"></div>', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        diff = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1,
                            key="quiz_diff_sel")
        st.session_state.difficulty = diff
    with dc2:
        num = st.selectbox("Number of Questions", [5, 10, 15, 20], index=1,
                           key="quiz_num_sel")
        st.session_state.num_q = num

    # Voice tip
    st.markdown("""
    <div class="voice-tip">
        🎤 You can say: "Start MCQ Quiz" or "Take a True or False Quiz"
    </div>
    """, unsafe_allow_html=True)

render_sidebar_nav(__file__)
