
# import cv2
# import math
# import time
# import mediapipe as mp
# from pathlib import Path

# # ============== CONFIGURATION ==============

# BASE_DIR = Path(__file__).resolve().parent
# MODEL_PATH = BASE_DIR / "hand_landmarker.task"

# CAMERA_ID = 0
# MAX_HANDS = 2
# WINDOW_NAME = "Cyber Girl | Hand Tracking"

# # ============== MEDIAPIPE API ==============

# BaseOptions = mp.tasks.BaseOptions
# HandLandmarker = mp.tasks.vision.HandLandmarker
# HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
# RunningMode = mp.tasks.vision.RunningMode

# # Hand landmark indexes
# WRIST = 0
# THUMB_TIP = 4
# INDEX_TIP = 8

# FINGER_TIPS = [8, 12, 16, 20]
# FINGER_PIPS = [6, 10, 14, 18]


# # ============== MATH ENGINE ==============

# def distance(point_a, point_b):
#     """Calculate Euclidean distance between two 3D landmarks."""
#     dx = point_a.x - point_b.x
#     dy = point_a.y - point_b.y
#     dz = point_a.z - point_b.z

#     return math.sqrt(dx * dx + dy * dy + dz * dz)


# # ============== GESTURE ENGINE ==============

# def finger_states(landmarks):
#     """Estimate whether four fingers are extended."""
#     states = []

#     for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
#         states.append(landmarks[tip].y < landmarks[pip].y)

#     return states


# def detect_gestures(landmarks):
#     """Return basic finger-count and pinch information."""
#     states = finger_states(landmarks)
#     pinch_distance = distance(
#         landmarks[THUMB_TIP],
#         landmarks[INDEX_TIP]
#     )

#     return {
#         "finger_count": sum(states),
#         "pinch": pinch_distance < 0.06,
#         "distance": pinch_distance,
#     }


# # ============== DRAWING ENGINE ==============

# def draw_hand(frame, landmarks, handedness, fps):
#     height, width = frame.shape[:2]

#     # Normalized coordinates -> pixel coordinates
#     points = [
#         (
#             max(0, min(width - 1, int(point.x * width))),
#             max(0, min(height - 1, int(point.y * height)))
#         )
#         for point in landmarks
#     ]

#     # Draw skeleton
#     for start, end in HandLandmarker.HAND_CONNECTIONS:
#         cv2.line(
#             frame,
#             points[start],
#             points[end],
#             (80, 255, 120),
#             2,
#             cv2.LINE_AA
#         )

#     # Draw landmarks
#     for x, y in points:
#         cv2.circle(frame, (x, y), 4, (255, 180, 0), -1)

#     # Highlight index fingertip
#     index_x, index_y = points[INDEX_TIP]
#     cv2.circle(
#         frame,
#         (index_x, index_y),
#         10,
#         (0, 255, 255),
#         2
#     )

#     # Calculate gesture
#     gesture = detect_gestures(landmarks)

#     label = (
#         f"{handedness} | Fingers: "
#         f"{gesture['finger_count']}"
#     )

#     cv2.putText(
#         frame,
#         label,
#         (max(10, points[WRIST][0] - 60),
#          max(25, points[WRIST][1] + 30)),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.6,
#         (0, 255, 100),
#         2,
#         cv2.LINE_AA
#     )

#     pinch_text = "PINCH: YES" if gesture["pinch"] else "PINCH: NO"

#     cv2.putText(
#         frame,
#         pinch_text,
#         (15, 90),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.65,
#         (0, 255, 255),
#         2,
#         cv2.LINE_AA
#     )

#     cv2.putText(
#         frame,
#         f"Pinch distance: {gesture['distance']:.3f}",
#         (15, 120),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.55,
#         (255, 255, 255),
#         1,
#         cv2.LINE_AA
#     )

#     cv2.putText(
#         frame,
#         f"FPS: {fps:.1f}",
#         (15, 30),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.7,
#         (255, 255, 255),
#         2,
#         cv2.LINE_AA
#     )


# # ============== MAIN TRACKING SYSTEM ==============

# def main():
#     print("Model path:", MODEL_PATH)
#     print("Model exists:", MODEL_PATH.is_file())

#     if not MODEL_PATH.is_file():
#         raise FileNotFoundError(
#             "Model file not found.\n"
#             f"Expected location: {MODEL_PATH}\n"
#             "Place hand_landmarker.task beside hand_traking.py."
#         )

