"""
GestureCanvas - Main Application
Interactive Air Canvas with Hand Tracking, OpenCV, and MediaPipe.
Replicates the exact UI and features from @stylegwn.css TikTok video.
"""

import os
import sys
import time
import math
import colorsys
import numpy as np
import cv2

from hand_tracker import HandTracker
from canvas import VirtualCanvas


# ---------------- UI CONFIGURATION & PALETTE ----------------
PALETTE_COLORS = [
    # Row 1: Gold / Orange
    (30, 200, 255), (0, 140, 255),
    # Row 2: Crimson Red / Hot Pink
    (30, 30, 240), (180, 50, 255),
    # Row 3: Purple / Deep Violet
    (200, 30, 180), (180, 30, 90),
    # Row 4: Sky Blue / Teal
    (255, 200, 30), (180, 180, 0),
    # Row 5: Yellow / Lime Green
    (30, 240, 240), (50, 255, 100),
    # Row 6: Emerald Green / Dark Olive
    (50, 180, 50), (20, 80, 20),
    # Row 7: Pure White / Silver
    (250, 250, 250), (180, 180, 180),
    # Row 8: Slate Gray / Dark Charcoal
    (80, 80, 80), (20, 20, 20),
]


class GestureCanvasApp:
    def __init__(self, camera_id=0):
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Check if camera opened; fallback gracefully
        self.camera_available = self.cap.isOpened()
        if not self.camera_available:
            print("[GestureCanvas] Camera not detected. Running in canvas simulation mode.")

        # Window & Canvas setup
        self.window_name = "GestureCanvas"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        # Modules
        self.tracker = HandTracker(max_hands=2, detection_con=0.6, tracking_con=0.6)
        self.canvas = VirtualCanvas(width=1280, height=720)

        # App state
        self.mode = "DRAW"   # Modes: 'DRAW', 'ERASE', 'MOVE'
        self.eraser_radius = 28
        self.selected_color_idx = 2  # Default: Crimson Red

        # UI Dimensions
        self.panel_left_w = 95
        self.panel_right_w = 95
        self.slider_y_top = 0
        self.slider_y_bot = 0
        self.slider_x_left = 0
        self.slider_x_right = 0
        self.slider_thumb_val = 0.0  # [0.0 - 1.0]

        # Buttons state & layout
        self.buttons = {}
        self.palette_rects = []

        # Gesture interaction smoothing & dwell
        self.dwell_btn = None
        self.dwell_start_time = 0.0
        self.dwell_threshold = 0.45  # Seconds of hover with 2 fingers to trigger click
        self.last_pinch_time = 0.0

        # Notifications
        self.notification_msg = ""
        self.notification_expiry = 0.0

        # FPS calculation
        self.prev_time = time.time()
        self.fps = 30.0

        # Mouse interaction support
        self.mouse_pressed = False
        self.mouse_pt = (0, 0)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)

    def _mouse_callback(self, event, x, y, flags, param):
        """Allows mouse testing and fallback input."""
        self.mouse_pt = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_pressed = True
            # Check UI clicks
            if not self._check_ui_click(x, y):
                if self.mode == "DRAW":
                    self.canvas.start_stroke(x, y)
                elif self.mode == "ERASE":
                    self.canvas.erase(x, y, self.eraser_radius)
                elif self.mode == "MOVE":
                    self.canvas.start_move(x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mouse_pressed:
                if self._is_in_slider(x, y):
                    self._update_slider(y)
                elif self.mode == "DRAW":
                    self.canvas.continue_stroke(x, y)
                elif self.mode == "ERASE":
                    self.canvas.erase(x, y, self.eraser_radius)
                elif self.mode == "MOVE":
                    self.canvas.continue_move(x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.mouse_pressed = False
            if self.mode == "DRAW":
                self.canvas.end_stroke()
            elif self.mode == "MOVE":
                self.canvas.end_move()

    def _notify(self, msg, duration=2.5):
        self.notification_msg = msg
        self.notification_expiry = time.time() + duration

    def _check_ui_click(self, x, y):
        """Checks if (x, y) clicked on any color, slider, or button."""
        # Check Color Palette
        for idx, (cx, cy, r) in enumerate(self.palette_rects):
            if math.hypot(x - cx, y - cy) <= r + 4:
                self.selected_color_idx = idx
                self.canvas.set_color(PALETTE_COLORS[idx])
                self._notify(f"Color: #{idx + 1}", 1.0)
                return True

        # Check Rainbow Slider
        if self._is_in_slider(x, y):
            self._update_slider(y)
            return True

        # Check Right Panel Buttons
        for name, rect in self.buttons.items():
            bx, by, bw, bh = rect
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self._trigger_action(name)
                return True

        return False

    def _is_in_slider(self, x, y):
        return (self.slider_x_left - 8 <= x <= self.slider_x_right + 8 and
                self.slider_y_top - 5 <= y <= self.slider_y_bot + 5)

    def _update_slider(self, y):
        clamped_y = max(self.slider_y_top, min(self.slider_y_bot, y))
        span = max(1, self.slider_y_bot - self.slider_y_top)
        self.slider_thumb_val = (clamped_y - self.slider_y_top) / span
        # Convert hue to BGR
        r, g, b = colorsys.hsv_to_rgb(self.slider_thumb_val, 1.0, 1.0)
        custom_bgr = (int(b * 255), int(g * 255), int(r * 255))
        self.selected_color_idx = -1  # Custom hue selected
        self.canvas.set_color(custom_bgr)

    def _trigger_action(self, action_name):
        """Executes action for specified button."""
        if action_name == "DRW":
            self.mode = "DRAW"
            self._notify("Mode: DRAW", 1.2)
        elif action_name == "ERS":
            self.mode = "ERASE"
            self._notify("Mode: ERASE", 1.2)
        elif action_name == "MOV":
            self.mode = "MOVE"
            self._notify("Mode: MOVE (Pinch to drag)", 1.5)
        elif action_name == "-":
            new_size = max(2, self.canvas.brush_thickness - 2)
            self.canvas.set_thickness(new_size)
            self._notify(f"Brush Size: {new_size}px", 1.0)
        elif action_name == "+":
            new_size = min(40, self.canvas.brush_thickness + 2)
            self.canvas.set_thickness(new_size)
            self._notify(f"Brush Size: {new_size}px", 1.0)
        elif action_name == "GLOW":
            st = self.canvas.toggle_glow()
            self._notify(f"Neon Glow: {'ON' if st else 'OFF'}", 1.2)
        elif action_name == "MRR":
            st = self.canvas.toggle_mirror()
            self._notify(f"Mirror Symmetry: {'ON' if st else 'OFF'}", 1.2)
        elif action_name == "FLL":
            st = self.canvas.toggle_fill()
            self._notify(f"Dark Canvas: {'ON' if st else 'OFF'}", 1.2)
        elif action_name == "RNBW":
            st = self.canvas.toggle_rainbow()
            self._notify(f"Rainbow Brush: {'ON' if st else 'OFF'}", 1.2)
        elif action_name == "UNDO":
            if self.canvas.undo():
                self._notify(f"Undo (Remaining: {self.canvas.undo_count})", 1.0)
            else:
                self._notify("Nothing to Undo", 1.0)
        elif action_name == "CLEAR":
            self.canvas.clear()
            self._notify("Canvas Cleared!", 1.2)
        elif action_name == "SAVE":
            # Pass placeholder, will be saved during render
            self._pending_save = True

    def _render_ui(self, frame):
        """Renders Left & Right Toolbars matching the video's exact design."""
        h, w, c = frame.shape
        overlay = frame.copy()

        # 1. Left Panel Background
        lw = self.panel_left_w
        cv2.rectangle(overlay, (0, 0), (lw, h), (14, 16, 22), -1)

        # 2. Right Panel Background
        rw = self.panel_right_w
        cv2.rectangle(overlay, (w - rw, 0), (w, h), (14, 16, 22), -1)

        # Apply transparency to panels
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

        # --- LEFT PANEL: PALETTE & SLIDER ---
        # Top title: "COLOR"
        cv2.putText(frame, "COLOR", (22, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 180, 255), 1, cv2.LINE_AA)

        self.palette_rects = []
        start_y = 52
        gap_y = 30
        col_x = [lw // 3 - 3, (lw * 2) // 3 + 3]

        for i, color in enumerate(PALETTE_COLORS):
            row = i // 2
            col = i % 2
            cx = col_x[col]
            cy = start_y + row * gap_y
            r = 11

            self.palette_rects.append((cx, cy, r))

            # Filled color circle
            cv2.circle(frame, (cx, cy), r, color, -1, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), r, (50, 50, 60), 1, cv2.LINE_AA)

            # Selection ring if active
            if i == self.selected_color_idx and not self.canvas.rainbow_mode:
                cv2.circle(frame, (cx, cy), r + 4, (255, 255, 255), 2, cv2.LINE_AA)

        # Vertical Rainbow Slider
        last_color_y = start_y + 8 * gap_y
        self.slider_y_top = last_color_y + 12
        self.slider_y_bot = self.slider_y_top + 130
        self.slider_x_left = 18
        self.slider_x_right = lw - 18

        slider_h = self.slider_y_bot - self.slider_y_top
        slider_w = self.slider_x_right - self.slider_x_left

        # Render rainbow spectrum bar
        for sy in range(slider_h):
            hue = sy / max(1, slider_h)
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            bar_color = (int(b * 255), int(g * 255), int(r * 255))
            y_pos = self.slider_y_top + sy
            cv2.line(frame, (self.slider_x_left, y_pos), (self.slider_x_right, y_pos), bar_color, 1)

        cv2.rectangle(frame, (self.slider_x_left, self.slider_y_top),
                      (self.slider_x_right, self.slider_y_bot), (100, 100, 110), 1, cv2.LINE_AA)

        # Slider Thumb
        thumb_y = int(self.slider_y_top + self.slider_thumb_val * slider_h)
        cv2.rectangle(frame, (self.slider_x_left - 3, thumb_y - 2),
                      (self.slider_x_right + 3, thumb_y + 2), (255, 255, 255), -1, cv2.LINE_AA)

        # Active Color Preview Circle (Bottom Left)
        preview_y = self.slider_y_bot + 32
        if preview_y + 20 < h:
            cv2.circle(frame, (lw // 2, preview_y), 15, self.canvas.current_color, -1, cv2.LINE_AA)
            cv2.circle(frame, (lw // 2, preview_y), 16, (255, 255, 255), 2, cv2.LINE_AA)

        # --- RIGHT PANEL: BUTTONS & TOOLS ---
        self.buttons = {}
        rx = w - rw + 8
        bw = rw - 16
        by = 14
        bh = 32
        space_y = 6

        # Button list matching the video
        btn_defs = [
            ("DRW", "DRW", self.mode == "DRAW", (30, 220, 255)),
            ("ERS", "ERS", self.mode == "ERASE", (40, 40, 255)),
            ("MOV", "MOV", self.mode == "MOVE", (0, 255, 120)),
            ("-", "-", False, (220, 220, 220)),
            ("DOT", "", False, (220, 220, 220)),  # Size preview indicator
            ("+", "+", False, (220, 220, 220)),
            ("GLOW", "GLOW", self.canvas.glow_mode, (255, 255, 50)),
            ("MRR", "MRR", self.canvas.mirror_mode, (255, 100, 220)),
            ("FLL", "FLL", self.canvas.fill_mode, (100, 255, 255)),
            ("RNBW", "RNBW", self.canvas.rainbow_mode, (0, 220, 255)),
            ("UNDO", f"UNDO({self.canvas.undo_count})", False, (80, 100, 240)),
            ("CLEAR", "CLEAR", False, (50, 50, 255)),
            ("SAVE", "SAVE", False, (50, 230, 100)),
        ]

        for code, label, is_active, active_color in btn_defs:
            if code == "DOT":
                # Render size preview circle between - and +
                dot_y = by + 10
                cv2.circle(frame, (rx + bw // 2, dot_y), self.canvas.brush_thickness // 2 + 1,
                           self.canvas.current_color, -1, cv2.LINE_AA)
                by += 22
                continue

            btn_rect = (rx, by, bw, bh)
            self.buttons[code] = btn_rect

            # Button background & border
            border_col = active_color if is_active else (60, 65, 75)
            bg_col = (35, 42, 55) if is_active else (22, 26, 34)

            cv2.rectangle(frame, (rx, by), (rx + bw, by + bh), bg_col, -1)
            cv2.rectangle(frame, (rx, by), (rx + bw, by + bh), border_col, 2 if is_active else 1, cv2.LINE_AA)

            # Button text
            text_col = active_color if is_active else (210, 215, 225)
            font_scale = 0.38 if len(label) > 4 else 0.46
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
            tx = rx + (bw - tw) // 2
            ty = by + (bh + th) // 2
            cv2.putText(frame, label, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_col, 1, cv2.LINE_AA)

            by += bh + space_y

        # --- TOP HEADER: FPS & STATUS & NOTIFICATIONS ---
        # FPS counter
        cv2.putText(frame, f"FPS: {int(self.fps)}", (lw + 20, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 120), 1, cv2.LINE_AA)

        # Mode Badge (Top Center)
        mode_badge = f"[ {self.mode} MODE ]"
        (mw, mh), _ = cv2.getTextSize(mode_badge, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        mode_x = lw + (w - lw - rw - mw) // 2
        mode_color = (0, 255, 120) if self.mode == "MOVE" else ((50, 80, 255) if self.mode == "ERASE" else (255, 220, 0))
        cv2.putText(frame, mode_badge, (mode_x, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2, cv2.LINE_AA)

        # Temporary Notification Toast
        if time.time() < self.notification_expiry and self.notification_msg:
            msg = self.notification_msg
            (nw, nh), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            nx = lw + (w - lw - rw - nw) // 2
            ny = 68
            # Semi-transparent toast badge
            cv2.rectangle(frame, (nx - 16, ny - nh - 8), (nx + nw + 16, ny + 8), (20, 24, 30), -1)
            cv2.rectangle(frame, (nx - 16, ny - nh - 8), (nx + nw + 16, ny + 8), (0, 220, 150), 1, cv2.LINE_AA)
            cv2.putText(frame, msg, (nx, ny), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    def _handle_gesture(self, gesture, index_pt, thumb_pt, frame):
        """Processes hand positions to control UI, drawing, and dragging."""
        ix, iy = index_pt

        # Check if cursor is over Left or Right UI panels
        in_left_ui = (ix < self.panel_left_w)
        in_right_ui = (ix > frame.shape[1] - self.panel_right_w)
        in_ui = in_left_ui or in_right_ui

        # Hover ring on index tip
        cursor_color = (0, 255, 200) if in_ui else (self.canvas.current_color if self.mode == "DRAW" else (50, 50, 255))
        cv2.circle(frame, (ix, iy), 8, cursor_color, 2, cv2.LINE_AA)

        # 1. UI INTERACTION (HOVER & DWELL OR PINCH CLICK)
        if in_ui:
            # End any ongoing drawing stroke when entering UI
            self.canvas.end_stroke()

            hovered_btn = None
            # Check buttons in right panel
            for name, rect in self.buttons.items():
                bx, by, bw, bh = rect
                if bx <= ix <= bx + bw and by <= iy <= by + bh:
                    hovered_btn = name
                    break

            # Check color palette in left panel
            if not hovered_btn:
                for idx, (cx, cy, r) in enumerate(self.palette_rects):
                    if math.hypot(ix - cx, iy - cy) <= r + 8:
                        hovered_btn = f"COLOR_{idx}"
                        break

            # Check slider
            if not hovered_btn and self._is_in_slider(ix, iy):
                hovered_btn = "SLIDER"

            # Selection gesture (2 fingers) or Pinch triggers UI selection
            if hovered_btn:
                # Draw hover highlight
                cv2.circle(frame, (ix, iy), 14, (0, 255, 255), 2, cv2.LINE_AA)

                # Dwell timer
                if self.dwell_btn == hovered_btn:
                    elapsed = time.time() - self.dwell_start_time
                    progress = min(1.0, elapsed / self.dwell_threshold)
                    # Draw circular progress bar around cursor
                    angle = int(progress * 360)
                    cv2.ellipse(frame, (ix, iy), (18, 18), 0, 0, angle, (0, 255, 120), 3, cv2.LINE_AA)

                    if progress >= 1.0 or gesture == "PINCH":
                        self._handle_ui_selection(hovered_btn, iy)
                        self.dwell_btn = None
                        self.dwell_start_time = time.time() + 0.3  # Cooldown
                else:
                    self.dwell_btn = hovered_btn
                    self.dwell_start_time = time.time()
            else:
                self.dwell_btn = None
            return

        self.dwell_btn = None

        # 2. CANVAS INTERACTION (DRAW, ERASE, MOVE)
        if self.mode == "DRAW":
            if gesture == "DRAW":
                self.canvas.start_stroke(ix, iy)
                self.canvas.continue_stroke(ix, iy)
            else:
                self.canvas.end_stroke()

        elif self.mode == "ERASE":
            # Show eraser circle cursor
            cv2.circle(frame, (ix, iy), self.eraser_radius, (50, 50, 240), 2, cv2.LINE_AA)
            if gesture in ("DRAW", "SELECT", "PINCH"):
                self.canvas.erase(ix, iy, self.eraser_radius)

        elif self.mode == "MOVE":
            # Display crosshair pointer
            cv2.drawMarker(frame, (ix, iy), (0, 255, 120), cv2.MARKER_CROSS, 20, 2, cv2.LINE_AA)
            cv2.circle(frame, (ix, iy), 12, (0, 255, 120), 1, cv2.LINE_AA)

            # Pinch gesture grabs and drags
            if gesture == "PINCH":
                px, py = (ix + thumb_pt[0]) // 2, (iy + thumb_pt[1]) // 2
                cv2.circle(frame, (px, py), 10, (0, 255, 0), -1, cv2.LINE_AA)
                if self.canvas.selected_stroke is None:
                    self.canvas.start_move(px, py)
                else:
                    self.canvas.continue_move(px, py)
            else:
                self.canvas.end_move()

    def _handle_ui_selection(self, btn_code, y_pos):
        """Dispatches button or color selection."""
        if btn_code.startswith("COLOR_"):
            idx = int(btn_code.split("_")[1])
            self.selected_color_idx = idx
            self.canvas.set_color(PALETTE_COLORS[idx])
            self._notify(f"Color: #{idx + 1}", 1.0)
        elif btn_code == "SLIDER":
            self._update_slider(y_pos)
        else:
            self._trigger_action(btn_code)

    def run(self):
        """Main application loop."""
        print("\n==========================================")
        print("       GestureCanvas is Running!          ")
        print("==========================================")
        print("Hotkeys:")
        print("  D: Draw Mode         E: Erase Mode")
        print("  M: Move Mode         G: Toggle Neon Glow")
        print("  R: Rainbow Brush     X: Toggle Mirror")
        print("  F: Dark Blackboard   Z: Undo")
        print("  C: Clear Canvas      S: Save Screenshot")
        print("  +/-: Brush Size      Q: Quit")
        print("==========================================\n")

        self._pending_save = False

        while True:
            # Capture frame
            if self.camera_available:
                ret, frame = self.cap.read()
                if not ret:
                    # Video source loop or black frame
                    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                else:
                    # Mirror horizontal for natural webcam interaction
                    frame = cv2.flip(frame, 1)
            else:
                # Simulated interactive dark canvas when no camera is present
                frame = np.full((720, 1280, 3), (25, 28, 35), dtype=np.uint8)

            # Hand tracking
            frame = self.tracker.find_hands(frame, draw=True, cyber_style=True)
            lms = self.tracker.get_positions(hand_idx=0)

            # Process gestures if hand is present
            if len(lms) >= 21:
                gesture = self.tracker.detect_gesture(hand_idx=0)
                index_pt = (lms[8][0], lms[8][1])
                thumb_pt = (lms[4][0], lms[4][1])
                self._handle_gesture(gesture, index_pt, thumb_pt, frame)
            else:
                # If no hand, end ongoing stroke
                if not self.mouse_pressed:
                    self.canvas.end_stroke()
                    self.canvas.end_move()

            # Render canvas drawing strokes over frame
            frame = self.canvas.render(frame)

            # Save artwork before rendering UI if pending save requested
            if self._pending_save:
                saved_path = self.canvas.save_artwork(frame)
                self._notify(f"Saved: {os.path.basename(saved_path)}", 3.0)
                self._pending_save = False

            # Render UI overlays (Left and Right panels, HUD)
            self._render_ui(frame)

            # Calculate FPS
            curr_time = time.time()
            fps_calc = 1.0 / max(0.001, curr_time - self.prev_time)
            self.fps = 0.9 * self.fps + 0.1 * fps_calc
            self.prev_time = curr_time

            # Display window
            cv2.imshow(self.window_name, frame)

            # Keyboard shortcuts
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord('q'), ord('Q')):
                break
            elif key in (ord('d'), ord('D')):
                self.mode = "DRAW"
                self._notify("Mode: DRAW", 1.2)
            elif key in (ord('e'), ord('E')):
                self.mode = "ERASE"
                self._notify("Mode: ERASE", 1.2)
            elif key in (ord('m'), ord('M')):
                self.mode = "MOVE"
                self._notify("Mode: MOVE", 1.2)
            elif key in (ord('g'), ord('G')):
                st = self.canvas.toggle_glow()
                self._notify(f"Neon Glow: {'ON' if st else 'OFF'}", 1.2)
            elif key in (ord('r'), ord('R')):
                st = self.canvas.toggle_rainbow()
                self._notify(f"Rainbow Brush: {'ON' if st else 'OFF'}", 1.2)
            elif key in (ord('x'), ord('X')):
                st = self.canvas.toggle_mirror()
                self._notify(f"Mirror Symmetry: {'ON' if st else 'OFF'}", 1.2)
            elif key in (ord('f'), ord('F')):
                st = self.canvas.toggle_fill()
                self._notify(f"Dark Blackboard: {'ON' if st else 'OFF'}", 1.2)
            elif key in (ord('z'), ord('Z'), ord('u'), ord('U')):
                self.canvas.undo()
                self._notify(f"Undo (Remaining: {self.canvas.undo_count})", 1.0)
            elif key in (ord('c'), ord('C')):
                self.canvas.clear()
                self._notify("Canvas Cleared!", 1.2)
            elif key in (ord('s'), ord('S')):
                self._pending_save = True
            elif key in (ord('+'), ord('=')):
                self.canvas.set_thickness(self.canvas.brush_thickness + 2)
                self._notify(f"Brush Size: {self.canvas.brush_thickness}px", 1.0)
            elif key in (ord('-'), ord('_')):
                self.canvas.set_thickness(self.canvas.brush_thickness - 2)
                self._notify(f"Brush Size: {self.canvas.brush_thickness}px", 1.0)

        # Cleanup
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = GestureCanvasApp()
    app.run()
