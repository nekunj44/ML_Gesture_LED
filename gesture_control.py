"""
Gesture‑to‑LED controller
------------------------
Requires:
    pip install opencv-python mediapipe pyserial
Make sure your Arduino sketch is running and listening at 9600 baud.
"""

import time
import cv2
import mediapipe as mp
import serial
import serial.tools.list_ports

# ========= Serial helpers ========= #
def find_arduino_port():
    """Return the first serial port that looks like an Arduino."""
    for p in serial.tools.list_ports.comports():
        if ("Arduino" in p.description) or ("CH340" in p.description) or ("USB‑SERIAL" in p.description):
            return p.device           # e.g. 'COM4' on Windows or '/dev/ttyACM0' on Linux
    raise IOError("🔌  No Arduino found – is it plugged in and the driver installed?")

# Pick a port automatically (or hard‑code e.g. 'COM13')
PORT = 'COM15'
BAUD = 9600

print(f"🔗  Connecting to Arduino on {PORT} @ {BAUD} baud …")
arduino = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)        # give the Arduino time to reset
print("✅  Serial link established.")

# ========= MediaPipe setup ========= #
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
mp_draw = mp.solutions.drawing_utils

# Indices of fingertips in MediaPipe model
FINGERTIP_IDS = [4, 8, 12, 16, 20]

# Utility for finger counting
def count_raised_fingers(hand_landmarks):
    """Return how many fingers are up (0‑5) for a right hand."""
    lm = hand_landmarks.landmark
    fingers = []

    # Thumb (compare x positions instead of y)
    fingers.append(1 if lm[FINGERTIP_IDS[0]].x < lm[FINGERTIP_IDS[0] - 1].x else 0)

    # 4 other fingers (compare y to knuckle two indices below)
    for tip_id in FINGERTIP_IDS[1:]:
        fingers.append(1 if lm[tip_id].y < lm[tip_id - 2].y else 0)

    return sum(fingers)

# ========= Video capture loop ========= #
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("❌  Cannot open webcam")

last_command = None        # remember last code sent so we don’t spam serial

def send_command(code_byte):
    global last_command
    if code_byte != last_command:
        arduino.write(code_byte)
        last_command = code_byte
        print(f"➡️  Sent command {code_byte} to Arduino")

print("\n🤚  Show a gesture to your webcam:")
print("     5 fingers → Pattern 1  (Chaser)")
print("     0 fingers → Pattern 2  (All Blink)")
print("     1 finger  → Pattern 3  (Bounce)")
print("     2 fingers → Pattern 4  (Odd/Even Blink)")
print("Press  q  to quit.\n")

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)                      # mirror for natural interaction
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture_label = "None"

        if result.multi_hand_landmarks:
            for hand_lms in result.multi_hand_landmarks:
                count = count_raised_fingers(hand_lms)
                # Map counts to commands
                if count == 5:
                    send_command(b'1'); gesture_label = "Open‑Palm (5)"
                elif count == 0:
                    send_command(b'2'); gesture_label = "Fist (0)"
                elif count == 1:
                    send_command(b'3'); gesture_label = "One Finger (1)"
                elif count == 2:
                    send_command(b'4'); gesture_label = "Two Fingers (2)"
                else:
                    # For counts 3 or 4 we don't send anything
                    last_command = None
                    gesture_label = f"{count} fingers (no cmd)"

                mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

        # Display the current gesture
        cv2.putText(frame, f"Gesture: {gesture_label}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Gesture → LED Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up
    cap.release()
    hands.close()
    arduino.close()
    cv2.destroyAllWindows()
    print("👋  Goodbye!")
