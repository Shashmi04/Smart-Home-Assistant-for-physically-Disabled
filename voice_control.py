from vosk import Model, KaldiRecognizer
import pyaudio
import json
import sys

# Load model
model = Model("model")
recognizer = KaldiRecognizer(model, 44100)

# Setup microphone
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=44100,
                  input=True,
                  frames_per_buffer=8192)
stream.start_stream()

print(" Say 'hey assistant' to activate...")

active = False  # Flag for wake word

try:
    while True:
        data = stream.read(4096, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower().strip()

            if text:
                print("You said:", text)

                # Wake word
                if "hey assistant" in text:
                    active = True
                    print(" Listening for commands...")

                # Stop command
                elif "stop" in text or "exit" in text:
                    print(" Goodbye!")
                    break

                # Commands only if assistant is active
                elif active:
                    if "light on" in text:
                        print(" Turning ON the light...")
                    elif "light off" in text:
                        print(" Turning OFF the light...")
                    else:
                        print(" Command not recognized")

except Exception as e:
    print(" Error:", str(e))

finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()
    sys.exit()