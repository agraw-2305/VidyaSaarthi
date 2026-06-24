"""
infographic_generator.py
Generates educational infographic components (processes, comparison cards, timelines)
as responsive HTML blocks styled for the light educational textbook theme.
Uses JSON-first pattern: LLM outputs structured data, Python builds HTML.
"""

import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ──────────────────────────────────────────────────────────────────────────────
# 1. EDUCATIONAL INFOGRAPHICS (Processes / Cycles)
# ──────────────────────────────────────────────────────────────────────────────

_INFOGRAPHIC_SYSTEM_PROMPT = """You are an expert school textbook visual designer.
Create a step-by-step process or cycle breakdown for the given topic in JSON format.

STRICT JSON FORMAT:
{
  "title": "Water Cycle Process (Jal Chakra)",
  "intro": "How water moves from Earth to the sky and back.",
  "steps": [
    {
      "step_num": 1,
      "title": "Evaporation (Vashpikaran)",
      "desc": "The Sun heats up water in lakes, turning it into vapor."
    },
    {
      "step_num": 2,
      "title": "Condensation (Sanganak)",
      "desc": "Water vapor cools down high in the air to form clouds."
    }
  ]
}

RULES:
1. ONLY return a valid JSON object. No conversational text or markdown code blocks.
2. Limit to 3-6 clear, logical steps. Keep explanations simple for Class 5-12.
3. Keep descriptions concise (15-25 words each).
4. Match language requested (Hinglish, Hindi, English).
"""

def generate_educational_infographic(topic: str, explanation: str, language: str = "Hinglish") -> str | None:
    try:
        user_msg = f"Language: {language}\nTopic: {topic}\nContext:\n{explanation[:500]}"
        resp = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _INFOGRAPHIC_SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        data = json.loads(resp.choices[0].message.content.strip())
        
        title = data.get("title", topic)
        intro = data.get("intro", "")
        steps = data.get("steps", [])

        if not steps:
            return None

        # Build clean Light Theme HTML
        steps_html = ""
        for s in steps:
            num = s.get("step_num", "")
            step_title = s.get("title", "")
            desc = s.get("desc", "")
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


# ──────────────────────────────────────────────────────────────────────────────
# 2. COMPARISON CARDS
# ──────────────────────────────────────────────────────────────────────────────

_COMPARISON_SYSTEM_PROMPT = """You are an expert school textbook designer.
Compare two topics/concepts side-by-side in JSON format.

STRICT JSON FORMAT:
{
  "title": "Herbivores vs Carnivores",
  "cards": [
    {
      "title": "Herbivores (Shakahari)",
      "points": [
        "Eat plants and fruits.",
        "Flat, broad teeth for grinding grass.",
        "Examples: Cow, Deer, Goat."
      ]
    },
    {
      "title": "Carnivores (Mansahari)",
      "points": [
        "Eat other animals and meat.",
        "Sharp, pointed teeth to tear flesh.",
        "Examples: Lion, Tiger, Leopard."
      ]
    }
  ]
}

RULES:
1. ONLY return a valid JSON object. No markdown, no fences.
2. Produce exactly 2 comparative items in the "cards" list.
3. Limit to 3-5 distinct bullet points per card.
4. Keep comparison points aligned and clear for school students.
5. Match language requested (Hinglish, Hindi, English).
"""

def generate_comparison_cards(topic: str, explanation: str, language: str = "Hinglish") -> str | None:
    try:
        user_msg = f"Language: {language}\nTopic: {topic}\nContext:\n{explanation[:500]}"
        resp = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _COMPARISON_SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        data = json.loads(resp.choices[0].message.content.strip())
        
        title = data.get("title", topic)
        cards = data.get("cards", [])

        if len(cards) < 2:
            return None

        # Build two side-by-side Light Theme cards
        cards_html = ""
        for card in cards:
            c_title = card.get("title", "")
            points = card.get("points", [])
            points_list = "".join([f'<li style="margin-bottom:0.7rem;">{p}</li>' for p in points])
            
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


# ──────────────────────────────────────────────────────────────────────────────
# 3. TIMELINE CARDS
# ──────────────────────────────────────────────────────────────────────────────

_TIMELINE_SYSTEM_PROMPT = """You are an expert history textbook illustrator.
Create a historical or process timeline in JSON format.

STRICT JSON FORMAT:
{
  "title": "Life of Mahatma Gandhi",
  "events": [
    {
      "time": "1869",
      "event": "Born in Porbandar, Gujarat."
    },
    {
      "time": "1915",
      "event": "Returned to India from South Africa to join the freedom movement."
    },
    {
      "time": "1947",
      "event": "India achieved Independence from British rule."
    }
  ]
}

RULES:
1. ONLY return a valid JSON object. No markdown, no fences.
2. Limit to 3-6 significant chronological events.
3. Keep event summaries simple and educational (10-20 words).
4. Match language requested (Hinglish, Hindi, English).
"""

def generate_timeline_cards(topic: str, explanation: str, language: str = "Hinglish") -> str | None:
    try:
        user_msg = f"Language: {language}\nTopic: {topic}\nContext:\n{explanation[:500]}"
        resp = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _TIMELINE_SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        data = json.loads(resp.choices[0].message.content.strip())
        
        title = data.get("title", topic)
        events = data.get("events", [])

        if not events:
            return None

        # Build vertical timeline Light Theme
        events_html = ""
        for i, ev in enumerate(events):
            time = ev.get("time", "")
            desc = ev.get("event", "")
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
