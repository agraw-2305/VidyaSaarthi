"""
VidyaSaarthi — llm.py
Complete LLM engine: intent classification, structured AI teaching,
NCERT-aligned responses, enriched JSON schema, retry/validation, configurable model.
"""

from groq import Groq
import os
import json
import re
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Configurable Model (Item #25, #26) ────────────────────────────────────────
_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
_MAX_TOKENS  = int(os.getenv("GROQ_MAX_TOKENS", "4096"))

# Load multiple API keys for rotation
_keys_str = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]
if not API_KEYS:
    # fallback to single key
    single_key = os.getenv("GROQ_API_KEY", "").strip()
    API_KEYS = [single_key] if single_key else []

# Default client
client = Groq(api_key=API_KEYS[0]) if API_KEYS else None

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# INTENT CLASSIFICATION (Item #2, #7)
# ══════════════════════════════════════════════════════════════════════════════
INTENT_TYPES = [
    "explanation", "quiz", "doubt", "revision", "compare",
    "diagram", "homework", "summary", "definition", "formula", "example"
]

# Extended quiz detection keywords (Item #7)
QUIZ_HINT_KEYWORDS = [
    "quiz", "test", "practice", "assessment", "revision", "worksheet",
    "mcq", "rapid fire", "challenge", "true false", "fill blanks",
    "ask me questions", "check my knowledge", "mock test", "question paper",
]

from prompt_builder import build_system_prompt


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def _build_system_prompt(text_language: str, audio_language: str, class_level: int = 8, intent: str = "explanation", audio_requested: bool = True) -> str:
    return build_system_prompt(text_language, audio_language, class_level, intent, audio_requested)