#     options = HandLandmarkerOptions(
#         base_options=BaseOptions(
#             model_asset_path=str(MODEL_PATH)
#         ),
#         running_mode=RunningMode.VIDEO,
#         num_hands=MAX_HANDS,
#         min_hand_detection_confidence=0.6,
#         min_hand_presence_confidence=0.6,
#         min_tracking_confidence=0.6
#     )

#     detector = None
#     camera = None

#     try:
#         detector = HandLandmarker.create_from_options(options)

#         camera = cv2.VideoCapture(CAMERA_ID)

#         if not camera.isOpened():
#             raise RuntimeError(
#                 "Webcam unavailable. Check camera permissions or CAMERA_ID."
#             )

#         camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#         camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

#         print("Cyber Girl Hand Tracking: ONLINE")
#         print("Show your hands to the camera.")
#         print("Press Q or ESC to exit.")

#         start_time = time.perf_counter()
#         previous_time = start_time
#         last_timestamp_ms = -1
#         fps = 0.0
#         frame_count = 0

#         while True:
#             success, frame = camera.read()

#             if not success:
#                 print("Could not read webcam frame.")
#                 break

#             frame = cv2.flip(frame, 1)

#             # Convert BGR -> RGB
#             rgb_frame = cv2.cvtColor(
#                 frame,
#                 cv2.COLOR_BGR2RGB
#             )

#             mp_image = mp.Image(
#                 image_format=mp.ImageFormat.SRGB,
#                 data=rgb_frame
#             )

#             # MediaPipe VIDEO mode requires increasing timestamps
#             timestamp_ms = int(
#                 (time.perf_counter() - start_time) * 1000
#             )

#             timestamp_ms = max(
#                 timestamp_ms,
#                 last_timestamp_ms + 1
#             )
#             last_timestamp_ms = timestamp_ms

#             result = detector.detect_for_video(
#                 mp_image,
#                 timestamp_ms
#             )

#             # Smooth FPS calculation
#             current_time = time.perf_counter()
#             delta = current_time - previous_time
#             previous_time = current_time

#             if delta > 0:
#                 instant_fps = 1.0 / delta
#                 fps = (
#                     instant_fps if fps == 0
#                     else 0.9 * fps + 0.1 * instant_fps
#                 )

#             frame_count += 1

#             if result.hand_landmarks:
#                 for index, landmarks in enumerate(
#                     result.hand_landmarks
#                 ):
#                     handedness = "Hand"

#                     if (
#                         result.handedness
#                         and index < len(result.handedness)
#                         and result.handedness[index]
#                     ):
#                         handedness = (
#                             result.handedness[index][0].category_name
#                         )

#                     draw_hand(
#                         frame,
#                         landmarks,
#                         handedness,
#                         fps
#                     )
#             else:
#                 cv2.putText(
#                     frame,
#                     "No hands detected",
#                     (15, 65),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7,
#                     (255, 255, 255),
#                     2
#                 )

#                 cv2.putText(
#                     frame,
#                     f"FPS: {fps:.1f}",
#                     (15, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7,
#                     (255, 255, 255),
#                     2
#                 )

#             cv2.imshow(WINDOW_NAME, frame)

#             key = cv2.waitKey(1) & 0xFF

#             if key in (ord("q"), 27):
#                 break

#     finally:
#         if camera is not None:
#             camera.release()

#         if detector is not None:
#             detector.close()

#         cv2.destroyAllWindows()
#         print("Hand tracking stopped safely.")


# if __name__ == "__main__":
#     main()

import cv2
import math
import time
import mediapipe as mp
from pathlib import Path

# ============== CONFIGURATION ==============

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "hand_landmarker.task"

CAMERA_ID = 0
MAX_HANDS = 2
WINDOW_NAME = "Cyber Girl | Hand Tracking"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# ============== MEDIAPIPE API ==============

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

# Standard MediaPipe hand skeleton connections.
# Each pair connects two landmark indexes.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8

FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]


# ============== MATH ENGINE ==============

def distance(point_a, point_b):
    """Euclidean distance between two normalized 3D landmarks."""
    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y
    dz = point_a.z - point_b.z

    return math.sqrt(dx * dx + dy * dy + dz * dz)


# ============== GESTURE ENGINE ==============

def finger_states(landmarks):
    """Estimate extension of the four non-thumb fingers."""
    return [
        landmarks[tip].y < landmarks[pip].y
        for tip, pip in zip(FINGER_TIPS, FINGER_PIPS)
    ]


