"""
Canvas Module for GestureCanvas
Manages drawing strokes, neon glow effects, rainbow brushes,
move/drag transformations, undo history, eraser, and layer rendering.
"""

import os
import math
import time
import colorsys
import numpy as np
import cv2


class Stroke:
    """Represents a continuous drawn line/brush stroke."""
    def __init__(self, color=(30, 30, 255), thickness=6, glow=False, rainbow=False, mirror=False):
        self.points = []          # List of (x, y) coordinates
        self.color = color        # Base BGR color tuple
        self.thickness = thickness
        self.glow = glow
        self.rainbow = rainbow
        self.mirror = mirror
        self.hues = []            # Hue values for rainbow brush [0.0 - 1.0]

    def add_point(self, x, y, hue=0.0):
        # Filter jitter: only add point if it moved at least 2 pixels
        if not self.points:
            self.points.append((x, y))
            if self.rainbow:
                self.hues.append(hue)
        else:
            lx, ly = self.points[-1]
            if math.hypot(x - lx, y - ly) >= 2:
                self.points.append((x, y))
                if self.rainbow:
                    self.hues.append(hue)

    def translate(self, dx, dy):
        """Translates all points in stroke by (dx, dy)."""
        self.points = [(x + dx, y + dy) for x, y in self.points]

    def distance_to_point(self, px, py):
        """Returns the minimum distance from (px, py) to any point in the stroke."""
        if not self.points:
            return 999999
        min_dist = 999999
        for x, y in self.points:
            d = math.hypot(px - x, py - y)
            if d < min_dist:
                min_dist = d
        return min_dist

    def get_bbox(self):
        """Returns bounding box (min_x, min_y, max_x, max_y)."""
        if not self.points:
            return None
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        pad = self.thickness + 5
        return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


