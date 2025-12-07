# PHÂN TÍCH HỆ THỐNG - AI MODEL GIÁM SÁT MẬT ĐỘ GIAO THÔNG

## 📋 TỔNG QUAN CHUNG

Đây là một hệ thống AI computer vision sử dụng **YOLO (You Only Look Once)** để phát hiện và đếm phương tiện giao thông theo thời gian thực. Hệ thống tự động gửi cảnh báo khi mật độ giao thông vượt ngưỡng và tích hợp với hệ thống giám sát lũ lụt/tắc đường thông qua API.

### Tên Dự Án
- **Component**: Traffic Density Monitoring System
- **Model**: YOLO v8/v11
- **License**: Apache License 2.0, CC BY 4.0 (dataset)

### Mục Đích
- Phát hiện và đếm phương tiện giao thông từ camera/video
- Giám sát mật độ giao thông theo thời gian thực
- Tự động gửi cảnh báo khi vượt ngưỡng
- Tích hợp với hệ thống sensor để tự động tạo zones cảnh báo
- Hỗ trợ nhiều loại phương tiện (8 classes)

---

## 🏗️ CẤU TRÚC DỰ ÁN

```
models/
├── train.py                              # Script huấn luyện model YOLO
├── traffic_monitor.py                    # Main monitoring application
├── api_client.py                         # API client tích hợp với backend
├── monitor_config.yaml                   # Cấu hình giám sát
├── data.yaml                            # Cấu hình dataset cho training
│
├── yolo11n.pt                           # YOLO v11 nano pre-trained (5.4MB)
├── yolov8s.pt                           # YOLO v8 small pre-trained (22MB)
├── calibration_image_sample_data_*.npy  # Sample data cho calibration
│
├── dataset/                             # Dataset YOLOv11 format
│   ├── data.yaml                       # Metadata dataset
│   ├── README.roboflow.txt             # Thông tin từ Roboflow
│   ├── train/                          # 2,363 ảnh training
│   │   ├── images/
│   │   └── labels/                     # YOLO format annotations
│   ├── valid/                          # 675 ảnh validation
│   │   ├── images/
│   │   └── labels/
│   └── test/                           # 338 ảnh testing
│       ├── images/
│       └── labels/
│
├── runs/                                # Training results
│   └── detect/
│       ├── train/                      # First training run
│       │   ├── weights/
│       │   │   ├── best.pt            # Best model weights
│       │   │   └── last.pt            # Last checkpoint
│       │   ├── results.png            # Training metrics plot
│       │   ├── confusion_matrix.png
│       │   └── ...                    # Other metrics/plots
│       └── train2/                     # Second training run
│
├── detections/                          # Saved detection images (runtime)
├── output_videos/                       # Saved output videos (optional)
├── monitoring.log                       # Application logs
│
├── requirements.txt                     # Python dependencies
├── LICENSE                              # Apache License 2.0
└── NOTICE                               # Copyright notice
```

---

## 💻 CÔNG NGHỆ SỬ DỤNG

### AI/ML Framework
- **Ultralytics YOLO** (≥8.0.0) - State-of-the-art object detection
  - YOLOv8s: Small model, cân bằng speed/accuracy
  - YOLOv11n: Nano model, ultra-fast cho edge devices
- **PyTorch** - Deep learning backend (optional, trong ultralytics)

### Computer Vision
- **OpenCV** (≥4.8.0) - Image/video processing
- **NumPy** (≥1.24.0) - Numerical computations
- **Pillow** (≥10.0.0) - Image manipulation

### Integration
- **Requests** (≥2.31.0) - HTTP client cho API calls
- **PyYAML** (≥6.0) - Configuration management

### Hardware Support
- **CPU**: Full support
- **GPU**: CUDA support (optional, faster inference)
  - torch ≥2.0.0
  - torchvision ≥0.15.0

---

## 🗄️ CẤU TRÚC DỮ LIỆU

### 1. Dataset Configuration (data.yaml)

