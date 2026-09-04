import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os
import time
import pyautogui

model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Завантаження моделі MediaPipe Hand Landmarker...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

global_cooldown = 1.0

vol_active = False
vol_anchor_y = 0.0
vol_threshold = 0.06 

win_active = False
win_anchor_x = 0.0
win_threshold = 0.05 
last_window_switch = 0.0
window_cooldown = 0.6 

fist_active = False
fist_start_time = 0.0
fist_anchor_y = 0.0 
last_mute_time = 0.0

peace_active = False
peace_start_time = 0.0
last_media_time = 0.0

three_active = False
three_start_time = 0.0
last_f_time = 0.0

with vision.HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(time.time() * 1000)
        
        result = landmarker.detect_for_video(mp_image, timestamp_ms)
        current_time = time.time()

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                h, w, _ = frame.shape
                
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), cv2.FILLED)


                tips_ids = [8, 12, 16, 20]
                pip_ids = [6, 10, 14, 18] 

                fingers_up = []
                for i in range(4):
                    fingers_up.append(hand_landmarks[tips_ids[i]].y < hand_landmarks[pip_ids[i]].y)

                index_up, middle_up, ring_up, pinky_up = fingers_up
                current_wrist_y = hand_landmarks[0].y

                if index_up and not middle_up and not ring_up and not pinky_up:
                    current_y = hand_landmarks[8].y
                    if not vol_active:
                        vol_active = True
                        vol_anchor_y = current_y 
                    else:
                        delta_y = current_y - vol_anchor_y
                        if delta_y < -vol_threshold:
                            print("Вгору -> Гучність +4")
                            pyautogui.press('volumeup', presses=2)
                            vol_anchor_y = current_y 
                        elif delta_y > vol_threshold:
                            print("Вниз -> Гучність -4")
                            pyautogui.press('volumedown', presses=2)
                            vol_anchor_y = current_y
                else:
                    vol_active = False

                if index_up and middle_up and not ring_up and not pinky_up:
                    if not peace_active:
                        peace_start_time = current_time
                        peace_active = True
                    elif current_time - peace_start_time > 0.8 and (current_time - last_media_time > global_cooldown):
                        print("Жест 2 пальці -> Play/Pause")
                        pyautogui.press('playpause')
                        last_media_time = current_time
                        peace_active = False
                else:
                    peace_active = False

                # 3. КЛАВІША F / ПОВНИЙ ЕКРАН (3 пальці — утримання 0.8 с)
                if index_up and middle_up and ring_up and not pinky_up:
                    if not three_active:
                        three_start_time = current_time
                        three_active = True
                    elif current_time - three_start_time > 0.8 and (current_time - last_f_time > global_cooldown):
                        print("Жест 3 пальці -> Натиснуто 'F'")
                        pyautogui.press('f')
                        last_f_time = current_time
                        three_active = False
                else:
                    three_active = False

                if index_up and middle_up and ring_up and pinky_up:
                    current_x = hand_landmarks[9].x 
                    if not win_active:
                        win_active = True
                        win_anchor_x = current_x
                    else:
                        delta_x = current_x - win_anchor_x
                        if current_time - last_window_switch > window_cooldown:
                            if delta_x > win_threshold:
                                print("Змах вправо -> Наступне вікно (Alt+Esc)")
                                pyautogui.hotkey('alt', 'esc')
                                win_anchor_x = current_x
                                last_window_switch = current_time
                            elif delta_x < -win_threshold:
                                print("Змах вліво -> Попереднє вікно (Alt+Shift+Esc)")
                                pyautogui.hotkey('alt', 'shift', 'esc')
                                win_anchor_x = current_x
                                last_window_switch = current_time
                else:
                    win_active = False

                if not index_up and not middle_up and not ring_up and not pinky_up:
                    if not fist_active:
                        fist_start_time = current_time
                        fist_active = True
                        fist_anchor_y = current_wrist_y
                    else:
                        if abs(current_wrist_y - fist_anchor_y) > 0.07:
                            fist_start_time = current_time
                            fist_anchor_y = current_wrist_y
                        
                        if current_time - fist_start_time > 1.0 and (current_time - last_mute_time > global_cooldown):
                            print("Нерухомий кулак -> Mute/Unmute")
                            pyautogui.press('volumemute')
                            last_mute_time = current_time
                            fist_active = False 
                else:
                    fist_active = False

        else:
            vol_active = False
            win_active = False
            fist_active = False
            peace_active = False
            three_active = False

        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(5) & 0xFF == 27:  # ESC для виходу
            break

cap.release()
cv2.destroyAllWindows()