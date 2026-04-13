from ultralytics import YOLO
model = YOLO("yolov8n.pt")
model.export(format="coreml", nms=True)

def detect_and_track(frame):
    results = model.track(frame, persist=True)

    detections = []

    if len(results) == 0:
        return detections

    result = results[0]

    if result.boxes is None:
        return detections

    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0]

        track_id = -1
        if box.id is not None:
            track_id = int(box.id[0])

        cls = int(box.cls[0])
        conf = float(box.conf[0])

        detections.append({
            "track_id": track_id,
            "bbox": [float(x1), float(y1), float(x2), float(y2)],
            "class_id": cls,
            "confidence": conf
        })

    return detections