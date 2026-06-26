import edge_tts
import asyncio
import threading
import os
import uuid

import time
import glob

VOICE_MAP = {
    "Hindi":    "hi-IN-SwaraNeural",
    "English":  "en-IN-NeerjaNeural",
    "Hinglish": "hi-IN-SwaraNeural"
}

async def _generate(text, voice, path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

def text_to_speech(text, language="Hinglish"):
    voice = VOICE_MAP.get(language, "hi-IN-SwaraNeural")
    os.makedirs("temp", exist_ok=True)
    # Cleanup old TTS files (older than 1 hour)
    try:
        now = time.time()
        for f in glob.glob("temp/tts_*.mp3"):
            if os.path.getmtime(f) < now - 3600:
                os.remove(f)
    except Exception as e:
        print("Cleanup error:", e)

    output_path = f"temp/tts_{uuid.uuid4().hex[:8]}.mp3"

    def run():
        asyncio.run(_generate(text, voice, output_path))

    t = threading.Thread(target=run)
    t.start()
    t.join()
    return output_path