"""
wake_word.py — מאזין ל-"Hey Sachbak" ברקע ומפעיל dispatch אוטומטי
הרץ: uv run python wake_word.py
"""
import subprocess
import os
import struct
import time
import pyaudio
import pvporcupine
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Sachbak wake word listener starting...")
    print("Say 'Hey Sachbak' to activate!")

    porcupine = pvporcupine.create(
        access_key=os.getenv("PORCUPINE_ACCESS_KEY"),
        keywords=["hey siri"],  # הכי קרוב ל-"hey friday" בחינמי
        # לחלופין השתמש ב-keyword_paths עם קובץ .ppn מותאם אישית
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    last_dispatch = 0

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm)

            if result >= 0:
                now = time.time()
                if now - last_dispatch > 5:  # מנע dispatch כפול
                    print("Wake word detected! Activating Sachbak...")
                    subprocess.run([
                        r"C:\claude\jarvis\friday-tony-stark-demo\livekit\lk.exe",
                        "dispatch", "create",
                        "--room", "my-room",
                        "--agent-name", "sachbak",
                        "--url", "ws://localhost:7880",
                        "--api-key", "devkey",
                        "--api-secret", "secret"
                    ])
                    last_dispatch = now
    finally:
        stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    main()
