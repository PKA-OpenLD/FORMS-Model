# 🚦 Traffic Density Monitoring System

<div align="center">

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![YOLO](https://img.shields.io/badge/YOLO-v8%20%7C%20v11-green.svg)
![Dataset License](https://img.shields.io/badge/dataset-CC%20BY%204.0-orange.svg)

*AI-powered real-time traffic density monitoring system using YOLO for vehicle detection and counting*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [License](#-license)

</div>

---

## 📋 Overview

This is an AI computer vision system that uses **YOLO (You Only Look Once)** for real-time vehicle detection and counting. The system automatically sends alerts when traffic density exceeds thresholds and integrates with flood/congestion monitoring systems via API.

### Key Capabilities

- 🚗 **8 Vehicle Classes**: Car, Bus, Truck, Van, Container Truck, Fire Engine, Motorcycle, Bicycle
- 📹 **Real-time Processing**: Detect and count vehicles from camera/video feeds
- 🚨 **Smart Alerting**: Automatic notifications when density exceeds thresholds
- 🗺️ **Multi-location Support**: Monitor multiple intersections simultaneously
- 🔗 **API Integration**: Seamlessly integrates with backend sensor systems
- ⚡ **High Performance**: Supports both CPU and GPU acceleration

---

## 🚀 Features

### Detection & Monitoring
- Real-time vehicle detection using YOLOv8/v11
- Support for 8 vehicle classes with high accuracy
- Configurable confidence thresholds
- Multiple camera/location monitoring
- Save detection images and videos

### Alert System
- Density-based threshold alerts
- Configurable cooldown periods
- API integration for automated zone creation
- Historical data tracking

### Performance
- YOLOv8s: Balanced speed and accuracy
- YOLOv11n: Ultra-fast for edge devices (5.4MB)
- GPU acceleration support (CUDA)
- Efficient frame processing

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-enabled GPU for faster processing

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd models
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download pre-trained models**

Models are included in the repository:
- `yolo11n.pt` - YOLO v11 Nano (5.4MB) - Fast inference
- `yolov8s.pt` - YOLO v8 Small (22MB) - Better accuracy

Or download custom-trained models from `runs/detect/train/weights/best.pt`

---

## 🎯 Usage

### Training a Model

```bash
python train.py
```

This will:
- Load the dataset from `dataset/` directory
- Train using the configuration in `data.yaml`
- Save results to `runs/detect/train*/`
- Generate metrics plots and confusion matrix

Training parameters can be customized in `train.py`:
- `epochs`: Number of training epochs (default: 10)
- `imgsz`: Image size (default: 640)
- `batch`: Batch size (default: 16)
- `device`: 'cpu' or 'cuda'

### Real-time Monitoring

```bash
python traffic_monitor.py
```

Configuration is in `monitor_config.yaml`:

```yaml
locations:
  - id: "sensor-intersection-01"
    name: "Main Street Intersection"
    coordinates:
      lat: 10.762622
      lon: 106.660172
    density_threshold: 15
    video_source: 0  # or "path/to/video.mp4"
    
model:
  path: "runs/detect/train/weights/best.pt"
  confidence_threshold: 0.5
  device: "cpu"  # or "cuda"
```

### Using the API Client

```python
from api_client import APIClient

client = APIClient(endpoint="http://localhost:3000/api/sensor-data")

# Send sensor data
result = client.send_sensor_data(
    location_id="sensor-01",
    vehicle_count=25,
    density_level="HIGH",
    coordinates={"lat": 10.762622, "lon": 106.660172}
)
```

---

## 📊 Dataset

### Dataset Information

- **Total Images**: 3,376 images
  - Training: 2,363 images
  - Validation: 675 images
  - Testing: 338 images
- **Format**: YOLOv11 (YOLO format)
- **Resolution**: 640x640
- **Classes**: 8 vehicle types
- **License**: CC BY 4.0
- **Source**: [Roboflow Universe](https://universe.roboflow.com/luong-duc/vehicle_detection_project-8jikm/dataset/1)

### Vehicle Classes

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

### Label Format

YOLO format (normalized coordinates 0.0-1.0):
```
<class_id> <x_center> <y_center> <width> <height>
```

Example:
```
2 0.5124 0.3456 0.1234 0.2345  # car
5 0.7890 0.6543 0.0987 0.1543  # motorcycle
```

---

## 🏗️ Project Structure

```
models/
├── train.py                    # Training script
├── traffic_monitor.py          # Main monitoring application
├── api_client.py               # API integration client
├── monitor_config.yaml         # Monitoring configuration
├── data.yaml                   # Dataset configuration
│
├── yolo11n.pt                  # Pre-trained YOLO v11 nano
├── yolov8s.pt                  # Pre-trained YOLO v8 small
│
├── dataset/                    # Training dataset
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   └── test/
│
├── runs/                       # Training results
│   └── detect/
│       └── train/
│           └── weights/
│               ├── best.pt     # Best model checkpoint
│               └── last.pt     # Last checkpoint
│
├── detections/                 # Saved detection images
├── output_videos/              # Processed videos
├── monitoring.log              # Application logs
│
└── requirements.txt            # Python dependencies
```

---

## 🔧 Configuration

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
    video_source: 0  # 0 for webcam, or video file path
    
# Model Settings
model:
  path: "runs/detect/train/weights/best.pt"
  confidence_threshold: 0.5
  device: "cpu"  # or "cuda"
  
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

---

## 📈 Performance

### Model Comparison

| Model | Size | Speed (CPU) | mAP@0.5 | Use Case |
|-------|------|-------------|---------|----------|
| YOLOv11n | 5.4MB | ~30 FPS | ~85% | Edge devices, real-time |
| YOLOv8s | 22MB | ~20 FPS | ~90% | Balanced, production |
| Custom Trained | Variable | Variable | 92%+ | Best accuracy |

### System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Storage: 2 GB

**Recommended:**
- CPU: Quad-core 3.0 GHz or NVIDIA GPU (CUDA)
- RAM: 8 GB
- Storage: 10 GB

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Model not loading**
```bash
# Check if model file exists
ls -lh runs/detect/train/weights/best.pt

# Verify Ultralytics installation
python -c "from ultralytics import YOLO; print('OK')"
```

**Issue: Low FPS**
- Reduce image size: `imgsz=416` or `320`
- Enable GPU: `device='cuda'`
- Increase frame skip: `frame_skip=2`
- Use YOLOv11n for faster inference

**Issue: API connection failed**
- Check endpoint URL in `monitor_config.yaml`
- Verify backend service is running
- Check network connectivity

### Debug Mode

Enable debug logging:
```yaml
logging:
  level: "DEBUG"
```

View logs:
```bash
tail -f monitoring.log
```

---

## 🗺️ Roadmap

### Current Features ✅
- [x] YOLO detection (8 vehicle classes)
- [x] Real-time monitoring
- [x] Threshold-based alerting
- [x] API integration
- [x] Multi-location support

### Planned Features 🚧
- [ ] Vehicle tracking with IDs
- [ ] Speed estimation
- [ ] Traffic flow analysis
- [ ] License plate recognition
- [ ] Historical trend analysis
- [ ] Mobile app integration
- [ ] Cloud deployment support

---

## 📚 Documentation

### Additional Resources

- [System Analysis Document](PHAN_TICH_HE_THONG.md) - Detailed technical documentation (Vietnamese)
- [Ultralytics YOLO Docs](https://docs.ultralytics.com/)
- [Dataset on Roboflow](https://universe.roboflow.com/luong-duc/vehicle_detection_project-8jikm/dataset/1)

### API Reference

See [api_client.py](api_client.py) for detailed API integration examples.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

Dataset is licensed under **CC BY 4.0** - see dataset documentation for details.

---

## 👥 Authors & Acknowledgments

- **Maintainer**: PKA-OpenLD
- **Dataset**: [Luong Duc](https://universe.roboflow.com/luong-duc) via Roboflow Universe
- **YOLO Framework**: [Ultralytics](https://github.com/ultralytics/ultralytics)

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the system analysis document

---

<div align="center">

**Made with ❤️ using YOLO and OpenCV**

*Last updated: December 2025*

</div>
