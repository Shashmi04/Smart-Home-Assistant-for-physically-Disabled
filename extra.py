import time
import pyttsx3
import random

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)   # Speed of speech
engine.setProperty("volume", 1.0) # Volume (0.0 to 1.0)

# --- SIMULATED SENSOR VALUES ---
def read_gas_sensor():
    # Simulate random gas values (0-500)
    return random.randint(200, 500)

def read_water_level():
    # Simulate random water level % (0-100)
    return random.randint(0, 100)

def read_door_sensor():
    # Simulate motion detected (True/False)
    return random.choice([True, False])

# --- ALERT SYSTEM ---
def speak_alert(message):
    print(" ALERT:", message)
    engine.say(message)
    engine.runAndWait()

# --- MAIN LOOP ---
print(" Smart Home Assistant Simulation Started...")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        gas_value = read_gas_sensor()
        water_level = read_water_level()
        door_detected = read_door_sensor()

        # Gas Leak Detection
        if gas_value > 400:
            speak_alert(" Gas leak detected!")

        # Water Tank Full Detection
        if water_level > 90:
            speak_alert(" Water tank is full.")

        # Door Sensor Detection
        if door_detected:
            speak_alert(" Someone is at the door.")

        # Delay between readings
        time.sleep(3)

except KeyboardInterrupt:
    print("\n Smart Home Assistant Stopped.")
