"""
Hand Tracker Module for GestureCanvas
Tracks hand landmarks using MediaPipe and detects user gestures.
Compatible with MediaPipe Tasks API (modern) & legacy mp.solutions.
"""

import os
import math
import urllib.request
import numpy as np
import cv2

# Model constants
MODEL_FILENAME = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


class HandTracker:
    def __init__(self, max_hands=2, detection_con=0.6, tracking_con=0.6):
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.tracking_con = tracking_con
        self.results = None
        self.lm_list = []  # List of hands, each containing 21 (x, y, z) landmarks
        self.handedness = []  # List of strings: 'Left' or 'Right'
        self.use_tasks_api = False

        # Prepare model path
        module_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(module_dir, MODEL_FILENAME)

        self._init_detector()

    def _init_detector(self):
        """Initializes detector using MediaPipe Tasks API or legacy mp.solutions"""
        # Try modern MediaPipe Tasks API first
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            import mediapipe as mp

            self._ensure_model_exists()
            base_options = python.BaseOptions(model_asset_path=self.model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=self.max_hands,
                min_hand_detection_confidence=self.detection_con,
                min_hand_presence_confidence=self.tracking_con,
                min_tracking_confidence=self.tracking_con,
            )
            self.detector = vision.HandLandmarker.create_from_options(options)
            self.mp_image_format = mp.ImageFormat.SRGB
            self.mp_Image = mp.Image
            self.use_tasks_api = True
            return
        except Exception as e:
            print(f"[HandTracker] Tasks API initialization failed: {e}")

        # Fallback to legacy mp.solutions.hands
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=self.max_hands,
                    min_detection_confidence=self.detection_con,
                    min_tracking_confidence=self.tracking_con,
                )
                self.use_tasks_api = False
                return
        except Exception as e:
            print(f"[HandTracker] Legacy solutions initialization failed: {e}")

        raise RuntimeError("Could not initialize MediaPipe HandLandmarker or mp.solutions.hands.")

    def _ensure_model_exists(self):
        """Downloads hand_landmarker.task if not present locally"""
        if not os.path.exists(self.model_path):
            print(f"[HandTracker] Downloading {MODEL_FILENAME}...")
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            urllib.request.urlretrieve(MODEL_URL, self.model_path)
            print(f"[HandTracker] Model downloaded to {self.model_path}")

    def find_hands(self, img, draw=True, cyber_style=True):
        """
        Processes frame to find hands and extracts landmarks.
        Returns the image with optional cyber-styled hand visualization.
        """
        h, w, c = img.shape
        self.lm_list = []
        self.handedness = []

        # OpenCV is BGR -> MediaPipe needs RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if self.use_tasks_api:
            mp_image = self.mp_Image(image_format=self.mp_image_format, data=img_rgb)
            self.results = self.detector.detect(mp_image)

            if self.results and self.results.hand_landmarks:
                for idx, hand_landmarks in enumerate(self.results.hand_landmarks):
                    curr_hand = []
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        curr_hand.append((cx, cy, lm.z))
                    self.lm_list.append(curr_hand)

                    label = "Right"
                    if self.results.handedness and len(self.results.handedness) > idx:
                        label = self.results.handedness[idx][0].category_name
                    self.handedness.append(label)
        else:
            self.results = self.hands.process(img_rgb)
            if self.results.multi_hand_landmarks:
                for idx, hand_lms in enumerate(self.results.multi_hand_landmarks):
                    curr_hand = []
                    for lm in hand_lms.landmark:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        curr_hand.append((cx, cy, lm.z))
                    self.lm_list.append(curr_hand)

                    label = "Right"
                    if self.results.multi_handedness and len(self.results.multi_handedness) > idx:
                        label = self.results.multi_handedness[idx].classification[0].label
                    self.handedness.append(label)

        if draw and self.lm_list:
            self._draw_cyber_skeleton(img, cyber_style)

        return img

    def _draw_cyber_skeleton(self, img, cyber_style=True):
        """
        Draws sleek cyber-aesthetic silver wireframe skeleton with glowing joints.
        Matches the look and feel from the video.
        """
        finger_chains = [
            [0, 1, 2, 3, 4],       # Thumb
            [0, 5, 6, 7, 8],       # Index
            [9, 10, 11, 12],      # Middle
            [13, 14, 15, 16],     # Ring
            [0, 17, 18, 19, 20],   # Pinky
        ]
        palm_chain = [5, 9, 13, 17]
        cyber_ties = [
            (2, 5), (5, 9), (9, 13), (13, 17),
            (6, 10), (10, 14), (14, 18),
            (7, 11), (11, 15), (15, 19)
        ]

        wire_color = (220, 220, 225)       # Silver / cool white
        cyber_color = (160, 160, 170)      # Translucent silver-gray
        joint_color = (255, 255, 255)      # Pure white
        glow_color = (0, 255, 170)         # Soft emerald glow for pointer

        for hand_lms in self.lm_list:
            if len(hand_lms) < 21:
                continue

            # 1. Draw cyber cross webbing if enabled
            if cyber_style:
                for p1, p2 in cyber_ties:
                    pt1 = (hand_lms[p1][0], hand_lms[p1][1])
                    pt2 = (hand_lms[p2][0], hand_lms[p2][1])
                    cv2.line(img, pt1, pt2, cyber_color, 1, cv2.LINE_AA)

            # 2. Draw standard finger bone lines
            for chain in finger_chains:
                for i in range(len(chain) - 1):
                    p1 = chain[i]
                    p2 = chain[i + 1]
                    pt1 = (hand_lms[p1][0], hand_lms[p1][1])
                    pt2 = (hand_lms[p2][0], hand_lms[p2][1])
                    cv2.line(img, pt1, pt2, wire_color, 1, cv2.LINE_AA)

            # Palm connection
            for i in range(len(palm_chain) - 1):
                p1 = palm_chain[i]
                p2 = palm_chain[i + 1]
                pt1 = (hand_lms[p1][0], hand_lms[p1][1])
                pt2 = (hand_lms[p2][0], hand_lms[p2][1])
                cv2.line(img, pt1, pt2, wire_color, 1, cv2.LINE_AA)

            # 3. Draw nodes / joints
            for idx, lm in enumerate(hand_lms):
                x, y = lm[0], lm[1]
                cv2.circle(img, (x, y), 2, joint_color, -1, cv2.LINE_AA)

            # 4. Highlight index fingertip (pointer cursor)
            idx_x, idx_y = hand_lms[8][0], hand_lms[8][1]
            cv2.circle(img, (idx_x, idx_y), 6, glow_color, 1, cv2.LINE_AA)
            cv2.circle(img, (idx_x, idx_y), 2, (255, 255, 255), -1, cv2.LINE_AA)

    def get_positions(self, hand_idx=0):
        """Returns the list of 21 landmark tuples (x, y, z) for specified hand."""
        if self.lm_list and len(self.lm_list) > hand_idx:
            return self.lm_list[hand_idx]
        return []

    def fingers_up(self, hand_idx=0):
        """
        Returns boolean list [Thumb, Index, Middle, Ring, Pinky]
        indicating which fingers are upright/extended.
        """
        lms = self.get_positions(hand_idx)
        if len(lms) < 21:
            return [False, False, False, False, False]

        fingers = []

        # Thumb: distance from thumb tip (4) to pinky MCP (17) vs thumb IP (3) to pinky MCP (17)
        dist_tip_pinky = math.hypot(lms[4][0] - lms[17][0], lms[4][1] - lms[17][1])
        dist_ip_pinky = math.hypot(lms[3][0] - lms[17][0], lms[3][1] - lms[17][1])
        fingers.append(dist_tip_pinky > dist_ip_pinky * 1.08)

        # 4 Fingers: Index (8), Middle (12), Ring (16), Pinky (20)
        tip_ids = [8, 12, 16, 20]
        pip_ids = [6, 10, 14, 18]

        for tip, pip in zip(tip_ids, pip_ids):
            fingers.append(lms[tip][1] < lms[pip][1])

        return fingers

    def get_distance(self, p1_idx, p2_idx, hand_idx=0):
        """Returns Euclidean pixel distance and mid-point between two landmarks."""
        lms = self.get_positions(hand_idx)
        if len(lms) < 21:
            return 9999, (0, 0)
        x1, y1 = lms[p1_idx][0], lms[p1_idx][1]
        x2, y2 = lms[p2_idx][0], lms[p2_idx][1]
        length = math.hypot(x2 - x1, y2 - y1)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        return length, (cx, cy)

    def detect_gesture(self, hand_idx=0):
        """
        Detects high-level gesture mode:
        - 'DRAW': Only index finger extended
        - 'SELECT': Index + Middle fingers extended (peace sign)
        - 'PINCH': Thumb tip & Index tip close (< 36 px)
        - 'PALM': All 5 fingers extended
        - 'FIST': All fingers curled
        - 'IDLE': Other combinations
        """
        fingers = self.fingers_up(hand_idx)
        pinch_dist, _ = self.get_distance(4, 8, hand_idx)

        if pinch_dist < 36:
            return "PINCH"

        if fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
            return "DRAW"

        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            return "SELECT"

        if all(fingers):
            return "PALM"

        if not any(fingers[1:]):
            return "FIST"

        return "IDLE"