```yaml
train: dataset/train/images         # 2,363 images
val: dataset/valid/images           # 675 images  
test: dataset/test/images           # 338 images

nc: 8                               # Number of classes
names: [                            # Class names
  'bicycle', 
  'bus', 
  'car', 
  'container_truck', 
  'fire_engine', 
  'motorcycle', 
  'truck', 
  'van'
]

# Dataset info
roboflow:
  workspace: luong-duc
  project: vehicle_detection_project-8jikm
  version: 1
  license: CC BY 4.0
  url: https://universe.roboflow.com/luong-duc/vehicle_detection_project-8jikm/dataset/1
```

**Dataset Details:**
- **Total**: 3,376 images
- **Format**: YOLOv11 (YOLO format)
- **Resolution**: 640x640 (stretched from original)
- **Annotations**: Bounding boxes for 8 vehicle types
- **Pre-processing**: Auto-orientation, resize to 640x640
- **Augmentation**: None (raw dataset)
- **Source**: Roboflow Universe

### 2. YOLO Label Format

Mỗi file `.txt` trong `labels/` có format:
```
<class_id> <x_center> <y_center> <width> <height>
```

Tất cả giá trị được normalize (0.0 - 1.0):
- `class_id`: 0-7 (tương ứng với 8 classes)
- `x_center`, `y_center`: Tọa độ tâm bounding box
- `width`, `height`: Kích thước bounding box

**Ví dụ:**
```
2 0.5124 0.3456 0.1234 0.2345    # car
5 0.7890 0.6543 0.0987 0.1543    # motorcycle
```

### 3. Monitor Configuration (monitor_config.yaml)

```yaml
api:
  endpoint: "http://localhost:3000/api/sensor-data"
  timeout: 10
  retry_attempts: 3

locations:
  - id: "sensor-intersection-01"
    name: "Main Street Intersection"
    coordinates:
      lat: 10.762622
      lon: 106.660172
    density_threshold: 15           # Vehicles count to trigger alert
    video_source: 0                 # Camera ID or video path
    confidence_threshold: 0.5       # Detection confidence
    check_interval: 30              # Seconds between checks
    count_vehicle_types: [...]      # Which types to count

model:
  weights: "runs/detect/train/weights/best.pt"
  imgsz: 640
  device: 0                         # 0=GPU, 'cpu'=CPU
  half: false                       # FP16 inference
  max_det: 300                      # Max detections per frame

logging:
  level: "INFO"
  save_detections: true
  detections_dir: "detections"
  log_file: "monitoring.log"

display:
  show_video: true                  # Show live preview
  save_video: false
  output_dir: "output_videos"
```

### 4. API Request/Response Format

**Request to Backend API (POST /api/sensor-data):**
```json
{
  "sensorId": "sensor-intersection-01",
  "value": 25.0,                    // Vehicle count
  "timestamp": 1704556789000        // Unix timestamp (ms)
}
```

**Response:**
```json
{
  "success": true,
  "thresholdExceeded": true,
  "sensor": {
    "id": "sensor-intersection-01",
    "threshold": 20
  },
  "automation": {
    "rulesChecked": 3,
    "rulesTriggered": 2,
    "zonesCreated": [
      "auto-zone-1234567890",
      "auto-zone-1234567891"
    ]
  }
}
```

---

## 🔄 LUỒNG HOẠT ĐỘNG

### A. Luồng Training Model

1. **Chuẩn bị Dataset**
   - Download từ Roboflow (3,376 images)
   - Extract vào thư mục `dataset/`
   - Verify structure: train/valid/test với images + labels

2. **Cấu hình Training**
   - Edit `data.yaml` nếu cần (paths, classes)
   - Chọn pre-trained model: yolov8s.pt hoặc yolo11n.pt

3. **Chạy Training**
   ```bash
   python train.py
   ```
   
   **Script thực hiện:**
   ```python
   model = YOLO("yolov8s.pt")
   model.train(
       data="data.yaml",
       epochs=50,
       imgsz=640,
       batch=16,
       device=0  # GPU
   )
   ```

4. **Training Process**
   - Ultralytics YOLO tự động:
     - Load pre-trained weights
     - Fine-tune trên custom dataset
     - Save checkpoints mỗi epoch
     - Generate metrics: mAP, precision, recall
     - Create plots: confusion matrix, F1 curve, etc.

