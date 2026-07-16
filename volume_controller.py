"""
Gesture Volume Controller (pyautogui version)
Pinch thumb + index finger closer/farther to decrease/increase system volume.
Uses media keys via pyautogui -> no pycaw/comtypes dependency, works cross-platform.
"""

import cv2
import mediapipe as mp
import numpy as np
import math
import time
import pyautogui

# ---------------- MediaPipe Setup ----------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Distance range for pinch gesture (calibrate if needed)
MIN_DIST = 20
MAX_DIST = 200

# Volume is tracked as a 0-100 percentage locally, since media keys
# don't report the OS's actual current volume back to us.
vol_per = 50          # assume starting around 50%, adjust if needed
prev_vol_per = 50
vol_bar = 400

# Debounce so we don't spam key presses every single frame
last_press_time = 0
PRESS_DELAY = 0.05     # seconds between key presses
STEP = 2               # % change per key press (matches typical OS volume step)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    lm_list = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            for idx, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((idx, cx, cy))
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    if lm_list:
        # Thumb tip = 4, Index tip = 8
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(frame, (x1, y1), 10, (255, 0, 255), -1)
        cv2.circle(frame, (x2, y2), 10, (255, 0, 255), -1)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

        length = math.hypot(x2 - x1, y2 - y1)

        # Map pinch distance -> target volume percentage
        target_vol_per = np.interp(length, [MIN_DIST, MAX_DIST], [0, 100])
        vol_bar = np.interp(length, [MIN_DIST, MAX_DIST], [400, 150])

        # Only send a key press if target moved enough (avoids spamming)
        now = time.time()
        if now - last_press_time > PRESS_DELAY:
            if target_vol_per > prev_vol_per + STEP:
                pyautogui.press("volumeup")
                prev_vol_per = min(100, prev_vol_per + STEP)
                last_press_time = now
            elif target_vol_per < prev_vol_per - STEP:
                pyautogui.press("volumedown")
                prev_vol_per = max(0, prev_vol_per - STEP)
                last_press_time = now

        vol_per = prev_vol_per

        if length < MIN_DIST:
            cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)

    # Volume bar UI
    cv2.rectangle(frame, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (255, 0, 0), -1)
    cv2.putText(frame, f'{int(vol_per)} %', (40, 430),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Gesture Volume Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
