import cv2
import time
import threading
import numpy as np
from detection.detector import detect_and_track
from logic.speed import SpeedEstimator 
from action.api import send_event
from bridge.queue import metadata_queue

# 1. Initialize the calibrated estimator
# This instance uses the 4K trapezoid coordinates and 15-frame smoothing
estimator = SpeedEstimator()

# SECRET 3: Define allowed COCO classes to avoid "Train" or "Bird" errors
# 2: car, 3: motorcycle, 5: bus, 7: truck
ALLOWED_CLASSES = [2, 3, 5, 7]

def action_worker():
    """Background thread to handle API calls without lagging the video."""
    while True:
        event = metadata_queue.get()
        if event is None:
            break
        try:
            send_event(event)
        except Exception as e:
            print(f"API Error: {e}")
        finally:
            metadata_queue.task_done()

def run_pipeline(video_path):
    # Start the background API worker
    worker_thread = threading.Thread(target=action_worker, daemon=True)
    worker_thread.start()

    cap = cv2.VideoCapture(video_path)
    
    # Get metadata for precise timing
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0: fps = 30  # Fallback
    
    sent_ids = set()
    SPEED_THRESHOLD = 60 # Set your speed limit here (KM/H)
    frame_count = 0

    print(f"Processing started at {fps} FPS...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # SECRET 2: Time-based calculation for smoothing
        # Calculate timestamp based on frame index for consistency
        timestamp = frame_count / fps
        frame_count += 1
        
        # Get raw detections from your modular detector
        detections = detect_and_track(frame)

        for obj in detections:
            track_id = obj.get("track_id", -1)
            class_id = obj.get("class_id") # Ensure your detector returns this

            # Filter for specific vehicles and valid tracking
            if track_id == -1 or class_id not in ALLOWED_CLASSES:
                continue

            # SECRET 1 & 2: Perspective-aware speed calculation
            # This method now returns a smoothed integer KM/H
            speed = estimator.estimate(track_id, obj["bbox"], timestamp)
            
            # Visualization Logic
            x1, y1, x2, y2 = map(int, obj["bbox"])
            color = (0, 255, 0) # Green for normal
            
            if speed > SPEED_THRESHOLD:
                color = (0, 0, 255) # Red for speeding

            # Draw Bounding Box and Speed Label
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"ID:{track_id} | {speed} KM/H"
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Trigger API event for speeding vehicles (once per ID)
            if speed > SPEED_THRESHOLD and track_id not in sent_ids:
                sent_ids.add(track_id)
                metadata_queue.put({
                    "track_id": int(track_id),
                    "speed": speed,
                    "timestamp": round(timestamp, 2),
                    "status": "Speeding Violation"
                })
        
        # Display the result
        cv2.imshow("High-Precision Speed Monitoring", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    metadata_queue.put(None)  
    cap.release()
    cv2.destroyAllWindows()
    print("Pipeline shut down gracefully.")

if __name__ == "__main__":
    # Ensure your video path is correct
    run_pipeline("Demo.mp4")