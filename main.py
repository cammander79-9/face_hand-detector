
# import cv2
# import time

# def main():
#     face_detector = cv2.CascadeClassifier(
#         cv2.data.haarcascades
#         + "haarcascade_frontalface_default.xml"
#     )

#     if face_detector.empty():
#         raise RuntimeError("Face detector failed to load!")

#     camera = cv2.VideoCapture(0)

#     if not camera.isOpened():
#         raise RuntimeError("Cannot open webcam!")

#     previous_time = time.perf_counter()

#     try:
#         print("Cyber Girl face detector online!")

#         while True:
#             success, frame = camera.read()

#             if not success:
#                 print("Failed to read webcam frame.")
#                 break

#             frame = cv2.flip(frame, 1)
#             gray = cv2.cvtColor(
#                 frame, cv2.COLOR_BGR2GRAY
#             )

#             faces = face_detector.detectMultiScale(
#                 gray,
#                 scaleFactor=1.1,
#                 minNeighbors=5,
#                 minSize=(30, 30)
#             )

#             for x, y, width, height in faces:
#                 cv2.rectangle(
#                     frame,
#                     (x, y),
#                     (x + width, y + height),
#                     (0, 255, 0),
#                     2
#                 )

#                 cv2.putText(
#                     frame,
#                     "Face Detected",
#                     (x, max(25, y - 10)),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.6,
#                     (0, 255, 0),
#                     2
#                 )

#             current_time = time.perf_counter()
#             elapsed = current_time - previous_time
#             fps = 1 / elapsed if elapsed > 0 else 0
#             previous_time = current_time

#             cv2.putText(
#                 frame,
#                 f"FPS: {fps:.1f}",
#                 (15, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (255, 255, 255),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 f"Faces: {len(faces)}",
#                 (15, 60),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 255, 0),
#                 2
#             )

#             cv2.imshow("Cyber Girl | Face Detector", frame)

#             key = cv2.waitKey(1) & 0xFF

#             if key == ord("q") or key == 27:
#                 break

#     finally:
#         camera.release()
#         cv2.destroyAllWindows()
#         print("Face detector stopped.")


# if __name__ == "__main__":
#     main()


# import cv2
# import time
# import mediapipe as mp
# from pathlib import Path

# from hand_traking import draw_hand, MAX_HANDS
# from voice_engine import VoiceEngine

# # ============== CONFIGURATION ==============

# BASE_DIR = Path(__file__).resolve().parent
# FACE_MODEL = BASE_DIR / "face_landmarker.task"
# HAND_MODEL = BASE_DIR / "hand_landmarker.task"

# CAMERA_ID = 0

# BaseOptions = mp.tasks.BaseOptions
# RunningMode = mp.tasks.vision.RunningMode

# FaceLandmarker = mp.tasks.vision.FaceLandmarker
# HandLandmarker = mp.tasks.vision.HandLandmarker


# def main():
#     # Verify both model files.
#     for model in (FACE_MODEL, HAND_MODEL):
#         if not model.is_file():
#             raise FileNotFoundError(f"Model not found: {model}")

#     face_options = mp.tasks.vision.FaceLandmarkerOptions(
#         base_options=BaseOptions(
#             model_asset_path=str(FACE_MODEL)
#         ),
#         running_mode=RunningMode.VIDEO,
#         num_faces=5,
#     )

#     hand_options = mp.tasks.vision.HandLandmarkerOptions(
#         base_options=BaseOptions(
#             model_asset_path=str(HAND_MODEL)
#         ),
#         running_mode=RunningMode.VIDEO,
#         num_hands=MAX_HANDS,
#         min_hand_detection_confidence=0.6,
#         min_hand_presence_confidence=0.6,
#         min_tracking_confidence=0.6,
#     )

#     face_engine = None
#     hand_engine = None
#     camera = None

#     try:
#         # Start both models.
#         face_engine = FaceLandmarker.create_from_options(
#             face_options
#         )
#         hand_engine = HandLandmarker.create_from_options(
#             hand_options
#         )

