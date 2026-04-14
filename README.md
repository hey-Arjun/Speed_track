### 🚀 Modular Vision Pipeline: High-Precision Speed Estimation
A real-time, production-grade computer vision pipeline designed to monitor traffic, track vehicles, and estimate speeds with sub-pixel accuracy. Optimized for Apple Silicon (M1/M2/M3) using CoreML and engineered to solve the "Perspective Problem" in 2D video feeds.

### 🌟 Key Features
Real-Time Inference: 25-30 FPS on Apple M1.

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

### 📂 Project Structure

 -> main.py: The entry point. Manages the video stream and orchestrates the AI and Logic modules.

 -> logic/speed.py: Contains the SpeedEstimator class (Homography math & 15-frame smoothing).

 -> action/api.py: The "Messenger" module that handles HTTP POST requests.

 -> action/mock_server.py: A standalone FastAPI server to demonstrate data reception.

 -> detection/detector.py: Contains the YOLO wrapper and CoreML inference logic.

 -> bridge/queue.py: This is the heart of the system's stability. It implements a Threaded Worker Pattern.

### 📐 The Logic: How Speed is Calculated
Standard pixel-per-frame calculation fails on roads because of the Vanishing Point Effect (objects get smaller as they move away). This pipeline solves that through:

1. Perspective Transformation (Homography) (Bird's EYE)
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

Step A: Start the Mock Alert Server
Open a new terminal tab and start the FastAPI receiver. This simulates the backend system that handles speeding violations.

```
uvicorn action.mock_server:app --reload --port 8000
```

Step B: Start the Vision Pipeline
In your original terminal tab, run the main processing engine.

```
python main.py
```