# ------------------------------------------------------------------------------
# Copyright 2025 PKA-OpenLD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from ultralytics import YOLO

# Use a small model first for speed
model = YOLO("yolov8s.pt")  # or yolov8n.pt for even faster, smaller

# Train
model.train(
    data="data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    device=0,  # GPU
)