5. **Kết quả**
   - Lưu trong `runs/detect/train*/`
   - `weights/best.pt`: Model tốt nhất (theo mAP)
   - `weights/last.pt`: Checkpoint cuối cùng
   - `results.png`: Training curves
   - `confusion_matrix.png`: Confusion matrix

6. **Validation**
   - Tự động validate trên validation set
   - Metrics: mAP@0.5, mAP@0.5:0.95, precision, recall
   - Class-wise performance

### B. Luồng Monitoring Real-time

1. **Khởi động System**
   ```bash
   python traffic_monitor.py --config monitor_config.yaml --location 0
   ```

2. **Initialization (TrafficDensityMonitor.__init__)**
   - Load configuration từ YAML
   - Setup logging (console + file)
   - Load trained YOLO model từ weights
   - Initialize API client với retry logic
   - Create output directories

3. **Mở Video Source**
   - Camera: `video_source: 0` (webcam)
   - Video file: `video_source: "path/to/video.mp4"`
   - RTSP stream: `video_source: "rtsp://..."`
   - HTTP stream: `video_source: "http://..."`

4. **Main Loop (monitor_location)**
   ```
   WHILE video is active:
     ├─ Read frame
     │
     ├─ IF check_interval elapsed:
     │  ├─ Run YOLO inference
     │  ├─ Count vehicles by type
     │  ├─ Calculate total count
     │  │
     │  ├─ IF count >= density_threshold:
     │  │  ├─ Log HIGH DENSITY ALERT
     │  │  ├─ Save detection image
     │  │  ├─ Send data to API (api_client.send_sensor_data)
     │  │  ├─ Check API response
     │  │  └─ Log automation triggers
     │  │
     │  └─ ELSE:
     │     └─ Log normal density
     │
     ├─ IF display.show_video:
     │  ├─ Run inference for visualization
     │  ├─ Draw bounding boxes + labels
     │  ├─ Add text overlay (location name, etc.)
     │  └─ Display in OpenCV window
     │
     └─ Check for quit key ('q')
   ```

5. **YOLO Inference Details**
   ```python
   results = model.predict(
       frame,
       conf=0.5,           # Confidence threshold
       imgsz=640,          # Input size
       device=0,           # GPU
       max_det=300,        # Max detections
       half=False,         # FP16
       verbose=False
   )
   ```

   **Output:**
   - Bounding boxes: [x1, y1, x2, y2]
   - Classes: [0-7]
   - Confidence scores: [0.0-1.0]

6. **Vehicle Counting**
   ```python
   def count_vehicles(results, vehicle_types):
       counts = {vtype: 0 for vtype in vehicle_types}
       for result in results:
           for box in result.boxes:
               class_name = result.names[int(box.cls[0])]
               if class_name in vehicle_types:
                   counts[class_name] += 1
       return counts
   ```

7. **Alert Triggering**
   - Nếu `total_count >= density_threshold`:
     - Save ảnh có annotations vào `detections/`
     - Gọi API với sensor data
     - Log kết quả automation (zones created)

8. **API Integration**
   - POST request với retry (3 attempts)
   - Exponential backoff: 2, 4, 8 seconds
   - Handle responses:
     - 200/201: Success
     - 202: Sensor not found (warning)
     - 400: Bad request (error)
     - 5xx: Server error (retry)

### C. Luồng Tích Hợp với Backend

1. **Sensor Registration** (Manual via admin panel)
   - Admin tạo sensor trong app
   - Sensor ID phải match với `id` trong monitor_config.yaml
   - Set threshold cho sensor (vd: 20 vehicles)

2. **Real-time Data Flow**
   ```
   [Camera/Video]
        ↓
   [YOLO Model] → Detect & Count
        ↓
   [Traffic Monitor] → Check threshold
        ↓ (if exceeded)
   [API Client] → POST /api/sensor-data
        ↓
   [Backend Rule Engine] → Check rules
        ↓ (if triggered)
   [Auto Create Zones] → Flood/Outage zones
        ↓
   [WebSocket Broadcast] → Notify all clients
        ↓
   [Map Display] → Show new zones real-time
   ```

