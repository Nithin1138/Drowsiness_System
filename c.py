import cv2
import dlib
import numpy as np
from imutils import face_utils
import serial
import time
import requests
import os
import threading

# Helper functions (No changes)
def single_eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5]); B = np.linalg.norm(eye[2] - eye[4]); C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C) if C > 1e-6 else 0.0
def eye_aspect_ratio(left_eye, right_eye):
    left_ear = single_eye_aspect_ratio(left_eye); right_ear = single_eye_aspect_ratio(right_eye)
    return (left_ear + right_ear) / 2.0
def mouth_aspect_ratio(mouth):
    A = np.linalg.norm(mouth[2] - mouth[10]); B = np.linalg.norm(mouth[4] - mouth[8]); C = np.linalg.norm(mouth[0] - mouth[6])
    return (A + B) / (2.0 * C) if C > 1e-6 else 0.0
def get_head_position(shape):
    return (shape[30][0], shape[30][1])

# --- Constants ---
# --- !!! IMPORTANT: TUNE THESE THRESHOLDS !!! ---
EYE_AR_THRESH = 0.23  # ADJUST based on your observation of EAR values
MOUTH_AR_THRESH = 0.60 # ADJUST based on your observation of MAR values during yawns
# --- !!! TUNE THE VALUES ABOVE !!! ---

# Frame count thresholds (Based on your new logic)
DROWSY_FRAMES_THRESH = 20   # ~1.5 sec eye closure for "Drowsy" (State 'B')
SLEEPY_FRAMES_THRESH = 75   # ~3-4 sec eye closure for "Sleepy" (State 'X')
YAWN_FRAMES_THRESH = 8     # Frames mouth must be open for a yawn (State 'Y')
# Threshold for visual "No Movement" text AND for escalating 'X' to 'E'
NO_MOVEMENT_FRAMES_THRESH = 150 # ~7-8 seconds
# Threshold for independent unresponsive alert (Path A)
STILLNESS_FRAMES_THRESH = 300 # ~15 sec for unresponsive alert (State 'E')
STILLNESS_PIXEL_THRESH = 5.0
DISTRACTION_ANGLE_THRESH = 30.0
DISTRACTION_FRAMES_THRESH = 60 # ~3 sec for distraction alert (State 'B')

# Performance tuning
CAMERA_WIDTH = 640; CAMERA_HEIGHT = 480; DETECT_SCALE = 0.5

# --- Setup ---
arduino = None
ARDUINO_PORT = 'COM5'
try:
    if 'arduino' in locals() and arduino and getattr(arduino, "is_open", False):
        arduino.close(); time.sleep(0.5)
    arduino = serial.Serial(ARDUINO_PORT, 9600, timeout=1); time.sleep(2)
    print(f"✅ Connected to Arduino on {ARDUINO_PORT}.")
except Exception as e:
    arduino = None
    print(f"⚠ Arduino connection failed on {ARDUINO_PORT}: {e}")

print("-> Loading dlib models...")
try:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
except Exception as e:
     print(f"[ERROR] Failed to load dlib models: {e}"); raise SystemExit(1)
print("✅ Models loaded.")

try:
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]
except KeyError as e: print(f"[ERROR] Landmark key error: {e}"); raise SystemExit(1)

EYE_COUNTER, YAWN_COUNTER, STILLNESS_COUNTER, DISTRACTION_COUNTER = 0, 0, 0, 0
last_head_position = None
STATE, last_state, last_sent_status = "N", None, None
BACKEND_URL = "http://localhost:5000/update_status"; ACTIVE_NUMBER = 'default_user'

# Backend communication
def send_status_to_backend(status_text: str) -> None:
    def task():
        try: 
            payload = {"status": status_text, "number": ACTIVE_NUMBER}
            requests.post(BACKEND_URL, json=payload, timeout=2)
            print(f"   -> Sent '{status_text}' to backend.")
        except Exception: pass
    threading.Thread(target=task, daemon=True).start()

def map_state_to_backend_status(state: str) -> str:
    """Maps Arduino state to backend status for logging/SMS"""
    if state == "N": return "Awake"
    if state == "Y": return "Yawning"
    if state == "B": return "Drowsy"   # Drowsy or Distracted
    if state == "X": return "Sleepy alert" # This is now a "Sleepy" alert
    if state == "E": return "Alert Sent" # This is the "Emergency" alert
    return "Awake"

model_points = np.array([(0.0, 0.0, 0.0), (0.0, -330.0, -65.0), (-225.0, 170.0, -135.0), (225.0, 170.0, -135.0), (-150.0, -150.0, -125.0), (150.0, -150.0, -125.0)], dtype="double")

# Camera Initialization
print("-> Initializing camera..."); cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened(): print("[Camera] ERROR: Could not open camera."); raise SystemExit(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH); actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"✅ Camera initialized (Res: {actual_width}x{actual_height})."); focal_length = actual_width
camera_matrix = np.array([[focal_length, 0, actual_width / 2], [0, focal_length, actual_height / 2], [0, 0, 1]], dtype="double"); dist_coeffs = np.zeros((4, 1))
time.sleep(1.0)

