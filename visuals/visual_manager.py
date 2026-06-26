"""
visual_manager.py
Orchestrator for the school-focused visual system.

Priorities:
1. Educational Images (Wikimedia Commons)
2. Educational Infographics (HTML/CSS process cards)
3. Comparison Cards (HTML side-by-side comparative cards)
4. Timeline Cards (HTML vertical timeline cards)
5. Graphviz (Simple process flows and classification trees only)

Public API:
    get_smart_visual(topic, explanation, language) -> dict
"""

from visuals.mermaid_generator import generate_mermaid_visual
from visuals.infographic_generator import (
    generate_educational_infographic,
    generate_comparison_cards,
    generate_timeline_cards,
    generate_table_visual
)
from visuals.wikimedia_fetcher import fetch_wikimedia_image


def get_smart_visual(visual_data: dict, fallback_topic: str = "") -> dict:
    """
    Retrieves the visual asset content based on the structured visual data provided by the LLM.
    """
    if not visual_data:
        vtype = "educational_image"
        topic = fallback_topic
    else:
        vtype = visual_data.get("visual_type", "educational_image").lower()
        topic = visual_data.get("query") or visual_data.get("title") or fallback_topic

    # ── 1. Educational Image ──────────────────────────────────────────────────
    if vtype == "educational_image" or vtype == "image":
        img = fetch_wikimedia_image(topic)
        if img:
            return {"type": "educational_image", "content": img, "label": "🖼️ Educational Diagram"}
        vtype = "none"

    # ── 2. Educational Infographic ────────────────────────────────────────────
    if vtype == "infographic":
        html = generate_educational_infographic(visual_data)
        if html:
            return {"type": "infographic", "content": html, "label": "💡 Process Infographic"}
        vtype = "mermaid"

    # ── 3. Comparison Card ────────────────────────────────────────────────────
    if vtype == "comparison":
        html = generate_comparison_cards(visual_data)
        if html:
            return {"type": "comparison", "content": html, "label": "⚖️ Comparison Cards"}
        vtype = "mermaid"

    # ── 4. Timeline ───────────────────────────────────────────────────────────
    if vtype == "timeline":
        html = generate_timeline_cards(visual_data)
        if html:
            return {"type": "timeline", "content": html, "label": "⏳ Timeline Summary"}
        vtype = "mermaid"

    # ── 5. Mermaid.js (Process Flow / Classification Tree) ────────────────────
    if vtype in ("mermaid", "flowchart", "mindmap", "classification_tree", "cycle", "network"):
        html = generate_mermaid_visual(visual_data)
        if html:
            return {"type": "mermaid", "content": html, "label": "📊 Concept flowchart"}
        vtype = "none"

    # ── 6. Table ──────────────────────────────────────────────────────────────
    if vtype == "table":
        html = generate_table_visual(visual_data)
        if html:
            return {"type": "table", "content": html, "label": "📊 Table Summary"}
        vtype = "none"

    # Final Fallback to Wikimedia search
    if fallback_topic:
        img = fetch_wikimedia_image(fallback_topic)
        if img:
            return {"type": "educational_image", "content": img, "label": "🖼️ Educational Diagram"}

    return {"type": "none", "content": None, "label": ""}


def render_visual(visual_result: dict):
    """
    Renders the visual result inside Streamlit.
    """
    import streamlit as st

    vtype   = visual_result.get("type")
    content = visual_result.get("content")

    if vtype == "none" or not content:
        st.info("No visual aid available for this topic.")
        return

    if vtype in ("infographic", "comparison", "timeline", "mermaid", "table"):
        height = 420
        if vtype == "comparison": height = 480
        elif vtype == "timeline": height = 500
        elif vtype == "table": height = 440
        
        import base64
        b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        st.markdown(f'<iframe src="data:text/html;base64,{b64}" width="100%" height="{height}" frameborder="0" scrolling="yes"></iframe>', unsafe_allow_html=True)

    elif vtype == "educational_image":
        img_url = content.get("image_url")
        title   = content.get("title", "")
        desc    = content.get("description", "")
        source  = content.get("source", "Wikimedia Commons")

        if img_url:
            st.markdown(f"""
            <div style="text-align:center; overflow:auto; padding:1.2rem;
                        background:#FFFFFF; border:2px solid #DBEAFE; border-radius:12px;
                        display:flex; justify-content:center; align-items:center;">
                <img src="{img_url}" style="max-width:100%; height:auto; border-radius:8px;">
            </div>
            """, unsafe_allow_html=True)

        if title or desc:
            import html
            st.markdown(f"""
            <div style="margin-top:0.6rem; padding:0.7rem 1rem;
                        background:rgba(37,99,235,0.06); border-left:3px solid #2563EB;
                        border-radius:8px;">
                <div style="font-weight:700; color:#1E3A8A;">{html.escape(title)}</div>
                <div style="font-size:0.9rem; color:#475569; margin-top:0.2rem; line-height:1.5;">{html.escape(desc)}</div>
                <div style="font-size:0.75rem; color:#94A3B8; margin-top:0.3rem;">Source: {html.escape(source)}</div>
            </div>
            """, unsafe_allow_html=True)
    