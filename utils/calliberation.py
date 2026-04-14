import cv2

cap = cv2.VideoCapture("Demo.mp4")
ret, frame = cap.read()
if ret:
    cv2.imwrite("calibration_frame.jpg", frame)
    print("Calibration frame saved ")
cap.release()