# --- Main Loop ---
while True:
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0:
        key = cv2.waitKey(30) & 0xFF
        if key == 27: print("-> ESC pressed during frame error."); break
        continue

    current_state_this_frame = "N"; status_text, status_color = "Awake", (0, 255, 0)
    display_ear, display_mar = 0.0, 0.0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small_gray = cv2.resize(gray, (0, 0), fx=DETECT_SCALE, fy=DETECT_SCALE)
    rects = detector(small_gray, 0)
    rects = [dlib.rectangle(int(r.left() / DETECT_SCALE), int(r.top() / DETECT_SCALE), int(r.right() / DETECT_SCALE), int(r.bottom() / DETECT_SCALE)) for r in rects]

    if not rects:
        EYE_COUNTER, YAWN_COUNTER, STILLNESS_COUNTER, DISTRACTION_COUNTER = 0, 0, 0, 0
        last_head_position = None; status_text, status_color = "No face detected", (0, 0, 255)
    else:
        rect = rects[0]
        try: shape = predictor(gray, rect); shape_np = face_utils.shape_to_np(shape)
        except Exception as e: print(f"[Dlib] Predictor failed: {e}"); continue

        ear = eye_aspect_ratio(shape_np[lStart:lEnd], shape_np[rStart:rEnd])
        mar = mouth_aspect_ratio(shape_np[mStart:mEnd])
        display_ear, display_mar = ear, mar

        cv2.drawContours(frame, [cv2.convexHull(shape_np[lStart:lEnd])], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [cv2.convexHull(shape_np[rStart:rEnd])], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [cv2.convexHull(shape_np[mStart:mEnd])], -1, (0, 255, 0), 1)

        # --- Update All Counters Independently ---
        yaw = 0.0
        try:
            image_points = np.array([shape_np[30], shape_np[8], shape_np[36], shape_np[45], shape_np[48], shape_np[54]], dtype="double")
            (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector); pose_angles = cv2.RQDecomp3x3(rotation_matrix)[0]; yaw = pose_angles[1]
            (nose_end_point2D, _) = cv2.projectPoints(np.array([(0.0, 0.0, 500.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
            p1 = tuple(image_points[0].astype(int)); p2 = tuple(nose_end_point2D[0][0].astype(int)); cv2.line(frame, p1, p2, (255, 0, 0), 2)
        except: pass
        if abs(yaw) > DISTRACTION_ANGLE_THRESH: DISTRACTION_COUNTER += 1
        else: DISTRACTION_COUNTER = 0

        current_head_position = get_head_position(shape_np)
        if last_head_position is not None:
            movement = np.linalg.norm(np.array(current_head_position) - np.array(last_head_position))
            if movement < STILLNESS_PIXEL_THRESH: STILLNESS_COUNTER += 1
            else: STILLNESS_COUNTER = 0
        last_head_position = current_head_position

        if ear < EYE_AR_THRESH: EYE_COUNTER += 1
        else: EYE_COUNTER = 0
        
        if mar > MOUTH_AR_THRESH: YAWN_COUNTER += 1
        else: YAWN_COUNTER = 0
        
        # --- Determine State and Text based on PRIORITY ---
        if STILLNESS_COUNTER >= STILLNESS_FRAMES_THRESH:
            current_state_this_frame = "E"; status_text = "EMERGENCY: UNRESPONSIVE?"; status_color = (0, 0, 255)
        elif EYE_COUNTER >= SLEEPY_FRAMES_THRESH:
            current_state_this_frame = "X"; status_text = "Driver Sleepy!"; status_color = (0, 0, 255)
            # --- NEW ESCALATION LOGIC (Path B) ---
            if STILLNESS_COUNTER >= NO_MOVEMENT_FRAMES_THRESH:
                 current_state_this_frame = "E"; status_text = "EMERGENCY: Sleepy + No Movement"; status_color = (0, 0, 255)
        elif DISTRACTION_COUNTER >= DISTRACTION_FRAMES_THRESH:
            current_state_this_frame = "B"; status_text = "DISTRACTION DETECTED!"; status_color = (0, 165, 255)
        elif EYE_COUNTER >= DROWSY_FRAMES_THRESH:
            current_state_this_frame = "B"; status_text = "Driver Drowsy!"; status_color = (0, 255, 255)
        elif YAWN_COUNTER >= YAWN_FRAMES_THRESH:
            current_state_this_frame = "Y"; status_text = "Yawn Detected"; status_color = (0, 255, 255)
        else:
            current_state_this_frame = "N"; status_text = "Awake"; status_color = (0, 255, 0)
        
        # Draw the final status text for the frame
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        # Draw EAR and MAR for tuning
        cv2.putText(frame, f"EAR: {display_ear:.2f}", (frame.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"MAR: {display_mar:.2f}", (frame.shape[1] - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # --- Update Global State & Communicate ---
    STATE = current_state_this_frame
    if STATE != last_state:
        print(f"STATE Change: {last_state} -> {STATE}")
        if arduino:
            try: arduino.write(STATE.encode())
            except Exception as e: print(f"[Arduino] Error writing: {e}")
        
        backend_status = map_state_to_backend_status(STATE)
        if backend_status != last_sent_status:
            send_status_to_backend(backend_status)
            last_sent_status = backend_status
        last_state = STATE

    try: cv2.imshow("Advanced Driver Monitor", frame)
    except Exception as e: print(f"[Display] Error showing frame: {e}. Exiting..."); break

    key = cv2.waitKey(1) & 0xFF
    if key == 27: print("-> ESC key pressed. Exiting..."); break

# --- Cleanup ---
print("-> Shutting down...")
cap.release()
if arduino:
    try: arduino.write(b'N'); arduino.close()
    except Exception: pass
cv2.destroyAllWindows()
time.sleep(0.5)
print("✅ Shutdown complete.")

