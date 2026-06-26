"""
VidyaSaarthi — app.py (entry point)
Uses st.navigation / st.Page for multi-page routing.
Each page lives in pages/pg_*.py and imports from pages/shared.py.
"""

import streamlit as st
import os

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="VidyaSaarthi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Ensure temp dir exists ────────────────────────────────────────────────────
os.makedirs("temp", exist_ok=True)

# ── Multi-page navigation via st.navigation + st.Page ────────────────────────
pg = st.navigation(
    [
        st.Page("pages/pg_home.py",   title="Home",   icon="🏠", default=True),
        st.Page("pages/pg_notes.py",  title="Notes",  icon="📚"),
        st.Page("pages/pg_quiz.py",   title="Quiz",   icon="🧠"),
        st.Page("pages/pg_type.py",   title="Ask by Typing",   icon="⌨️"),
    ],
    position="hidden",
)

pg.run()