3. **Automation Rules**
   - Backend có sensor rules (1-sensor, 2-sensor)
   - Khi nhận data, rule engine kiểm tra:
     - Value > threshold?
     - Multiple sensors với AND/OR logic?
   - Nếu trigger → Tự động tạo zone với:
     - Type: flood hoặc outage
     - Shape: circle (radius từ sensor location)
     - Title: "Tự Động: [Rule Name]"
     - Description: Ghi rõ sensor ID và giá trị

### D. Luồng Debugging & Visualization

1. **Live Video Display** (nếu `show_video: true`)
   - OpenCV window hiển thị frame với:
     - Bounding boxes màu (theo class)
     - Class labels + confidence scores
     - Location name overlay
     - Press 'q' để quit

2. **Save Detections** (nếu `save_detections: true`)
   - Mỗi alert tạo file ảnh:
   - Format: `{location_id}_{timestamp}_count{N}.jpg`
   - Ví dụ: `sensor-intersection-01_20250106_143052_count25.jpg`

3. **Logging**
   - Console output: Colored, structured
   - File log: `monitoring.log`
   - Log levels: DEBUG, INFO, WARNING, ERROR
   - Nội dung:
     - Frame analysis results
     - Vehicle counts by type
     - Threshold checks
     - API calls and responses
     - Automation triggers

---

## 📊 METRICS & PERFORMANCE

### Training Metrics

**Tiêu chí đánh giá:**
- **mAP@0.5**: Mean Average Precision với IoU threshold 0.5
- **mAP@0.5:0.95**: mAP trung bình từ IoU 0.5 đến 0.95
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: Harmonic mean của Precision và Recall

**Expected Performance** (YOLOv8s on this dataset):
- Training time: ~2-4 hours (GPU)
- mAP@0.5: ~85-95%
- Inference speed: ~50-100 FPS (GPU), ~5-10 FPS (CPU)

### Runtime Performance

**Hardware Requirements:**
- **Minimum (CPU)**:
  - Intel i5 hoặc equivalent
  - 8GB RAM
  - 2GB storage cho model + dataset
  - Speed: ~5-10 FPS

- **Recommended (GPU)**:
  - NVIDIA GPU với CUDA (GTX 1060+)
  - 16GB RAM
  - 4GB storage
  - Speed: ~50-100 FPS

**Optimization Tips:**
- Use YOLOv11n (5.4MB) thay vì YOLOv8s (22MB) cho edge devices
- Enable FP16 inference: `half: true` (2x faster on compatible GPUs)
- Giảm `imgsz` xuống 416 hoặc 320 (trade-off accuracy)
- Giảm `max_det` nếu không cần detect nhiều objects
- Batch processing nếu process nhiều cameras

---

## 🎨 CLASSES & DETECTION

### Vehicle Classes (8 loại)

| ID | Class Name      | Mô Tả                     | Typical Size | Priority |
|----|-----------------|---------------------------|--------------|----------|
| 0  | bicycle         | Xe đạp                    | Small        | Low      |
| 1  | bus             | Xe buýt, xe khách         | Large        | High     |
| 2  | car             | Ô tô con, sedan, SUV      | Medium       | High     |
| 3  | container_truck | Xe container              | Very Large   | High     |
| 4  | fire_engine     | Xe cứu hỏa                | Large        | Critical |
| 5  | motorcycle      | Xe máy, mô tô             | Small        | Medium   |
| 6  | truck           | Xe tải                    | Large        | High     |
| 7  | van             | Xe van, minibus           | Medium       | Medium   |

### Detection Examples

**Typical Confidence Scores:**
- Car, Motorcycle: 0.85-0.95 (high accuracy)
- Bus, Truck: 0.75-0.90
- Bicycle, Van: 0.65-0.85
- Container truck, Fire engine: 0.70-0.85

**Challenging Scenarios:**
- Occlusion (xe che khuất nhau): giảm recall
- Night time: giảm confidence
- Bad weather (mưa, sương mù): giảm accuracy
- Small objects (xa camera): giảm detection rate
- Motion blur: giảm confidence

---

## 🔧 CÁC FILE CHÍNH

### 1. train.py