# ══════════════════════════════════════════════════════════════════════════════
# INTENT ROUTER (Item #20, #4)
# ══════════════════════════════════════════════════════════════════════════════
def route_intent(query: str, is_quiz_forced: bool = False) -> str:
    """Uses Python heuristic keyword matching to classify intent. Falls back to LLM if ambiguous."""
    if is_quiz_forced:
        return "quiz"
        
    q = query.lower()
    
    # Quiz keywords
    if re.search(r'\b(quiz|test|practice|assessment|mcq|rapid fire|challenge|true false|fill blanks|question paper|mock test)\b', q):
        return "quiz"
    # Compare keywords
    if re.search(r'\b(compare|difference|vs|versus|distinguish)\b', q):
        return "compare"
    # Homework keywords
    if re.search(r'\b(homework|solve|calculate|find the value|equation)\b', q):
        return "homework"
    # Revision keywords
    if re.search(r'\b(revision|revise|summary|summarize|short notes)\b', q):
        return "revision"
    # Definition keywords
    if re.search(r'\b(define|definition|what is|what are|meaning of)\b', q):
        if not re.search(r'\b(how|why|process)\b', q):
            return "definition"
            
    # Hybrid Fallback: Use lightweight LLM for ambiguous queries
    router_prompt = """Classify the user's educational query into exactly ONE of these intents:
"explanation", "quiz", "definition", "compare", "revision", "homework".
If unsure, default to "explanation".
Respond STRICTLY with JSON: {"intent": "explanation"}"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=20,
            temperature=0.1
        )
        data = json.loads(resp.choices[0].message.content.strip())
        intent = data.get("intent", "explanation").lower()
        if intent not in ["explanation", "quiz", "definition", "compare", "revision", "homework"]:
            return "explanation"
        return intent
    except Exception as e:
        logger.warning(f"Hybrid router fallback failed: {e}. Defaulting to explanation.")
        return "explanation"


# ══════════════════════════════════════════════════════════════════════════════
# GENERATE RESPONSE (Items #25, #26, #27)
# ══════════════════════════════════════════════════════════════════════════════
def generate_response(
    query: str,
    text_language: str = "English",
    audio_language: str = "English",
    num_questions: int = 5,
    difficulty: str = "Medium",
    question_type: str = "MCQ",
    class_level: int = 8,
    conversation_history: list = None,
    override_model: str = None,
    override_client = None,
    override_max_tokens: int = None,
    audio_requested: bool = True,
) -> str:
    """
    Generate an LLM response with full context.
    """
    # Call the Python router to determine intent
    is_quiz_forced = (num_questions != 5)
    intent = route_intent(query, is_quiz_forced)
    
    system_prompt = _build_system_prompt(text_language, audio_language, class_level, intent, audio_requested)

    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation context — last 3 turns
    if conversation_history:
        for turn in conversation_history[-3:]:
            # Prevent massive token bloat from previous JSON responses
            if turn["role"] == "assistant" and len(turn.get("content", "")) > 500:
                messages.append({"role": "assistant", "content": turn["content"][:300] + "... [Detailed JSON omitted to save context length]"})
            else:
                messages.append(turn)

    # Build user message with explicit language and quiz length demands
    user_content = f"USER QUERY: {query}\n\n=========================================\nCRITICAL LANGUAGE ENFORCEMENT:\n- You MUST write ALL JSON content (explanations, notes, questions, options) in strictly {text_language.upper()} (EXCEPT Mermaid code structure and image queries, which stay in English)."
    if audio_requested:
        user_content += f"\n- You MUST write the 'audio_script' field in strictly {audio_language.upper()}."
    else:
        user_content += "\n- DO NOT GENERATE AN AUDIO SCRIPT. Leave the 'audio_script' field completely empty string \"\" to save output tokens."
    user_content += f"\n- DO NOT default to English unless English is requested. If {text_language.upper()} is Hindi, output Devnagari script. If Hinglish, output Romanized Hindi.\n========================================="

    print(f"DEBUG: Generating Response for text_lang={text_language}, audio_lang={audio_language}, intent={intent}, audio_req={audio_requested}")
    if intent == "quiz":
        quiz_specs = []
        quiz_specs.append(f"Generate exactly {num_questions} questions.")
        quiz_specs.append(f"The difficulty level must be: {difficulty}.")
        quiz_specs.append(f"Follow Bloom's Taxonomy progression: Remember → Understand → Apply → Analyze.")
        quiz_specs.append(f"Progress difficulty within the quiz: start Easy, then Medium, then Hard.")

        if question_type in ("True/False", "True False"):
            quiz_specs.append("All questions must be True/False type, where options are strictly 'A': 'True' and 'B': 'False'.")
        else:
            quiz_specs.append("All questions must be standard Multiple Choice Questions (MCQ) with options A, B, C, D.")

        user_content += f"\n\nIMPORTANT QUIZ SPECIFICATIONS:\n" + "\n".join(f"- {s}" for s in quiz_specs)

    messages.append({"role": "user", "content": user_content})

    model_to_use = override_model or _MODEL
    active_client = override_client or client
    active_max_tokens = override_max_tokens or _MAX_TOKENS
    # API call with configured parameters
    resp = active_client.chat.completions.create(
        model=model_to_use,
        response_format={"type": "json_object"},
        temperature=_TEMPERATURE,
        max_completion_tokens=active_max_tokens,
        messages=messages,
    )
    return resp.choices[0].message.content


# ══════════════════════════════════════════════════════════════════════════════
# JSON VALIDATION (Item #22)
# ══════════════════════════════════════════════════════════════════════════════

# Required fields for explanation responses
_EXPLANATION_REQUIRED = {
    "type":                   "explanation",
    "intent":                 "explanation",
    "tags":                   [],
    "topic_title":            "Concept Details",
    "notes_intro":            "",
    "notes_key_concepts":     ["Key concepts detail"],
    "notes_examples":         ["Example"],
    "notes_summary":          "Summary",
    "visual":                 {"visual_type": "none"},
}

# Required fields for quiz responses
_QUIZ_REQUIRED = {
    "type":       "quiz",
    "intent":     "quiz",
    "tags":       [],
    "quiz_title": "Quiz",
    "intro_text": "Let's start the quiz!",
    "visual":     {"visual_type": "none"},
    "questions":  [],
}

# Required fields per quiz question
_QUESTION_REQUIRED = {
    "question_number": 1,
    "bloom_level":     "Remember",
    "question_text":   "",
    "options":         {"A": "", "B": "", "C": "", "D": ""},
    "correct_option":  "A",
    "explanation":     "",
    "audio_script":    "",
    "visual_hint":     "",
}


def _validate_response(data: dict) -> dict:
    """
    Validate and fill missing fields in the LLM response.
    Ensures all required fields exist with correct types.
    """
    resp_type = data.get("type", "explanation")

    if resp_type == "quiz":
        template = _QUIZ_REQUIRED
    else:
        template = _EXPLANATION_REQUIRED

    # Fill missing top-level fields
    for key, default in template.items():
        if key not in data or data[key] is None:
            data[key] = default
        elif isinstance(default, list) and not isinstance(data[key], list):
            data[key] = [data[key]] if data[key] else default
        elif isinstance(default, str) and not isinstance(data[key], str):
            data[key] = str(data[key]) if data[key] else default
        elif isinstance(default, dict) and not isinstance(data[key], dict):
            data[key] = default

    # Validate visual object
    if "visual" not in data or not isinstance(data["visual"], dict):
        data["visual"] = {"visual_type": "none"}
    elif "visual_type" not in data["visual"]:
        data["visual"]["visual_type"] = "none"

    # Validate quiz questions
    if resp_type == "quiz" and data.get("questions"):
        validated_qs = []
        for i, q in enumerate(data["questions"]):
            if not isinstance(q, dict):
                continue
            for key, default in _QUESTION_REQUIRED.items():
                if key not in q or q[key] is None:
                    q[key] = default
            q["question_number"] = i + 1
            validated_qs.append(q)
        data["questions"] = validated_qs

    return data


# ══════════════════════════════════════════════════════════════════════════════
# JSON REPAIR HELPER (Item #23)
# ══════════════════════════════════════════════════════════════════════════════
def _attempt_json_repair(raw: str) -> dict | None:
    """Try to repair common JSON issues from LLM output."""
    clean = raw.strip()

    # Remove markdown code fences
    if clean.startswith("```json"):
        clean = clean[7:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    clean = clean.strip()

    # Try direct parse first
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object from surrounding text
    match = re.search(r'\{[\s\S]*\}', clean)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try fixing common issues: trailing commas
    fixed = re.sub(r',\s*([}\]])', r'\1', clean)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    return None


# ══════════════════════════════════════════════════════════════════════════════
# PARSE RESPONSE (Items #22, #23, #24)
# ══════════════════════════════════════════════════════════════════════════════
def parse_response(raw: str, fallback_title: str = "Concept Detail") -> dict:
    """
    Parse and validate the LLM JSON response.
    Includes JSON repair and structured fallback.
    """
    # Attempt 1: Direct parse
    data = _attempt_json_repair(raw)

    if data is not None:
        return _validate_response(data)

    # Attempt 2 failed — return structured fallback (Item #24)
    logger.warning("JSON parse failed after repair attempts. Using fallback.")
    fallback = {
        "type":                   "explanation",
        "intent":                 "explanation",
        "topic_title":            fallback_title,
        "learning_objectives":    [f"Understand {fallback_title}"],
        "prerequisites":          [],
        "notes_intro":            raw[:500] if len(raw) > 500 else raw,
        "notes_key_concepts":     ["Concept details are being processed..."],
        "notes_important_points": ["Key point 1", "Key point 2"],
        "notes_examples":         ["Real-world classroom example"],
        "common_mistakes":        [],
        "memory_tip":             "",
        "fun_fact":               "",
        "real_life_applications": [],
        "notes_summary":          "Summary of the explained concept.",
        "visual":                 {"visual_type": "none"},
        "follow_up_questions":    ["What more would you like to know?"],
        "audio_script":           raw[:500] if len(raw) > 500 else raw,
        "_error":                 "json_parse_failed",
        "_error_message":         "The AI response could not be parsed. Showing raw content.",
    }
    return fallback


# ══════════════════════════════════════════════════════════════════════════════
# RETRY WRAPPER (Item #23)
# ══════════════════════════════════════════════════════════════════════════════
def generate_and_parse(
    query: str,
    text_language: str = "English",
    audio_language: str = "English",
    num_questions: int = 5,
    difficulty: str = "Medium",
    question_type: str = "MCQ",
    class_level: int = 8,
    conversation_history: list = None,
    audio_requested: bool = True,
    fallback_title: str = "Concept Detail",
) -> dict:
    """
    Generate LLM response with automatic retry on failure using a Multi-Model Fallback Chain.
    Returns a validated, parsed dict.
    """
    # Item #5: Fallback Router Chain (Updated with active Groq models and high TPM limits)
    # Updated fallback chain with only the robust, valid Groq models
    fallback_chain = [_MODEL, "llama-3.1-8b-instant"]
    
    # Outer loop: Try each API key if Rate Limit is hit
    for key_idx, current_key in enumerate(API_KEYS):
        local_client = Groq(api_key=current_key) if current_key else None
        
        # Inner loop: Try fallback models
        for i, model in enumerate(fallback_chain):
            try:
                if i > 0:
                    logger.info(f"Retrying LLM call (Attempt {i+1}) using fallback model: {model} on Key #{key_idx+1}")
                    import time
                    time.sleep(1.0) # Brief wait on rate limits
                else:
                    logger.info(f"Attempt 1 using primary model: {model} on Key #{key_idx+1}")
                    
                local_max_tokens = 3000 if "8b" in model.lower() else _MAX_TOKENS

                raw = generate_response(
                    query, text_language, audio_language, num_questions, difficulty,
                    question_type, class_level, conversation_history, 
                    override_model=model, override_client=local_client,
                    override_max_tokens=local_max_tokens, audio_requested=audio_requested
                )
                data = _attempt_json_repair(raw)
                if data is not None:
                    return _validate_response(data)
            except Exception as e:
                err_str = str(e).lower()
                logger.error(f"Model {model} failed on Key #{key_idx+1}: {e}")
                
                # If rate limit hit, break inner loop to try next API KEY immediately
                if "rate limit" in err_str or "429" in err_str:
                    logger.info(f"Rate limit hit on Key #{key_idx+1}, switching to next API key.")
                    break 

    # Final fallback if ALL models in the chain fail
    return parse_response("", fallback_title=fallback_title)