def detect_gestures(landmarks):
    """Calculate finger count and thumb-index pinch."""
    states = finger_states(landmarks)

    pinch_distance = distance(
        landmarks[THUMB_TIP],
        landmarks[INDEX_TIP]
    )

    return {
        "finger_count": sum(states),
        "pinch": pinch_distance < 0.06,
        "distance": pinch_distance,
    }


# ============== DRAWING ENGINE ==============

def draw_hand(frame, landmarks, handedness, fps):
    height, width = frame.shape[:2]

    # Convert normalized landmark positions to pixels.
    points = [
        (
            max(0, min(width - 1, int(point.x * width))),
            max(0, min(height - 1, int(point.y * height)))
        )
        for point in landmarks
    ]

    # Draw skeleton.
    for start, end in HAND_CONNECTIONS:
        cv2.line(
            frame,
            points[start],
            points[end],
            (80, 255, 120),
            2,
            cv2.LINE_AA
        )

    # Draw landmarks.
    for x, y in points:
        cv2.circle(frame, (x, y), 4, (255, 180, 0), -1)

    # Highlight index fingertip.
    index_x, index_y = points[INDEX_TIP]
    cv2.circle(
        frame,
        (index_x, index_y),
        10,
        (0, 255, 255),
        2
    )

    gesture = detect_gestures(landmarks)

    label = (
        f"{handedness} | Fingers: "
        f"{gesture['finger_count']}"
    )

    wrist_x, wrist_y = points[WRIST]

    cv2.putText(
        frame,
        label,
        (max(10, wrist_x - 60), min(height - 10, wrist_y + 30)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 100),
        2,
        cv2.LINE_AA
    )

    pinch_text = "PINCH: YES" if gesture["pinch"] else "PINCH: NO"

    cv2.putText(
        frame,
        pinch_text,
        (15, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"Pinch distance: {gesture['distance']:.3f}",
        (15, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


# ============== MAIN TRACKING SYSTEM ==============

def main():
    print("Model path:", MODEL_PATH)
    print("Model exists:", MODEL_PATH.is_file())

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}\n"
            "Place hand_landmarker.task beside hand_traking.py."
        )

    options = HandLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=str(MODEL_PATH)
        ),
        running_mode=RunningMode.VIDEO,
        num_hands=MAX_HANDS,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6
    )

    detector = None
    camera = None

    try:
        # Initialize detector.
        detector = HandLandmarker.create_from_options(options)

        # Initialize webcam.
        camera = cv2.VideoCapture(CAMERA_ID)

        if not camera.isOpened():
            raise RuntimeError(
                "Webcam unavailable. Check permissions or CAMERA_ID."
            )

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        print("Cyber Girl Hand Tracking: ONLINE")
        print("Show your hands to the camera.")
        print("Press Q or ESC to exit.")

        start_time = time.perf_counter()
        previous_time = start_time
        last_timestamp_ms = -1
        fps = 0.0

        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read webcam frame.")
                break

            # Mirror the image for natural interaction.
            frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # VIDEO mode requires monotonically increasing timestamps.
            timestamp_ms = int(
                (time.perf_counter() - start_time) * 1000
            )
            timestamp_ms = max(
                timestamp_ms,
                last_timestamp_ms + 1
            )
            last_timestamp_ms = timestamp_ms

            result = detector.detect_for_video(
                mp_image,
                timestamp_ms
            )

            # Smooth FPS estimate.
            current_time = time.perf_counter()
            delta = current_time - previous_time
            previous_time = current_time

            if delta > 0:
                instant_fps = 1.0 / delta
                fps = (
                    instant_fps if fps == 0
                    else 0.9 * fps + 0.1 * instant_fps
                )

            if result.hand_landmarks:
                for index, landmarks in enumerate(result.hand_landmarks):
                    handedness = "Hand"

                    if (
                        result.handedness
                        and index < len(result.handedness)
                        and result.handedness[index]
                    ):
                        handedness = (
                            result.handedness[index][0].category_name
                        )

                    draw_hand(
                        frame,
                        landmarks,
                        handedness,
                        fps
                    )
            else:
                cv2.putText(
                    frame,
                    "No hands detected",
                    (15, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key in (ord("q"), 27):
                break

    finally:
        if camera is not None:
            camera.release()

        if detector is not None:
            detector.close()

        cv2.destroyAllWindows()
        print("Hand tracking stopped safely.")


if __name__ == "__main__":
    main()