class VirtualCanvas:
    """Manages full air canvas operations, history, and rendering."""
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

        # Stroke collections
        self.strokes = []
        self.current_stroke = None

        # Canvas settings
        self.current_color = (30, 30, 255)  # Default: Vibrant Red (BGR)
        self.brush_thickness = 6
        self.glow_mode = False
        self.rainbow_mode = False
        self.mirror_mode = False
        self.fill_mode = False              # True = dark blackboard, False = video pass-through

        # Dynamic rainbow hue state
        self.rainbow_hue = 0.0

        # Move/Transform interaction
        self.selected_stroke = None
        self.last_move_pt = None

        # Saved artwork directory
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved")
        os.makedirs(self.save_dir, exist_ok=True)

    def set_color(self, bgr_color):
        self.current_color = bgr_color
        self.rainbow_mode = False

    def set_thickness(self, thickness):
        self.brush_thickness = max(2, min(50, thickness))

    def toggle_glow(self):
        self.glow_mode = not self.glow_mode
        return self.glow_mode

    def toggle_mirror(self):
        self.mirror_mode = not self.mirror_mode
        return self.mirror_mode

    def toggle_fill(self):
        self.fill_mode = not self.fill_mode
        return self.fill_mode

    def toggle_rainbow(self):
        self.rainbow_mode = not self.rainbow_mode
        return self.rainbow_mode

    def start_stroke(self, x, y):
        """Begins recording a new stroke."""
        if self.current_stroke is None:
            self.current_stroke = Stroke(
                color=self.current_color,
                thickness=self.brush_thickness,
                glow=self.glow_mode,
                rainbow=self.rainbow_mode,
                mirror=self.mirror_mode
            )
            self.current_stroke.add_point(x, y, self.rainbow_hue)

    def continue_stroke(self, x, y):
        """Adds intermediate points to the active stroke."""
        if self.current_stroke is not None:
            if self.rainbow_mode:
                self.rainbow_hue = (self.rainbow_hue + 0.02) % 1.0
            self.current_stroke.add_point(x, y, self.rainbow_hue)

    def end_stroke(self):
        """Finalizes active stroke and pushes to history."""
        if self.current_stroke is not None:
            if len(self.current_stroke.points) >= 1:
                self.strokes.append(self.current_stroke)
            self.current_stroke = None

    def erase(self, x, y, radius=30):
        """Erases strokes near (x, y) within the specified radius."""
        new_strokes = []
        for stroke in self.strokes:
            # Check bounding box first
            bbox = stroke.get_bbox()
            if bbox is not None:
                bx1, by1, bx2, by2 = bbox
                if not (bx1 - radius <= x <= bx2 + radius and by1 - radius <= y <= by2 + radius):
                    new_strokes.append(stroke)
                    continue

            # Split or filter points outside erase radius
            segments = []
            curr_segment = []
            curr_hues = []

            for idx, pt in enumerate(stroke.points):
                if math.hypot(pt[0] - x, pt[1] - y) > radius:
                    curr_segment.append(pt)
                    if stroke.rainbow and idx < len(stroke.hues):
                        curr_hues.append(stroke.hues[idx])
                else:
                    if len(curr_segment) > 1:
                        st = Stroke(
                            color=stroke.color,
                            thickness=stroke.thickness,
                            glow=stroke.glow,
                            rainbow=stroke.rainbow,
                            mirror=stroke.mirror
                        )
                        st.points = curr_segment
                        st.hues = curr_hues
                        segments.append(st)
                    curr_segment = []
                    curr_hues = []

            if len(curr_segment) > 1:
                st = Stroke(
                    color=stroke.color,
                    thickness=stroke.thickness,
                    glow=stroke.glow,
                    rainbow=stroke.rainbow,
                    mirror=stroke.mirror
                )
                st.points = curr_segment
                st.hues = curr_hues
                segments.append(st)

            new_strokes.extend(segments)

        self.strokes = new_strokes

    def start_move(self, x, y, threshold=60):
        """Finds closest stroke near (x, y) to move/drag."""
        self.selected_stroke = None
        self.last_move_pt = (x, y)

        closest_stroke = None
        min_dist = threshold

        for stroke in reversed(self.strokes):
            d = stroke.distance_to_point(x, y)
            if d < min_dist:
                min_dist = d
                closest_stroke = stroke

        self.selected_stroke = closest_stroke
        return self.selected_stroke is not None

    def continue_move(self, x, y):
        """Drags the selected stroke or canvas by (dx, dy)."""
        if self.last_move_pt is not None:
            dx = x - self.last_move_pt[0]
            dy = y - self.last_move_pt[1]

            if self.selected_stroke is not None:
                self.selected_stroke.translate(dx, dy)
            else:
                # If no specific stroke was pinched, move all strokes!
                for s in self.strokes:
                    s.translate(dx, dy)

            self.last_move_pt = (x, y)

    def end_move(self):
        """Ends move/drag operation."""
        self.selected_stroke = None
        self.last_move_pt = None

    def undo(self):
        """Removes the last stroke."""
        if self.strokes:
            self.strokes.pop()
            return True
        return False

    def clear(self):
        """Clears all strokes."""
        self.strokes.clear()
        self.current_stroke = None
        self.selected_stroke = None
        self.last_move_pt = None

    @property
    def undo_count(self):
        return len(self.strokes)

    def render(self, frame):
        """
        Renders all strokes and current active stroke onto the frame.
        Supports glow bloom, rainbow colors, mirror reflection, and dark mode fill.
        """
        h, w, c = frame.shape
        self.width = w
        self.height = h

        # If fill mode is active, blend frame with dark chalkboard background
        if self.fill_mode:
            dark_bg = np.zeros_like(frame)
            dark_bg[:] = (20, 22, 26)  # Sleek dark matte chalkboard
            frame = cv2.addWeighted(frame, 0.25, dark_bg, 0.75, 0)

        # Collect all strokes to render (committed + ongoing)
        all_strokes = list(self.strokes)
        if self.current_stroke is not None and len(self.current_stroke.points) > 0:
            all_strokes.append(self.current_stroke)

        if not all_strokes:
            return frame

        # Separate glow strokes vs regular strokes for efficient batch bloom
        has_glow = any(s.glow for s in all_strokes)

        if has_glow:
            glow_layer = np.zeros_like(frame)
            for stroke in all_strokes:
                if stroke.glow:
                    self._draw_stroke_lines(glow_layer, stroke, w, is_glow_pass=True)
            # Apply multi-scale Gaussian blur for bright neon bloom
            blur1 = cv2.GaussianBlur(glow_layer, (21, 21), 9)
            blur2 = cv2.GaussianBlur(glow_layer, (41, 41), 19)
            # Add neon glow to frame
            frame = cv2.add(frame, cv2.addWeighted(blur1, 0.7, blur2, 0.5, 0))

        # Render crisp core lines
        for stroke in all_strokes:
            self._draw_stroke_lines(frame, stroke, w, is_glow_pass=False)

        # Highlight selected stroke in MOVE mode with dashed/pulsing bounding box
        if self.selected_stroke is not None:
            bbox = self.selected_stroke.get_bbox()
            if bbox is not None:
                bx1, by1, bx2, by2 = bbox
                bx1, by1 = max(0, bx1), max(0, by1)
                bx2, by2 = min(w - 1, bx2), min(h - 1, by2)
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 255, 120), 2, cv2.LINE_AA)
                cv2.putText(frame, "SELECTED", (bx1, max(20, by1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 120), 1, cv2.LINE_AA)

        return frame

    def _draw_stroke_lines(self, target_img, stroke, screen_w, is_glow_pass=False):
        """Draws stroke segments with optional rainbow, mirror, and glow styling."""
        pts = stroke.points
        n = len(pts)
        if n == 0:
            return

        base_thick = stroke.thickness if not is_glow_pass else stroke.thickness + 4

        # Single point (dot)
        if n == 1:
            color = stroke.color
            if stroke.rainbow and stroke.hues:
                color = self._hue_to_bgr(stroke.hues[0])
            cv2.circle(target_img, pts[0], base_thick // 2, color, -1, cv2.LINE_AA)
            if stroke.mirror:
                m_pt = (screen_w - pts[0][0], pts[0][1])
                cv2.circle(target_img, m_pt, base_thick // 2, color, -1, cv2.LINE_AA)
            return

        # Multi-point continuous lines
        for i in range(n - 1):
            p1 = pts[i]
            p2 = pts[i + 1]

            color = stroke.color
            if stroke.rainbow:
                hue = stroke.hues[i] if i < len(stroke.hues) else 0.0
                color = self._hue_to_bgr(hue)

            cv2.line(target_img, p1, p2, color, base_thick, cv2.LINE_AA)
            cv2.circle(target_img, p1, base_thick // 2, color, -1, cv2.LINE_AA)

            if stroke.mirror:
                mp1 = (screen_w - p1[0], p1[1])
                mp2 = (screen_w - p2[0], p2[1])
                cv2.line(target_img, mp1, mp2, color, base_thick, cv2.LINE_AA)
                cv2.circle(target_img, mp1, base_thick // 2, color, -1, cv2.LINE_AA)

        # Cap last point
        last_color = stroke.color
        if stroke.rainbow and stroke.hues:
            last_color = self._hue_to_bgr(stroke.hues[-1])
        cv2.circle(target_img, pts[-1], base_thick // 2, last_color, -1, cv2.LINE_AA)
        if stroke.mirror:
            last_mpt = (screen_w - pts[-1][0], pts[-1][1])
            cv2.circle(target_img, last_mpt, base_thick // 2, last_color, -1, cv2.LINE_AA)

    @staticmethod
    def _hue_to_bgr(hue):
        """Converts normalized hue [0, 1] to BGR tuple."""
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return (int(b * 255), int(g * 255), int(r * 255))

    def save_artwork(self, frame):
        """Saves current frame with drawings to the saved/ directory."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"GestureCanvas_{timestamp}.png"
        filepath = os.path.join(self.save_dir, filename)
        cv2.imwrite(filepath, frame)
        return filepath
