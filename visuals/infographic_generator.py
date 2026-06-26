"""
infographic_generator.py
Generates educational infographic components (processes, comparison cards, timelines)
as responsive HTML blocks styled for the light educational textbook theme.
Uses JSON-first pattern: LLM outputs structured data via the main EXPLANATION payload, Python builds HTML.
"""

def generate_educational_infographic(visual_data: dict) -> str | None:
    try:
        title = visual_data.get("title", "Process Infographic")
        intro = visual_data.get("intro", "")
        steps = visual_data.get("steps", [])

        if not steps:
            return None

        # Build clean Light Theme HTML
        steps_html = ""
        for s in steps:
            import html
            num = html.escape(str(s.get("step_num", "")))
            step_title = html.escape(s.get("title", ""))
            desc = html.escape(s.get("desc", ""))
            steps_html += f"""
            <div style="display:flex; gap:1.2rem; align-items:flex-start; background:#F0F4FF; 
                        border-radius:12px; padding:1.2rem; border:1px solid #BFDBFE; 
                        margin-bottom:1rem; box-shadow:0 2px 6px rgba(37,99,235,0.06);">
                <div style="background:#2563EB; color:#FFFFFF; font-weight:bold; font-size:1.15rem; 
                            border-radius:50%; width:36px; height:36px; display:flex; 
                            justify-content:center; align-items:center; flex-shrink:0; 
                            box-shadow: 0 2px 5px rgba(37,99,235,0.2);">
                    {num}
                </div>
                <div style="flex:1;">
                    <h4 style="color:#1E3A8A; margin:0 0 0.4rem 0; font-size:1.15rem; font-family:system-ui,sans-serif; font-weight:700;">{step_title}</h4>
                    <p style="color:#374151; margin:0; font-size:1rem; line-height:1.6; font-family:system-ui,sans-serif;">{desc}</p>
                </div>
            </div>
            """

        wrapped = f"""
        <div style="background:#FFFFFF; padding:1.5rem; border-radius:16px; 
                    border:1px solid #DBEAFE; font-family:system-ui, sans-serif;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <h3 style="color:#1E3A8A; margin:0 0 0.4rem 0; font-size:1.45rem; font-weight:800;">💡 {title}</h3>
            <p style="color:#4B5563; margin:0 0 1.5rem 0; font-size:1.05rem; line-height:1.5;">{intro}</p>
            <div>
                {steps_html}
            </div>
        </div>
        """
        return wrapped
    except Exception as e:
        print("[infographic_generator] Infographic error:", e)
        return None


def generate_comparison_cards(visual_data: dict) -> str | None:
    try:
        title = visual_data.get("title", "Comparison")
        cards = visual_data.get("cards", [])

        if len(cards) < 2:
            return None

        import html
        # Build two side-by-side Light Theme cards
        cards_html = ""
        for card in cards:
            c_title = html.escape(card.get("title", ""))
            desc = card.get("desc", "")
            
            # If desc is a string, make it a bullet point. If it's a list, make multiple bullet points.
            points_list = ""
            if isinstance(desc, list):
                points_list = "".join([f'<li style="margin-bottom:0.7rem;">{html.escape(p)}</li>' for p in desc])
            else:
                points_list = f'<li style="margin-bottom:0.7rem;">{html.escape(desc)}</li>'
            
            cards_html += f"""
            <div style="flex:1; min-width:280px; background:#F0F4FF; border-radius:12px; 
                        padding:1.3rem; border:1px solid #BFDBFE; 
                        display:flex; flex-direction:column; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <h4 style="color:#1E3A8A; font-size:1.3rem; margin:0 0 1.2rem 0; 
                           padding-bottom:0.6rem; border-bottom:2px solid #BFDBFE; 
                           text-align:center; font-family:system-ui,sans-serif; font-weight:700;">
                    {c_title}
                </h4>
                <ul style="padding-left:1.2rem; margin:0; color:#374151; font-size:1.05rem; 
                           line-height:1.65; font-family:system-ui,sans-serif;">
                    {points_list}
                </ul>
            </div>
            """

        wrapped = f"""
        <div style="background:#FFFFFF; padding:1.5rem; border-radius:16px; 
                    border:1px solid #DBEAFE; font-family:system-ui, sans-serif;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <h3 style="color:#1E3A8A; margin:0 0 1.5rem 0; font-size:1.45rem; text-align:center; font-weight:800;">⚖️ {title}</h3>
            <div style="display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center;">
                {cards_html}
            </div>
        </div>
        """
        return wrapped
    except Exception as e:
        print("[infographic_generator] Comparison card error:", e)
        return None


