import cv2
import numpy as np
import time
import mediapipe as mp

def find_red_puck_live(frame):
    prev_puck_center = None
    prev_time = time.time()
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 175, 50])
    upper_red = np.array([10, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 175, 50])
    upper_red = np.array([180, 255, 255])

    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 40:
            # Fit a circle around the contour
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            if radius > 10:  # Ensure the detected circle has a reasonable radius
                # Draw the circular boundary around the red puck
                cv2.circle(frame, center, radius, (0, 255, 0), 2)

                # Draw the center of the red puck
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

                # Compute the center of the circular boundary
                puck_center = center

                current_time = time.time()
                time_difference = current_time - prev_time

                if prev_puck_center is not None:
                    puck_velocity = (0, 0)

                    # Check if the time difference is not zero to avoid division by zero
                    if time_difference != 0:
                        puck_velocity = (
                            int((puck_center[0] - prev_puck_center[0]) / time_difference),
                            int((puck_center[1] - prev_puck_center[1]) / time_difference)
                        )

                    cv2.arrowedLine(frame, prev_puck_center, puck_center, (0, 0, 255), 2)

                    text = f"Position: {puck_center}, Velocity: {puck_velocity}"
                    print(text)
                    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                prev_puck_center = puck_center
                prev_time = current_time

    cv2.imshow('Red Puck Detection', frame)


def hand_detection_func(frame):
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(
        min_detection_confidence=0.5, min_tracking_confidence=0.5)

    frame = cv2.flip(frame, 1)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    handedness_labels = []
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            handedness_label = handedness.classification[0].label
            handedness_labels.append(handedness_label)

            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            selected_landmarks = [hand_landmarks.landmark[i] for i in [0, 5, 9, 13, 17]]
            x_coords = [int(lmk.x * frame.shape[1]) for lmk in selected_landmarks]
            y_coords = [int(lmk.y * frame.shape[0]) for lmk in selected_landmarks]

            centroid_x = sum(x_coords) // len(x_coords)
            centroid_y = sum(y_coords) // len(y_coords)

            print(f"Centroid: ({centroid_x}, {centroid_y})")

            cv2.circle(frame, (centroid_x, centroid_y), 5, (0, 255, 0), -1)

            min_x, min_y, max_x, max_y = min(x_coords), min(y_coords), max(x_coords), max(y_coords)

            cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 0, 0), 2)

            cv2.putText(frame, handedness_label, (min_x, min_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    if len(set(handedness_labels)) == 1:
        cv2.putText(frame, handedness_labels[0], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    cv2.imshow('ERC ASSIGNMENT-3', frame)


# Main code
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        print("Empty camera frame encountered, ignoring!.")
        continue

    hand_detection_func(frame)
    find_red_puck_live(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()