**Mục đích**: Script train YOLO model trên custom dataset

**Code chính:**
```python
from ultralytics import YOLO

model = YOLO("yolov8s.pt")  # Load pre-trained
model.train(
    data="data.yaml",       # Dataset config
    epochs=50,              # Training epochs
    imgsz=640,              # Image size
    batch=16,               # Batch size
    device=0                # GPU device
)
```

**Output**:
- Tự động save vào `runs/detect/train/`
- Best model: `weights/best.pt`
- Metrics plots, confusion matrix

### 2. traffic_monitor.py (359 lines)

**Class: TrafficDensityMonitor**

**Methods:**
- `__init__(config_path)`: Khởi tạo, load model
- `_setup_logging()`: Config logging
- `count_vehicles(results, vehicle_types)`: Đếm xe theo loại
- `process_frame(frame, location_config)`: Xử lý 1 frame
- `save_detection_image(results, location_id, count)`: Lưu ảnh
- `monitor_location(location_config)`: Main monitoring loop
- `run(location_index)`: Chạy 1 location
- `run_all_locations()`: Chạy tất cả locations

**Main Entry:**
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="monitor_config.yaml")
    parser.add_argument("--location", type=int, default=0)
    parser.add_argument("--all", action="store_true")
    
    monitor = TrafficDensityMonitor(config_path=args.config)
    
    if args.all:
        monitor.run_all_locations()
    else:
        monitor.run(location_index=args.location)
```

**Usage:**
```bash
# Monitor location 0
python traffic_monitor.py

# Monitor location 1
python traffic_monitor.py --location 1

# Monitor all locations
python traffic_monitor.py --all

# Custom config
python traffic_monitor.py --config my_config.yaml
```

### 3. api_client.py (167 lines)

**Class: SensorAPIClient**

**Methods:**
- `__init__(endpoint, timeout, retry_attempts)`: Khởi tạo client
- `send_sensor_data(sensor_id, value, timestamp)`: Gửi data
- `get_recent_data(limit)`: Lấy historical data

**Features:**
- Automatic retry với exponential backoff
- Comprehensive error handling
- Response parsing and logging
- Support for different status codes

**Usage:**
```python
client = SensorAPIClient(
    endpoint="http://localhost:3000/api/sensor-data",
    timeout=10,
    retry_attempts=3
)

response = client.send_sensor_data(
    sensor_id="sensor-001",
    value=25.5
)
```

---

## 🚀 HƯỚNG DẪN SỬ DỤNG

### Setup Environment

```bash
cd models/

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# For GPU support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Training Workflow

```bash
# 1. Verify dataset structure
ls dataset/train/images  # Should have images
ls dataset/train/labels  # Should have .txt files

# 2. Check data.yaml
cat data.yaml

# 3. Start training
python train.py

# 4. Monitor progress (Ultralytics provides live updates)
# Training metrics displayed in terminal

# 5. Check results
cd runs/detect/train/
ls weights/  # best.pt, last.pt
ls *.png     # Metrics plots

# 6. Validate
python -c "from ultralytics import YOLO; \
           model = YOLO('runs/detect/train/weights/best.pt'); \
           metrics = model.val(); \
           print(metrics)"
```

### Monitoring Workflow

```bash
# 1. Edit configuration
nano monitor_config.yaml

# Key settings to change:
# - api.endpoint: Your API URL
# - locations[0].id: Match với sensor ID trong backend
# - locations[0].video_source: Camera ID hoặc video path
# - locations[0].density_threshold: Alert threshold
# - model.weights: Path to trained model

# 2. Test API connection
python api_client.py

# 3. Start monitoring
python traffic_monitor.py --location 0

# 4. Monitor logs
tail -f monitoring.log

# 5. Check detections
ls detections/
```

### Testing with Video File

```yaml
# monitor_config.yaml
locations:
  - id: "sensor-test-001"
    video_source: "test_video.mp4"  # Path to video
    # ... other settings
```

```bash
python traffic_monitor.py --location 0
```

### Multi-Location Monitoring

**Option 1: Sequential (trong cùng 1 process)**
```bash
python traffic_monitor.py --all
```

