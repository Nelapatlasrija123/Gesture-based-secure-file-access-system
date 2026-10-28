import cv2
import mediapipe as mp
import time
import os
import subprocess
import urllib.request

password_file = "password.txt"

# Check if legacy mp.solutions is available (MediaPipe <= 0.10.14)
HAS_SOLUTIONS = hasattr(mp, "solutions")

if HAS_SOLUTIONS:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1)
else:
    # Modern MediaPipe (0.10.15+) Tasks API
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")
    MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

    if not os.path.exists(MODEL_PATH):
        print("Downloading hand_landmarker.task model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully.")

    with open(MODEL_PATH, "rb") as f:
        model_data = f.read()

    base_options = python.BaseOptions(model_asset_buffer=model_data)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1
    )
    detector = vision.HandLandmarker.create_from_options(options)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

def draw_landmarks(image, landmarks):
    h, w, _ = image.shape
    for p1_idx, p2_idx in HAND_CONNECTIONS:
        pt1 = (int(landmarks[p1_idx].x * w), int(landmarks[p1_idx].y * h))
        pt2 = (int(landmarks[p2_idx].x * w), int(landmarks[p2_idx].y * h))
        cv2.line(image, pt1, pt2, (0, 255, 0), 2)
    for lm in landmarks:
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(image, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

def count_fingers(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    lms = hand_landmarks.landmark if hasattr(hand_landmarks, "landmark") else hand_landmarks

    fingers = []

    # thumb
    if lms[tip_ids[0]].x > lms[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # other fingers
    for id in range(1, 5):
        if lms[tip_ids[id]].y < lms[tip_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers.count(1)

cap = cv2.VideoCapture(0)

gesture_sequence = []
capture_interval = 2
last_capture = time.time()

print("Show finger gestures to the camera")

while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)

    if HAS_SOLUTIONS:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        detected_hands = results.multi_hand_landmarks if results.multi_hand_landmarks else []
        for handLms in detected_hands:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
    else:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        results = detector.detect(mp_image)
        detected_hands = results.hand_landmarks if results.hand_landmarks else []
        for handLms in detected_hands:
            draw_landmarks(img, handLms)

    if detected_hands:
        for handLms in detected_hands:
            if time.time() - last_capture > capture_interval:
                finger_count = count_fingers(handLms)
                gesture = f"G{finger_count}"
                gesture_sequence.append(gesture)
                print("Captured:", gesture)
                last_capture = time.time()

                if len(gesture_sequence) == 4:
                    break

    cv2.imshow("Gesture Lock", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

    if len(gesture_sequence) == 4:
        break

cap.release()
cv2.destroyAllWindows()

entered_password = " ".join(gesture_sequence)
print("Entered:", entered_password)

# FIRST RUN → SAVE PASSWORD
if not os.path.exists(password_file):
    with open(password_file, "w") as f:
        f.write(entered_password)

    print("Password saved successfully")
    print("Run program again to unlock file")

# SECOND RUN → VERIFY PASSWORD
else:
    with open(password_file, "r") as f:
        saved_password = f.read().strip()

    if entered_password == saved_password:
        print("ACCESS GRANTED")
        subprocess.run(["python", "decrypt_and_open.py"])
    else:
        print("ACCESS DENIED")