#         # Open the webcam only once.
#         camera = cv2.VideoCapture(CAMERA_ID)

#         if not camera.isOpened():
#             raise RuntimeError("Cannot open webcam!")

#         camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#         camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

#         print("Cyber Girl Main System: ONLINE")
#         print("Face Engine: ONLINE")
#         print("Hand Engine: ONLINE")
#         print("Press Q or ESC to exit.")

#         start_time = time.perf_counter()
#         previous_time = start_time
#         last_timestamp_ms = -1
#         fps = 0.0

#         while True:
#             success, frame = camera.read()

#             if not success:
#                 print("Failed to read webcam frame.")
#                 break

#             frame = cv2.flip(frame, 1)

#             # Convert this frame once for both engines.
#             rgb_frame = cv2.cvtColor(
#                 frame, cv2.COLOR_BGR2RGB
#             )

#             image = mp.Image(
#                 image_format=mp.ImageFormat.SRGB,
#                 data=rgb_frame,
#             )

#             timestamp_ms = max(
#                 int((time.perf_counter() - start_time) * 1000),
#                 last_timestamp_ms + 1,
#             )
#             last_timestamp_ms = timestamp_ms

#             # Run face and hand detection on the same frame.
#             face_result = face_engine.detect_for_video(
#                 image, timestamp_ms
#             )
#             hand_result = hand_engine.detect_for_video(
#                 image, timestamp_ms
#             )

#             # Calculate smoothed FPS.
#             current_time = time.perf_counter()
#             delta = current_time - previous_time
#             previous_time = current_time

#             if delta > 0:
#                 instant_fps = 1.0 / delta
#                 fps = (
#                     instant_fps if fps == 0
#                     else 0.9 * fps + 0.1 * instant_fps
#                 )

#             # Draw face landmarks.
#             height, width = frame.shape[:2]

#             for face in face_result.face_landmarks:
#                 for point in face[::2]:
#                     x = int(point.x * width)
#                     y = int(point.y * height)

#                     cv2.circle(
#                         frame, (x, y), 1,
#                         (0, 255, 0), -1
#                     )

#             # Draw hand skeletons and gesture information.
#             if hand_result.hand_landmarks:
#                 for index, landmarks in enumerate(
#                     hand_result.hand_landmarks
#                 ):
#                     handedness = "Hand"

#                     if (
#                         hand_result.handedness
#                         and index < len(hand_result.handedness)
#                         and hand_result.handedness[index]
#                     ):
#                         handedness = (
#                             hand_result.handedness[index][0].category_name
#                         )

#                     draw_hand(
#                         frame, landmarks, handedness, fps
#                     )

#             # Display combined system status.
#             cv2.putText(
#                 frame,
#                 f"FPS: {fps:.1f}",
#                 (15, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7, (255, 255, 255), 2,
#             )

#             cv2.putText(
#                 frame,
#                 f"Faces: {len(face_result.face_landmarks)}",
#                 (15, 60),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7, (0, 255, 0), 2,
#             )

#             cv2.putText(
#                 frame,
#                 f"Hands: {len(hand_result.hand_landmarks)}",
#                 (15, 90),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7, (255, 180, 0), 2,
#             )

#             cv2.imshow("Cyber Girl | Main System", frame)

#             key = cv2.waitKey(1) & 0xFF

#             if key in (ord("q"), 27):
#                 break

#     finally:
#         if camera is not None:
#             camera.release()

#         if hand_engine is not None:
#             hand_engine.close()

#         if face_engine is not None:
#             face_engine.close()

#         cv2.destroyAllWindows()
#         print("Cyber Girl Main System: STOPPED")


# if __name__ == "__main__":
#     main()

import cv2
import time
import mediapipe as mp
from pathlib import Path

from hand_traking import draw_hand, MAX_HANDS
from voice_engine import VoiceEngine

# ============== CONFIGURATION ==============

BASE_DIR = Path(__file__).resolve().parent
FACE_MODEL = BASE_DIR / "face_landmarker.task"
HAND_MODEL = BASE_DIR / "hand_landmarker.task"

