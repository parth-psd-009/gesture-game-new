import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras.models import load_model


def start_camera_and_detect():

    print("Starting camera....")
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    model = load_model('mp_hand_gesture')

    # with open('gesture.names', 'r') as f:
    #     classNames = f.read().split('\n')

    # # Remove any empty strings from classNames
    # classNames = [name for name in classNames if name]

    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()

        x, y, c = frame.shape

        frame = cv2.flip(frame, 1)
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(framergb)

        if result.multi_hand_landmarks:
            for handslms in result.multi_hand_landmarks:
                landmarks = []
                for lm in handslms.landmark:
                    lmx = int(lm.x * x)
                    lmy = int(lm.y * y)
                    landmarks.append([lmx, lmy])

                # Drawing landmarks on frames
                mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

                # Extracting relevant landmarks for thumbs up and thumbs down
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]

                # Calculate the distance between thumb tip and index finger tip
                distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)

                # Predict gesture
                prediction = model.predict([landmarks])
                classID = np.argmax(prediction)

                if classID == 0 and distance > 50:  
                    className = "Thumbs Up"
                elif classID == 1 and distance < 30:  
                    className = "Thumbs Down"
                else:
                    className = "Unknown"

                hand_side = "Left" if landmarks[0][0] < x / 2 else "Right"

                text_position = (10, 50) if hand_side == "Right" else (x - 150, 50)

                cv2.putText(frame, f"{hand_side} Hand: {className}", text_position,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)

        cv2.imshow("Output", frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