**Option 2: Parallel (nhiều processes)**
```bash
# Terminal 1
python traffic_monitor.py --location 0

# Terminal 2
python traffic_monitor.py --location 1

# Terminal 3
python traffic_monitor.py --location 2
```

---

## 📡 API INTEGRATION

### Backend API Requirements

**Endpoint: POST /api/sensor-data**

**Request:**
```json
{
  "sensorId": "string",
  "value": "number",
  "timestamp": "number (optional)"
}
```

**Response:**
```json
{
  "success": "boolean",
  "message": "string (optional)",
  "thresholdExceeded": "boolean (optional)",
  "sensor": {
    "id": "string",
    "name": "string",
    "threshold": "number"
  },
  "automation": {
    "rulesChecked": "number",
    "rulesTriggered": "number",
    "zonesCreated": ["string array"]
  }
}
```

### Error Handling

**Status Codes:**
- 200/201: Success
- 202: Accepted but sensor not found
- 400: Bad request (invalid format)
- 500: Server error
- Timeout: Network error

**Retry Logic:**
- 3 attempts mặc định
- Exponential backoff: 2s, 4s, 8s
- Log mỗi attempt
- Raise exception sau khi hết attempts

---

## 🔍 TROUBLESHOOTING

### Common Issues

**1. Model không load được**
```
Error: No such file or directory: 'runs/detect/train/weights/best.pt'
```
**Solution**: Train model trước hoặc dùng pre-trained:
```yaml
model:
  weights: "yolov8s.pt"  # Use pre-trained
```

**2. Camera không mở được**
```
Error: Failed to open video source: 0
```
**Solutions:**
- Check camera permissions
- Try different camera ID (0, 1, 2...)
- Check camera đã được plug in chưa
- Linux: `ls /dev/video*`

**3. API connection failed**
```
Error: Failed to send data after all retries
```
**Solutions:**
- Check backend server đang chạy
- Verify endpoint URL trong config
- Check firewall/network
- Test với curl:
  ```bash
  curl -X POST http://localhost:3000/api/sensor-data \
    -H "Content-Type: application/json" \
    -d '{"sensorId":"test","value":10}'
  ```

**4. Inference quá chậm (CPU)**
```
Speed: 0.5 FPS
```
**Solutions:**
- Use smaller model: yolo11n.pt
- Giảm imgsz: 320 or 416
- Tăng check_interval: 60 seconds
- Enable half precision (GPU only)

**5. Low detection accuracy**
```
Many false positives/negatives
```
**Solutions:**
- Tăng confidence_threshold (0.5 → 0.7)
- Re-train với more data
- Check lighting conditions
- Adjust camera angle

**6. Out of memory (GPU)**
```
CUDA out of memory
```
**Solutions:**
- Giảm batch size trong training
- Use smaller model
- Giảm imgsz
- Close other GPU applications

---

## 📈 PERFORMANCE OPTIMIZATION

### Inference Speed

**GPU Optimization:**
```yaml
model:
  device: 0        # Use GPU 0
  half: true       # FP16 (2x faster)
  imgsz: 640       # Standard size
  max_det: 300     # Reasonable max
```

**CPU Optimization:**
```yaml
model:
  device: 'cpu'
  half: false      # CPU doesn't support FP16
  imgsz: 416       # Smaller = faster
  max_det: 100     # Limit detections
```

### Memory Usage

**Reduce Memory:**
- Use yolo11n.pt (5.4MB) instead of yolov8s.pt (22MB)
- Lower imgsz: 320, 416
- Disable save_detections if not needed
- Don't show_video in production

### Accuracy vs Speed Trade-off

| Model    | Size  | Speed (GPU) | mAP@0.5 | Use Case          |
|----------|-------|-------------|---------|-------------------|
| YOLO11n  | 5.4MB | ~200 FPS    | ~75%    | Edge, Real-time   |
| YOLO8s   | 22MB  | ~100 FPS    | ~85%    | General           |
| YOLO8m   | 50MB  | ~60 FPS     | ~90%    | High accuracy     |
| YOLO8l   | 88MB  | ~40 FPS     | ~92%    | Research          |
| YOLO8x   | 136MB | ~25 FPS     | ~93%    | Best accuracy     |

