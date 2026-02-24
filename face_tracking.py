import cv2
import mediapipe as mp
import numpy as np
import time
import serial  # for Arduino

# ---------------------------
# Config
# ---------------------------
YAW_LEFT_TH = -15
YAW_RIGHT_TH = 15
SMILE_RATIO_TH = 0.60
MOUTH_OPEN_RATIO_TH = 0.28
DISPLAY_DURATION = 1.5
EYE_CLOSE_TH = 0.23
EYE_CLOSE_TIME = 2.0
# ---------------------------

# Set your Arduino COM port (check in Arduino IDE → Tools → Port)
arduino = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)  # wait for serial to connect

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

current_fan_state = None
current_light_state = None
display_text = ""
display_expires_at = 0.0
eyes_closed_start = None

def send_to_arduino(cmd):
    try:
        arduino.write((cmd + "\n").encode())
    except:
        pass

def pt(landmarks, idx, w, h):
    l = landmarks[idx]
    return np.array([l.x * w, l.y * h], dtype=np.float32)

def eye_aspect_ratio(landmarks, eye_indices, w, h):
    p = [pt(landmarks, i, w, h) for i in eye_indices]
    A = np.linalg.norm(p[1] - p[5])
    B = np.linalg.norm(p[2] - p[4])
    C = np.linalg.norm(p[0] - p[3])
    ear = (A + B) / (2.0 * C)
    return ear

try:
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break

        h, w = frame.shape[:2]
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(frame_rgb)

        if result.multi_face_landmarks:
            landmarks = result.multi_face_landmarks[0].landmark

            left_mouth = pt(landmarks, 61, w, h)
            right_mouth = pt(landmarks, 291, w, h)
            top_mouth = pt(landmarks, 13, w, h)
            bottom_mouth = pt(landmarks, 14, w, h)
            left_eye = pt(landmarks, 33, w, h)
            right_eye = pt(landmarks, 263, w, h)

            mouth_w = np.linalg.norm(right_mouth - left_mouth)
            mouth_h = np.linalg.norm(bottom_mouth - top_mouth)
            interocular = np.linalg.norm(right_eye - left_eye) + 1e-6

            mouth_open_ratio = mouth_h / interocular
            smile_ratio = mouth_w / interocular

            mouth_status = "NEUTRAL"
            if mouth_open_ratio > MOUTH_OPEN_RATIO_TH:
                mouth_status = "OPEN"
            elif smile_ratio > SMILE_RATIO_TH:
                mouth_status = "SMILE"

            # EAR for both eyes
            LEFT_EYE = [33, 160, 158, 133, 153, 144]
            RIGHT_EYE = [362, 385, 387, 263, 373, 380]
            left_EAR = eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
            right_EAR = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
            avg_EAR = (left_EAR + right_EAR) / 2.0

            # Emergency detection (eyes closed)
            now = time.time()
            if avg_EAR < EYE_CLOSE_TH:
                if eyes_closed_start is None:
                    eyes_closed_start = now
                elif now - eyes_closed_start > EYE_CLOSE_TIME:
                    display_text = "🚨 EMERGENCY ALERT! (Eyes Closed) 🚨"
                    display_expires_at = now + DISPLAY_DURATION
                    print(display_text)
                    send_to_arduino("MUSIC_NEXT")  # Emergency = trigger next
                    eyes_closed_start = None
            else:
                eyes_closed_start = None

            # Head pose for fan control
            nose = pt(landmarks, 1, w, h)
            chin = pt(landmarks, 199, w, h)
            image_points = np.array([
                (nose[0], nose[1]),
                (chin[0], chin[1]),
                (left_eye[0], left_eye[1]),
                (right_eye[0], right_eye[1]),
                (left_mouth[0], left_mouth[1]),
                (right_mouth[0], right_mouth[1])
            ], dtype="double")

            model_points = np.array([
                (0.0, 0.0, 0.0),
                (0.0, -330.0, -65.0),
                (-225.0, 170.0, -135.0),
                (225.0, 170.0, -135.0),
                (-150.0, -150.0, -125.0),
                (150.0, -150.0, -125.0)
            ])

            focal_length = w
            center = (w / 2.0, h / 2.0)
            camera_matrix = np.array(
                [[focal_length, 0, center[0]],
                 [0, focal_length, center[1]],
                 [0, 0, 1]], dtype="double"
            )
            dist_coeffs = np.zeros((4, 1))

            success = False
            try:
                success, rotation_vector, translation_vector = cv2.solvePnP(
                    model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
                )
            except cv2.error:
                success = False

            if success:
                rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
                pose_mat = cv2.hconcat((rotation_matrix, translation_vector))
                _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
                pitch, yaw, roll = [float(angle[0]) for angle in euler_angles]

                # Fan control
                if yaw < YAW_LEFT_TH:
                    if current_fan_state != "Fan ON":
                        current_fan_state = "Fan ON"
                        display_text = "FACE LEFT -> Fan ON"
                        display_expires_at = time.time() + DISPLAY_DURATION
                        print(display_text)
                        send_to_arduino("FAN_ON")

                elif yaw > YAW_RIGHT_TH:
                    if current_fan_state != "Fan OFF":
                        current_fan_state = "Fan OFF"
                        display_text = "FACE RIGHT -> Fan OFF"
                        display_expires_at = time.time() + DISPLAY_DURATION
                        print(display_text)
                        send_to_arduino("FAN_OFF")

            # Light control
            if mouth_status == "SMILE":
                if current_light_state != "Light ON":
                    current_light_state = "Light ON"
                    display_text = "SMILE -> Light ON"
                    display_expires_at = time.time() + DISPLAY_DURATION
                    print(display_text)
                    send_to_arduino("LIGHT_ON")

            elif mouth_status == "OPEN":
                if current_light_state != "Light OFF":
                    current_light_state = "Light OFF"
                    display_text = "MOUTH OPEN -> Light OFF"
                    display_expires_at = time.time() + DISPLAY_DURATION
                    print(display_text)
                    send_to_arduino("LIGHT_OFF")

        # Display alert text
        if time.time() < display_expires_at and display_text:
            cv2.putText(frame, display_text, (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Smart Home Face Control + Eye Emergency", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    face_mesh.close()
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
