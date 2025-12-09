
<p align="center">
  <img src="docs/FORMS_logo.png" alt="FORMS Logo" width="600"/>
</p>

<h1 align = "center">🚦 Traffic Density Monitoring System</h1>

<div align="center">

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![YOLO](https://img.shields.io/badge/YOLO-v8%20%7C%20v11-green.svg)
![Dataset License](https://img.shields.io/badge/dataset-CC%20BY%204.0-orange.svg)

*Hệ thống giám sát mật độ giao thông theo thời gian thực sử dụng AI, YOLO để phát hiện và đếm phương tiện*
</div>



## 📋 Tổng quan

Đây là hệ thống thị giác máy tính sử dụng **YOLO (You Only Look Once)** để phát hiện và đếm phương tiện theo thời gian thực. Hệ thống tự động gửi cảnh báo khi mật độ giao thông vượt ngưỡng và tích hợp với hệ thống giám sát ngập/lũ và tắc đường qua API.

### Khả năng chính

- 🚗 **8 Loại phương tiện**: Car, Bus, Truck, Van, Container Truck, Fire Engine, Motorcycle, Bicycle
- 📹 **Xử lý thời gian thực**: Phát hiện và đếm phương tiện từ camera/video
- 🚨 **Cảnh báo thông minh**: Thông báo tự động khi mật độ vượt ngưỡng
- 🗺️ **Hỗ trợ đa vị trí**: Giám sát nhiều giao lộ cùng lúc
- 🔗 **Tích hợp API**: Kết nối trực tiếp với hệ thống backend sensor
- ⚡ **Hiệu năng cao**: Hỗ trợ tăng tốc CPU và GPU

---

## 🚀 Tính năng

### Phát hiện & Giám sát
- Phát hiện phương tiện thời gian thực sử dụng YOLOv8/v11
- Hỗ trợ 8 loại phương tiện với độ chính xác cao
- Ngưỡng confidence có thể cấu hình
- Giám sát đa camera/vị trí
- Lưu ảnh và video phát hiện

### Hệ thống cảnh báo
- Cảnh báo dựa trên ngưỡng mật độ
- Thời gian cooldown có thể cấu hình
- Tích hợp API để tạo zone tự động
- Theo dõi dữ liệu lịch sử

### Hiệu năng
- YOLOv8s: Cân bằng tốc độ và độ chính xác
- YOLOv11n: Rất nhanh cho thiết bị edge (5.4MB)
- Hỗ trợ tăng tốc GPU (CUDA)
- Xử lý frame hiệu quả

---

## 📦 Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Trình quản lý gói pip
- (Tùy chọn) GPU hỗ trợ CUDA để tăng tốc

### Bắt đầu nhanh

1. **Clone repository**
```bash
git clone <repository-url>
cd models
```

2. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

3. **Tải mô hình đã huấn luyện trước**

Các mô hình đã được bao gồm trong repository:
- `yolo11n.pt` - YOLO v11 Nano (5.4MB) - Inference nhanh
- `yolov8s.pt` - YOLO v8 Small (22MB) - Độ chính xác tốt hơn

Hoặc tải mô hình custom từ `runs/detect/train/weights/best.pt`

---

## 🎯 Sử dụng

### Huấn luyện mô hình

```bash
python train.py
```

Hành động này sẽ:
- Tải dataset từ thư mục `dataset/`
- Huấn luyện theo cấu hình trong `data.yaml`
- Lưu kết quả vào `runs/detect/train*/`
- Tạo biểu đồ metrics và confusion matrix

Các tham số huấn luyện có thể cấu hình trong `train.py`:
- `epochs`: Số epoch (mặc định: 10)
- `imgsz`: Kích thước ảnh (mặc định: 640)
- `batch`: Kích thước batch (mặc định: 16)
- `device`: 'cpu' hoặc 'cuda'

### Giám sát thời gian thực

```bash
python traffic_monitor.py
```

Cấu hình trong `monitor_config.yaml`:

```yaml
locations:
  - id: "sensor-intersection-01"
    name: "Main Street Intersection"
    coordinates:
      lat: 10.762622
      lon: 106.660172
    density_threshold: 15
    video_source: 0  # hoặc "path/to/video.mp4"
    
model:
  path: "runs/detect/train/weights/best.pt"
  confidence_threshold: 0.5
  device: "cpu"  # hoặc "cuda"
```

### Sử dụng API Client

```python
from api_client import APIClient

client = APIClient(endpoint="http://localhost:3000/api/sensor-data")

# Gửi dữ liệu sensor
result = client.send_sensor_data(
    location_id="sensor-01",
    vehicle_count=25,
    density_level="HIGH",
    coordinates={"lat": 10.762622, "lon": 106.660172}
)
```

---

## 📊 Dataset

### Thông tin Dataset

- **Tổng số ảnh**: 3,376 images
  - Training: 2,363 images
  - Validation: 675 images
  - Testing: 338 images
- **Định dạng**: YOLOv11 (YOLO format)
- **Độ phân giải**: 640x640
- **Classes**: 8 vehicle types
- **License**: CC BY 4.0
- **Nguồn**: [Roboflow Universe](https://universe.roboflow.com/luong-duc/vehicle_detection_project-8jikm/dataset/1)

### Các loại phương tiện

```yaml
0: bicycle
1: bus
2: car
3: container_truck
4: fire_engine
5: motorcycle
6: truck
7: van
```

### Định dạng nhãn

YOLO format (tọa độ chuẩn hóa 0.0-1.0):
```
<class_id> <x_center> <y_center> <width> <height>
```

Ví dụ:
```
2 0.5124 0.3456 0.1234 0.2345  # car
5 0.7890 0.6543 0.0987 0.1543  # motorcycle
```

---

## 🏗️ Cấu trúc dự án

```
models/
├── train.py                    # Script huấn luyện
├── traffic_monitor.py          # Ứng dụng giám sát chính
├── api_client.py               # Client tích hợp API
├── monitor_config.yaml         # Cấu hình giám sát
├── data.yaml                   # Cấu hình dataset
│
├── yolo11n.pt                  # Mô hình YOLO v11 nano đã huấn luyện
├── yolov8s.pt                  # Mô hình YOLO v8 small đã huấn luyện
│
├── dataset/                    # Dataset huấn luyện
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   └── test/
│
├── runs/                       # Kết quả huấn luyện
│   └── detect/
│       └── train/
│           └── weights/
│               ├── best.pt
│               └── last.pt
│
├── detections/                 # Ảnh phát hiện lưu
├── output_videos/              # Video xử lý lưu
├── monitoring.log              # Log ứng dụng
│
└── requirements.txt            # Dependencies Python
```

---

## 🔧 Cấu hình

### Monitor Configuration (`monitor_config.yaml`)

```yaml
# API Configuration
api:
  endpoint: "http://localhost:3000/api/sensor-data"
  timeout: 10
  retry_attempts: 3

# Location Settings
locations:
  - id: "sensor-intersection-01"
    name: "Main Street Intersection"
    coordinates:
      lat: 10.762622
      lon: 106.660172
    density_threshold: 15
    video_source: 0  # 0 cho webcam, hoặc video file path
    
# Model Settings
model:
  path: "runs/detect/train/weights/best.pt"
  confidence_threshold: 0.5
  device: "cpu"  # hoặc "cuda"
  
# Processing Settings
processing:
  frame_skip: 1
  display_window: true
  save_detections: true
  save_videos: false
  
# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "monitoring.log"
```