CAMERA_ID = 0

BaseOptions = mp.tasks.BaseOptions
RunningMode = mp.tasks.vision.RunningMode

FaceLandmarker = mp.tasks.vision.FaceLandmarker
HandLandmarker = mp.tasks.vision.HandLandmarker


def main():
    for model in (FACE_MODEL, HAND_MODEL):
        if not model.is_file():
            raise FileNotFoundError(f"Model not found: {model}")

    face_options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(FACE_MODEL)),
        running_mode=RunningMode.VIDEO,
        num_faces=5,
    )

    hand_options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(HAND_MODEL)),
        running_mode=RunningMode.VIDEO,
        num_hands=MAX_HANDS,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    face_engine = None
    hand_engine = None
    voice = None
    camera = None

    try:
        print("Initializing Cyber Girl engines...")

        face_engine = FaceLandmarker.create_from_options(face_options)
        hand_engine = HandLandmarker.create_from_options(hand_options)
        voice = VoiceEngine()

        camera = cv2.VideoCapture(CAMERA_ID)

        if not camera.isOpened():
            raise RuntimeError("Cannot open webcam!")

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("Cyber Girl Main System: ONLINE")
        print("Face Engine: ONLINE")
        print("Hand Engine: ONLINE")
        print("Voice Engine: ONLINE")
        print("V: speak | 1/2: change voice | S: status | Q/ESC: exit")

        # Voice starts in its worker thread; webcam processing remains here.
        # Note: speak() currently waits for playback to finish.
        voice.speak("Cyber Girl main system online.")

        start_time = time.perf_counter()
        previous_time = start_time
        last_timestamp_ms = -1
        fps = 0.0

        while True:
            success, frame = camera.read()

            if not success:
                print("Failed to read webcam frame.")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame,
            )

            timestamp_ms = max(
                int((time.perf_counter() - start_time) * 1000),
                last_timestamp_ms + 1,
            )
            last_timestamp_ms = timestamp_ms

            face_result = face_engine.detect_for_video(image, timestamp_ms)
            hand_result = hand_engine.detect_for_video(image, timestamp_ms)

            current_time = time.perf_counter()
            delta = current_time - previous_time
            previous_time = current_time

            if delta > 0:
                instant_fps = 1.0 / delta
                fps = instant_fps if fps == 0 else 0.9 * fps + 0.1 * instant_fps

            height, width = frame.shape[:2]

            for face in face_result.face_landmarks:
                for point in face[::2]:
                    x = int(point.x * width)
                    y = int(point.y * height)
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            for index, landmarks in enumerate(hand_result.hand_landmarks):
                handedness = "Hand"

                if (
                    hand_result.handedness
                    and index < len(hand_result.handedness)
                    and hand_result.handedness[index]
                ):
                    handedness = hand_result.handedness[index][0].category_name

                draw_hand(frame, landmarks, handedness, fps)

            cv2.putText(
                frame, f"FPS: {fps:.1f}", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
            cv2.putText(
                frame, f"Faces: {len(face_result.face_landmarks)}", (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )
            cv2.putText(
                frame, f"Hands: {len(hand_result.hand_landmarks)}", (15, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 180, 0), 2
            )

            cv2.imshow("Cyber Girl | Main System", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("v"):
                voice.speak("Cyber Girl voice system online.")

            elif key in (ord("1"), ord("2")):
                voice_index = key - ord("1")
                available = voice.available_voices()

                if voice_index < len(available):
                    voice.set_voice(voice_index)
                    print(f"Selected voice: {available[voice_index]['name']}")
                else:
                    print(f"Voice {voice_index} is not available.")

            elif key == ord("s"):
                print(voice.status())

            elif key in (ord("q"), 27):
                break

    finally:
        if camera is not None:
            camera.release()

        if hand_engine is not None:
            hand_engine.close()

        if face_engine is not None:
            face_engine.close()

        if voice is not None:
            voice.close()

        cv2.destroyAllWindows()
        print("Cyber Girl Main System: STOPPED")


if __name__ == "__main__":
    main()
