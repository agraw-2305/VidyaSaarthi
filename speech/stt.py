from groq import Groq
import os


from dotenv import load_dotenv
load_dotenv(override=True)

_keys_str = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [k.strip() for k in _keys_str.split(",") if k.strip()]
if not API_KEYS:
    single_key = os.getenv("GROQ_API_KEY", "").strip()
    API_KEYS = [single_key] if single_key else []

api_key = API_KEYS[0] if API_KEYS else None
client = Groq(api_key=api_key) if api_key else None
# Known Whisper hallucination phrases to reject
HALLUCINATIONS = {
    "झाल", "झाल झाल", "धन्यवाद", "subscribe", "subscribed",
    "thank you", "thanks for watching", ".", "..", "...", ""
}

def speech_to_text(audio_path):
    if not client:
        return "[Error: GROQ API Key is missing. Please check your .env file]"

    # Check if file exists
    if not os.path.exists(audio_path):
        return "[Audio file missing — please try again]"

    # Reject tiny/empty audio files (< 5KB = likely silence)
    file_size = os.path.getsize(audio_path)
    if file_size < 5000:
        return "[Audio too short — please speak clearly and try again]"

    _, ext = os.path.splitext(audio_path)
    ext = ext.lower().strip(".")
    mime_type = "audio/mpeg" if ext == "mp3" else f"audio/{ext}" if ext else "audio/webm"

    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=(os.path.basename(audio_path), audio_file, mime_type),
            prompt="Teacher is giving instructions to students in Hindi or Hinglish.",
            response_format="text"
        )

    result = transcription.strip()

    # Reject known hallucinated phrases
    if result.lower().strip(".,!? ") in {h.lower() for h in HALLUCINATIONS}:
        return "[Could not understand — please speak again]"

    return result
