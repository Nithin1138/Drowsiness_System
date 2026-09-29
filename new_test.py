



























import cv2
import dlib
import numpy as np
from imutils import face_utils
import serial
import time
import requests
import os

# Helper functions
def single_eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def eye_aspect_ratio(left_eye, right_eye):
    left_ear = single_eye_aspect_ratio(left_eye)
    right_ear = single_eye_aspect_ratio(right_eye)
    return (left_ear + right_ear) / 2.0

def mouth_aspect_ratio(mouth):
    A = np.linalg.norm(mouth[2] - mouth[10])
    B = np.linalg.norm(mouth[4] - mouth[8])
    C = np.linalg.norm(mouth[0] - mouth[6])
    mar = (A + B) / (2.0 * C)
    return mar

def get_head_position(shape):
    """Returns the (x, y) coordinates of the nose tip as a proxy for head position."""
    return (shape[30][0], shape[30][1])

# Try to connect Arduino
try:
    arduino = serial.Serial('COM5', 9600)  # change COM3 to your Arduino port
    time.sleep(2)
    print("✅ Connected to Arduino.")
except:
    arduino = None
    print("⚠ Arduino not connected, running in camera-only mode.")

# Dlib setup
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Landmark indexes
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

# Constants
EYE_AR_THRESH = 0.25
WARNING_FRAMES = 15
STOP_FRAMES = 30
CRITICAL_FRAMES = 200

MOUTH_AR_THRESH = 0.70
YAWN_CONSEC_FRAMES = 10

STILLNESS_PIXEL_THRESH = 3  # Maximum pixel movement to be considered "still"
STILLNESS_FRAMES_THRESH = 300 # Approx. 15 seconds at 20 FPS

# Counters and State
EYE_COUNTER = 0
YAWN_COUNTER = 0
STILLNESS_COUNTER = 0
last_head_position = None
STATE = "N"
last_state = None  # To track changes
last_sent_status = None  # Track last status sent to backend

# Backend configuration
BACKEND_URL = "http://localhost:5000/update_status"

def resolve_active_number() -> str | None:
    # Prefer environment variable
    env_num = os.environ.get('ACTIVE_NUMBER', '').strip()
    if env_num:
        return env_num
    # Fallback to first stored number
    try:
        with open('data/numbers.txt', 'r') as f:
            for line in f:
                num = line.strip()
                if num:
                    return num
    except Exception:
        pass
    return None

ACTIVE_NUMBER = resolve_active_number()

def map_state_to_backend_status(state: str) -> str:
    """Map internal STATE to backend-friendly status labels."""
    if state == "N":
        return "Awake"
    if state == "B":
        return "Drowsy"
    # Treat both stop and emergency as alerts sent
    if state in ("X", "E"):
        return "Alert Sent"
    return "Awake"

def send_status_to_backend(status_text: str) -> None:
    """POST status change to Flask backend; ignore errors if backend is down."""
    try:
        payload = {"status": status_text}
        if ACTIVE_NUMBER:
            payload["number"] = ACTIVE_NUMBER
        requests.post(BACKEND_URL, json=payload, timeout=2)
    except Exception:
        # Silently ignore to avoid interrupting video loop
        pass

# Robust camera initialization for Windows
def open_camera() -> cv2.VideoCapture:
    backends = [
        getattr(cv2, 'CAP_DSHOW', None),
        getattr(cv2, 'CAP_MSMF', None),
        None,  # default
    ]
    indices = [0, 1, 2, 3]
    for backend in backends:
        for idx in indices:
            try:
                if backend is not None:
                    cap = cv2.VideoCapture(idx, backend)
                else:
                    cap = cv2.VideoCapture(idx)
                if cap is not None and cap.isOpened():
                    print(f"[Camera] Opened camera index {idx} with backend {backend}.")
                    return cap
                if cap is not None:
                    cap.release()
            except Exception as e:
                try:
                    if cap is not None:
                        cap.release()
                except Exception:
                    pass
    print("[Camera] ERROR: Could not open camera. Ensure no other app is using it and permissions are granted.")
    return None

cap = open_camera()
if cap is None:
    raise SystemExit(1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("[Camera] WARNING: Failed to grab frame from camera.")
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector
    
    (gray, 0)

    if len(rects) == 0:
        last_head_position = None
        EYE_COUNTER = 0
        YAWN_COUNTER = 0
        STILLNESS_COUNTER = 0
        STATE = "N"
        cv2.putText(frame, "No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            mouth = shape[mStart:mEnd]
            ear = eye_aspect_ratio(leftEye, rightEye)
            mar = mouth_aspect_ratio(mouth)

            leftHull = cv2.convexHull(leftEye)
            rightHull = cv2.convexHull(rightEye)
            mouthHull = cv2.convexHull(mouth)
            cv2.drawContours(frame, [leftHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)

            current_head_position = get_head_position(shape)
            if last_head_position is not None:
                movement_dist = np.linalg.norm(np.array(current_head_position) - np.array(last_head_position))
                if movement_dist < STILLNESS_PIXEL_THRESH:
                    STILLNESS_COUNTER += 1
                else:
                    STILLNESS_COUNTER = 0
            last_head_position = current_head_position

            if STILLNESS_COUNTER >= STILLNESS_FRAMES_THRESH:
                STATE = "E"
                cv2.putText(frame, "EMERGENCY: DRIVER UNRESPONSIVE?", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "STOPPING VEHICLE", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            elif ear < EYE_AR_THRESH:
                EYE_COUNTER += 1
                if EYE_COUNTER >= CRITICAL_FRAMES:
                    STATE = "X"
                    cv2.putText(frame, "CRITICAL ALERT! (10 SEC)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                elif EYE_COUNTER >= STOP_FRAMES:
                    STATE = "X"
                    cv2.putText(frame, "STOP - DRIVER ASLEEP!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                elif EYE_COUNTER >= WARNING_FRAMES:
                    STATE = "B"
                    cv2.putText(frame, "WARNING - Sleepy!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            else:
                EYE_COUNTER = 0
                if mar > MOUTH_AR_THRESH:
                    YAWN_COUNTER += 1
                    if YAWN_COUNTER >= YAWN_CONSEC_FRAMES:
                        cv2.putText(frame, "YAWN DETECTED - Feeling Sleepy", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        # Notify backend about yawn event once per sustained yawn episode
                        if last_sent_status != "Yawning":
                            send_status_to_backend("Yawning")
                            last_sent_status = "Yawning"
                else:
                    YAWN_COUNTER = 0
                    STATE = "N"
                    cv2.putText(frame, "Awake", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # On state change, send to Arduino and backend
    if STATE != last_state:
        if arduino:
            arduino.write(STATE.encode())
        backend_status = map_state_to_backend_status(STATE)
        if backend_status != last_sent_status:
            send_status_to_backend(backend_status)
            last_sent_status = backend_status
        last_state = STATE
        

    cv2.imshow("Driver Monitor", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
if arduino:
    arduino.write(b'N')
    arduino.close()
cv2.destroyAllWindows()