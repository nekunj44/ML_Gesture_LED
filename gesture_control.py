import cv2
import mediapipe as mp
import serial
import time

# Connect to Arduino on COM port
arduino = serial.Serial('COM13', 9600)  # Change COM3 to your Arduino port
time.sleep(2)  # Wait for Arduino to reset

# MediaPipe setup
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip in tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            finger_count = count_fingers(handLms)

            # Send corresponding gesture code
            if finger_count == 5:
                arduino.write(b'1')  # Open palm
            elif finger_count == 0:
                arduino.write(b'2')  # Fist
            elif finger_count == 1:
                arduino.write(b'3')  # One finger
            elif finger_count == 2:
                arduino.write(b'4')  # Two fingers

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()