def generate_timeline_cards(visual_data: dict) -> str | None:
    try:
        title = visual_data.get("title", "Timeline")
        events = visual_data.get("cards", []) # Use 'cards' from the visual payload to stay consistent

        if not events:
            return None

        # Build vertical timeline Light Theme
        import html
        events_html = ""
        for ev in events:
            time = html.escape(ev.get("title", "")) # using title as the time/event name
            desc = html.escape(ev.get("desc", ""))
            events_html += f"""
            <div style="position:relative; margin-bottom:1.5rem;">
                <!-- Timeline Dot -->
                <div style="position:absolute; left:-29px; top:6px; width:12px; height:12px; 
                            border-radius:50%; background:#2563EB; border:2px solid #FFFFFF;
                            box-shadow: 0 0 6px rgba(37,99,235,0.4);"></div>
                <div style="background:#F0F4FF; border-radius:12px; padding:1.2rem; 
                            border:1px solid #BFDBFE; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                    <span style="display:inline-block; font-weight:bold; color:#2563EB; 
                                 font-size:1.15rem; margin-bottom:0.4rem; font-family:system-ui,sans-serif;">
                        📅 {time}
                    </span>
                    <p style="color:#374151; margin:0; font-size:1.05rem; line-height:1.55; font-family:system-ui,sans-serif;">
                        {desc}
                    </p>
                </div>
            </div>
            """

        wrapped = f"""
        <div style="background:#FFFFFF; padding:1.5rem; border-radius:16px; 
                    border:1px solid #DBEAFE; font-family:system-ui, sans-serif;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <h3 style="color:#1E3A8A; margin:0 0 1.8rem 0; font-size:1.45rem; font-weight:800;">⏳ {title}</h3>
            <div style="position:relative; padding-left:1.5rem; border-left:3px solid #BFDBFE; 
                        margin-left:1rem; display:flex; flex-direction:column;">
                {events_html}
            </div>
        </div>
        """
        return wrapped
    except Exception as e:
        print("[infographic_generator] Timeline error:", e)
        return None

def generate_table_visual(visual_data: dict) -> str | None:
    try:
        title = visual_data.get("title", "Table Summary")
        headers = visual_data.get("headers", [])
        rows = visual_data.get("rows", [])

        if not headers or not rows:
            return None

        import html
        headers_html = "".join([f'<th style="background:#2563EB; color:#FFFFFF; padding:10px 12px; font-weight:700; text-align:left; border:1px solid #BFDBFE; font-family:system-ui,sans-serif;">{html.escape(h)}</th>' for h in headers])

        rows_html = ""
        for i, row in enumerate(rows):
            bg = "#F8FAFC" if i % 2 == 1 else "#FFFFFF"
            cells_html = "".join([f'<td style="padding:10px 12px; border:1px solid #E2E8F0; color:#374151; font-size:0.95rem; font-family:system-ui,sans-serif;">{html.escape(str(cell))}</td>' for cell in row])
            rows_html += f'<tr style="background:{bg};">{cells_html}</tr>'

        wrapped = f"""
        <div style="background:#FFFFFF; padding:1.5rem; border-radius:16px; 
                    border:1px solid #DBEAFE; font-family:system-ui, sans-serif;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow-x:auto;">
            <h3 style="color:#1E3A8A; margin:0 0 1rem 0; font-size:1.45rem; font-weight:800;">📊 {title}</h3>
            <table style="width:100%; border-collapse:collapse; border:1px solid #DBEAFE; border-radius:8px; overflow:hidden;">
                <thead>
                    <tr>{headers_html}</tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        return wrapped
    except Exception as e:
        print("[infographic_generator] Table error:", e)
        return None