---

## 🎯 USE CASES & SCENARIOS

### 1. Giám Sát Ngã Tư Giao Thông

**Setup:**
```yaml
locations:
  - id: "sensor-intersection-hoangdieu-trahmieu"
    name: "Ngã Tư Hoàng Diệu - Trần Hưng Miếu"
    coordinates: {lat: 21.0285, lon: 105.8542}
    density_threshold: 30          # 30 xe = tắc
    video_source: "rtsp://camera-ip/stream"
    check_interval: 20             # Check mỗi 20s
    count_vehicle_types:
      - car
      - bus
      - motorcycle
      - truck
```

**Expected Behavior:**
- Normal: 10-20 vehicles
- Rush hour: 30-50 vehicles (trigger alert)
- Alert → Backend tạo "outage" zone radius 200m

### 2. Giám Sát Cao Tốc

**Setup:**
```yaml
locations:
  - id: "sensor-highway-km15"
    name: "Cao Tốc Hà Nội - Hải Phòng KM15"
    density_threshold: 50          # 50 xe = ùn tắc
    check_interval: 60             # Check mỗi phút
    count_vehicle_types:
      - car
      - bus
      - container_truck
      - truck
```

**Expected Behavior:**
- High speed → Low density
- Traffic jam → High density
- Focus on large vehicles (trucks, buses)

### 3. Khu Vực Ngập Lụt

**Setup:**
```yaml
locations:
  - id: "sensor-flood-prone-area"
    name: "Đường Nguyễn Khoái (Khu Dễ Ngập)"
    density_threshold: 5           # Threshold thấp = cảnh báo sớm
    check_interval: 10             # Check thường xuyên
    count_vehicle_types:
      - car
      - motorcycle
```

**Expected Behavior:**
- Giảm đột ngột traffic → Có thể do ngập
- Combine với water level sensors
- Alert → Tạo "flood" zone

### 4. Parking Lot Monitoring

**Setup:**
```yaml
locations:
  - id: "sensor-parking-vincom"
    name: "Bãi Đỗ Xe Vincom"
    density_threshold: 80          # 80% capacity
    check_interval: 120            # Check mỗi 2 phút
    count_vehicle_types:
      - car
      - motorcycle
```

**Expected Behavior:**
- Count parked vehicles
- Alert khi gần full
- Không cần tạo zones, chỉ thông báo

---

## 🔐 BẢO MẬT & BEST PRACTICES

### Security Considerations

**1. API Credentials**
```yaml
# DON'T commit sensitive configs to git
api:
  endpoint: "${API_ENDPOINT}"     # Use env vars
  api_key: "${API_KEY}"           # If needed
```

**2. Camera Access**
- Use RTSP authentication
- Restrict network access to cameras
- Monitor unauthorized access attempts

**3. Data Privacy**
- Không save ảnh có mặt người rõ ràng
- Blur faces nếu cần (OpenCV)
- Follow GDPR/data privacy laws
- Auto-delete old detection images

### Production Best Practices

**1. Monitoring & Alerting**
- Setup log aggregation (ELK stack)
- Monitor process health
- Alert on high error rates
- Track inference latency

**2. Reliability**
```python
# Auto-restart on crash
while True:
    try:
        monitor = TrafficDensityMonitor(config)
        monitor.run()
    except Exception as e:
        logger.error(f"Crashed: {e}")
        time.sleep(10)  # Wait before restart
```

**3. Resource Management**
- Limit max_det to prevent memory spike
- Rotate logs (logrotate)
- Clean old detection images
- Monitor disk usage

**4. Configuration Management**
- Use environment-specific configs
- Validate config on startup
- Document all parameters
- Version control configs (git)

---

## 📊 LUỒNG DỮ LIỆU TỔNG QUÁT

