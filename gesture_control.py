from cvzone.HandTrackingModule import HandDetector
import cv2, serial, time, threading

# ✅ Arduino Serial
arduino =None
time.sleep(2)

cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1, detectionCon=0.7)

prev_cmd = ""
send_lock = False  # avoid flooding

def send_command(cmd):
    global prev_cmd, send_lock
    if cmd != prev_cmd and not send_lock:
        send_lock = True
        prev_cmd = cmd
        threading.Thread(target=serial_thread, args=(cmd,)).start()

def serial_thread(cmd):
    global send_lock
    arduino.write((cmd + "\n").encode())
    print("Sent ->", cmd)
    time.sleep(0.4)
    send_lock = False

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    gesture = ""  # ✅ text to show on screen

    if hands:
        fingers = detector.fingersUp(hands[0])
        total = sum(fingers)

        # ✅ Gesture commands + UI text
        if total == 5:
            gesture = "LIGHT ON"
            send_command("LIGHT_ON")
        elif total == 0:
            gesture = "LIGHT OFF"
            send_command("LIGHT_OFF")
        elif fingers == [1,0,0,0,0]:
            gesture = "FAN ON"
            send_command("FAN_ON")
        elif fingers == [1,1,0,0,0]:
            gesture = "FAN OFF"
            send_command("FAN_OFF")
        elif fingers == [0,1,1,0,0]:
            gesture = "MUSIC ON"
            send_command("MUSIC_ON")
        elif fingers == [0,1,0,0,0]:
            gesture = "MUSIC OFF"
            send_command("MUSIC_OFF")
        elif fingers == [0,1,1,1,0]:
            gesture = "NEXT SONG"
            send_command("MUSIC_NEXT")
        elif fingers == [0,1,1,1,1]:
            gesture = "PREVIOUS SONG"
            send_command("MUSIC_PREV")

        # ✅ Show on screen
        cv2.putText(img, gesture, (50,80), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0,255,0), 3)

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
