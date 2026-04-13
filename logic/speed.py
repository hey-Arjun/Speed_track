import numpy as np
import cv2
from collections import deque

class SpeedEstimator:
    def __init__(self):
        # Coordinates for the 4K frame
        self.src_pts = np.float32([
            [380, 100], [610, 100], 
            [150, 950], [950, 950]  
        ])
        
        self.dst_pts = np.float32([
            [0, 0], [3.75, 0],
            [0, 45], [3.75, 45]
        ])
        
        self.matrix = cv2.getPerspectiveTransform(self.src_pts, self.dst_pts)
        self.history = {}

    # RENAME THIS FROM estimate_speed TO estimate
    def estimate(self, track_id, bbox, timestamp):
        x1, y1, x2, y2 = bbox
        
        # Secret 1: Contact point (Bottom Center)
        cx = (x1 + x2) / 2
        cy = y2 
        
        point = np.array([[[cx, cy]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, self.matrix)[0][0]
        curr_pos = transformed 

        if track_id not in self.history:
            self.history[track_id] = deque(maxlen=15)
            self.history[track_id].append((curr_pos, timestamp))
            return 0

        # Secret 2: Smoothing window
        prev_pos, prev_time = self.history[track_id][0] 
        
        dist_m = np.linalg.norm(curr_pos - prev_pos)
        time_diff = timestamp - prev_time

        if time_diff <= 0:
            return 0

        raw_speed = (dist_m / time_diff) * 3.6
        self.history[track_id].append((curr_pos, timestamp))

        # JSON safe return
        return int(round(raw_speed))