```
┌─────────────────────┐
│  Camera/Video Feed  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   OpenCV Capture    │
│   Read Frame        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   YOLO Model        │
│   - Detect objects  │
│   - Classify        │
│   - Get bboxes      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Vehicle Counter    │
│  - Count by type    │
│  - Sum total        │
└──────────┬──────────┘
           │
           ▼
      [Threshold?]
           │
     YES ──┴── NO → Continue
      │
      ▼
┌─────────────────────┐
│  Save Detection     │
│  Image (optional)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  API Client         │
│  POST sensor-data   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Backend System     │
│  - Check rules      │
│  - Auto create zones│
│  - WebSocket notify │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Frontend Map       │
│  Display zones      │
│  Real-time update   │
└─────────────────────┘
```

---

## 🎓 TÀI LIỆU THAM KHẢO

### YOLO & Ultralytics
- Ultralytics Docs: https://docs.ultralytics.com/
- YOLO v8 Paper: https://arxiv.org/abs/2305.09972
- YOLO v11 Release: https://github.com/ultralytics/ultralytics
- Training Guide: https://docs.ultralytics.com/modes/train/

### Computer Vision
- OpenCV Docs: https://docs.opencv.org/
- NumPy Docs: https://numpy.org/doc/

### Dataset
- Roboflow Universe: https://universe.roboflow.com/
- Dataset URL: https://universe.roboflow.com/luong-duc/vehicle_detection_project-8jikm/dataset/1
- YOLO Format: https://docs.ultralytics.com/datasets/detect/

### Integration
- Requests Docs: https://requests.readthedocs.io/
- PyYAML: https://pyyaml.org/

---

## 🔮 HƯỚNG PHÁT TRIỂN

### Phase 1: Current Features ✅
- ✅ YOLO detection (8 vehicle classes)
- ✅ Real-time monitoring
- ✅ Threshold-based alerting
- ✅ API integration
- ✅ Multi-location support

### Phase 2: Enhanced Detection
- [ ] Vehicle tracking (track IDs, trajectories)
- [ ] Speed estimation
- [ ] Traffic flow analysis (in/out counting)
- [ ] License plate recognition (OCR)
- [ ] Vehicle color detection

### Phase 3: Advanced Analytics
- [ ] Historical trend analysis
- [ ] Predictive modeling (ML)
- [ ] Anomaly detection
- [ ] Traffic pattern recognition
- [ ] Peak hour analysis

### Phase 4: Scalability
- [ ] Distributed processing (multi-GPU)
- [ ] Cloud deployment (AWS, Azure)
- [ ] Edge device support (Jetson Nano, Raspberry Pi)
- [ ] Kubernetes orchestration
- [ ] Load balancing cho nhiều cameras

### Phase 5: Integration
- [ ] MQTT protocol support
- [ ] Kafka streaming
- [ ] Time-series database (InfluxDB)
- [ ] Grafana dashboards
- [ ] Mobile notifications

### Phase 6: AI Improvements
- [ ] Active learning (improve model với production data)
- [ ] Multi-object tracking (MOT)
- [ ] 3D detection (depth estimation)
- [ ] Night/bad weather model variants
- [ ] Transformer-based models (DETR, ViT)

---

## 📞 SUPPORT & MAINTENANCE

### Logging & Debugging

**Enable Debug Logging:**
```yaml
logging:
  level: "DEBUG"
```

**Check Logs:**
```bash
# Real-time
tail -f monitoring.log

# Search errors
grep "ERROR" monitoring.log

# Count alerts
grep "HIGH DENSITY ALERT" monitoring.log | wc -l
```

### System Requirements Check

```bash
# Check Python version
python --version  # Should be 3.8+

# Check CUDA (GPU)
nvidia-smi

# Check OpenCV
python -c "import cv2; print(cv2.__version__)"

# Check Ultralytics
python -c "from ultralytics import YOLO; print('OK')"
```

### Monitoring Health

```bash
# CPU usage
top -p $(pgrep -f traffic_monitor)

# GPU usage
nvidia-smi -l 1

# Disk usage
df -h ./detections

# Memory usage
free -h
```

---

## 👥 TEAM & LICENSE

- **Maintainer**: PKA-OpenLD
- **License**: Apache License 2.0
- **Dataset License**: CC BY 4.0
- **Year**: 2025
- **Contact**: GitHub Issues

---

_Tài liệu này được tạo tự động dựa trên phân tích source code._
_Cập nhật lần cuối: 2025-12-05_
