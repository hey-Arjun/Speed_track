### 🚀 Modular Vision Pipeline: High-Precision Speed Estimation
A real-time, production-grade computer vision pipeline designed to monitor traffic, track vehicles, and estimate speeds with sub-pixel accuracy. Optimized for Apple Silicon (M1/M2/M3) using CoreML and engineered to solve the "Perspective Problem" in 2D video feeds.

### 🌟 Key Features
Real-Time Inference: 25-30 FPS on Apple M1 using yolov8n.mlpackage.

Perspective-Aware Math: Uses Homography matrices to map 2D pixels to 3D real-world meters.

Multi-Threaded Telemetry: An asynchronous worker handles API alerts without lagging the main video processing loop.

Jitter Reduction: 15-frame temporal smoothing to eliminate bounding-box noise.

### 🏗️ System Architecture
The pipeline is built on a modular "Bridge" pattern, separating detection logic from mathematical estimation and external actions.

Detection Layer: YOLOv8 (CoreML optimized) identifies vehicles.

Tracking Layer: BoT-SORT/ByteTrack maintains unique IDs across frames.

Logic Layer (The "Deep" Math):

Homography Transformation: Warps the camera's vanishing point into a bird's-eye view.

Coordinate Localization: Tracks the Bottom-Center of the bounding box to ensure vehicle height doesn't skew the distance calculation.

Action Layer: A threaded queue pushes speeding violations to a REST API.

### 📐 The "Deep" Logic: How Speed is Calculated
Standard pixel-per-frame calculation fails on roads because of the Vanishing Point Effect (objects get smaller as they move away). This pipeline solves that through:

1. Perspective Transformation (Homography)
We define a 2D trapezoid on the road surface and map it to a Top-Down rectangle representing real-world meters. We calculate a 3×3 matrix M where:
 
This ensures that a vehicle moving 10 pixels at the top of the frame represents the same physical distance as a vehicle moving 100 pixels at the bottom.

2. The "Tire-to-Asphalt" Rule
To keep the math consistent regardless of vehicle size (e.g., a tall truck vs. a low sports car), the system ignores the center of the bounding box and calculates speed based strictly on the Bottom-Center (cx,y2). This is the only point guaranteed to be on the calibrated road surface.

3. Temporal Smoothing
AI bounding boxes naturally "jitter." To prevent massive speed spikes, we use a 15-frame circular buffer (deque). Speed is calculated as a moving average across this window:

Formula: v = ΔTime ((seconds) / ΔDistance (meters)) ×3.6=km/h

### 💻 Tech Stack
Core: Python 3.11, OpenCV

AI/ML: Ultralytics YOLOv8, CoreML (Apple Silicon Optimization)

Math: NumPy (Linear Algebra & Matrix Transformations)

Concurrency: Threading & Queue (for non-blocking API calls)


### 🚀 Installation & Setup

Clone the repository:

```
git clone https://github.com/your-username/modular-vision-pipeline.git
cd modular-vision-pipeline
```

Set up the environment:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


```
python main.py
```