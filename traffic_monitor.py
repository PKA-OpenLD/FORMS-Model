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

"""
Traffic Density Monitor using YOLO
Monitors traffic density and reports to sensor API when thresholds are exceeded
"""

import cv2
import yaml
import logging
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from ultralytics import YOLO

from api_client import SensorAPIClient


class TrafficDensityMonitor:
    """Monitor traffic density using YOLO detection"""

    def __init__(self, config_path: str = "monitor_config.yaml"):
        """
        Initialize the traffic density monitor

        Args:
            config_path: Path to configuration YAML file
        """
        # Load configuration
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Setup logging
        self._setup_logging()

        # Load YOLO model
        self.logger.info(f"Loading YOLO model from {self.config['model']['weights']}")
        self.model = YOLO(self.config["model"]["weights"])

        # Initialize API client
        api_config = self.config["api"]
        self.api_client = SensorAPIClient(
            endpoint=api_config["endpoint"],
            timeout=api_config["timeout"],
            retry_attempts=api_config["retry_attempts"],
        )

        # Create output directories
        if self.config["logging"]["save_detections"]:
            Path(self.config["logging"]["detections_dir"]).mkdir(exist_ok=True)

        if self.config["display"].get("save_video", False):
            Path(self.config["display"]["output_dir"]).mkdir(exist_ok=True)

        self.logger.info("Traffic Density Monitor initialized successfully")

    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config["logging"]

        # Configure logger
        self.logger = logging.getLogger("TrafficMonitor")
        self.logger.setLevel(getattr(logging, log_config["level"]))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_config["level"]))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_config.get("log_file"):
            file_handler = logging.FileHandler(log_config["log_file"])
            file_handler.setLevel(getattr(logging, log_config["level"]))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def count_vehicles(self, results, vehicle_types: List[str]) -> Dict[str, int]:
        """
        Count detected vehicles by type

        Args:
            results: YOLO detection results
            vehicle_types: List of vehicle types to count

        Returns:
            Dictionary with counts per vehicle type
        """
        counts = {vtype: 0 for vtype in vehicle_types}

        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = result.names[class_id]

                if class_name in vehicle_types:
                    counts[class_name] += 1

        return counts

    def process_frame(self, frame, location_config: Dict[str, Any]) -> tuple[int, Any]:
        """
        Process a single frame and detect vehicles

        Args:
            frame: Input frame (numpy array)
            location_config: Location configuration dictionary

        Returns:
            Tuple of (total_count, results)
        """
        # Run inference
        results = self.model.predict(
            frame,
            conf=location_config["confidence_threshold"],
            imgsz=self.config["model"]["imgsz"],
            device=self.config["model"]["device"],
            max_det=self.config["model"]["max_det"],
            half=self.config["model"]["half"],
            verbose=False,
        )

        # Count vehicles
        vehicle_counts = self.count_vehicles(
            results, location_config["count_vehicle_types"]
        )

        total_count = sum(vehicle_counts.values())

        return total_count, results, vehicle_counts

    def save_detection_image(self, results, location_id: str, count: int):
        """Save annotated detection image"""
        if not self.config["logging"]["save_detections"]:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{location_id}_{timestamp}_count{count}.jpg"
        filepath = os.path.join(self.config["logging"]["detections_dir"], filename)

        # Plot results on frame
        annotated_frame = results[0].plot()
        cv2.imwrite(filepath, annotated_frame)
        self.logger.debug(f"Saved detection image: {filepath}")

    def monitor_location(self, location_config: Dict[str, Any]):
        """
        Monitor a single location

        Args:
            location_config: Location configuration dictionary
        """
        location_id = location_config["id"]
        location_name = location_config["name"]
        video_source = location_config["video_source"]
        density_threshold = location_config["density_threshold"]
        check_interval = location_config["check_interval"]

        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"Starting monitoring: {location_name} ({location_id})")
        self.logger.info(f"Video source: {video_source}")
        self.logger.info(f"Density threshold: {density_threshold} vehicles")
        self.logger.info(f"Check interval: {check_interval} seconds")
        self.logger.info(f"{'=' * 60}\n")

        # Open video source
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            self.logger.error(f"Failed to open video source: {video_source}")
            return

        last_check_time = 0
        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    self.logger.warning("End of video or failed to read frame")
                    break

                frame_count += 1
                current_time = time.time()

                # Check if it's time to analyze
                if current_time - last_check_time >= check_interval:
                    self.logger.info(f"\n--- Analysis at frame {frame_count} ---")

                    # Process frame
                    total_count, results, vehicle_counts = self.process_frame(
                        frame, location_config
                    )

                    # Log counts
                    self.logger.info(f"Vehicle count: {total_count}")
                    for vtype, count in vehicle_counts.items():
                        if count > 0:
                            self.logger.info(f"  - {vtype}: {count}")

                    # Check threshold
                    if total_count >= density_threshold:
                        self.logger.warning(
                            f"⚠ HIGH DENSITY ALERT! Count: {total_count} "
                            f"(threshold: {density_threshold})"
                        )

                        # Save detection image
                        self.save_detection_image(results, location_id, total_count)

                        # Report to API
                        try:
                            response = self.api_client.send_sensor_data(
                                sensor_id=location_id, value=float(total_count)
                            )

                            # Check if automation was triggered
                            if response.get("thresholdExceeded"):
                                self.logger.warning(
                                    "🚨 Sensor threshold exceeded on server!"
                                )

                            if response.get("automation", {}).get("zonesCreated"):
                                zones = response["automation"]["zonesCreated"]
                                self.logger.warning(
                                    f"🚨 Alert zones created: {', '.join(zones)}"
                                )

                        except Exception as e:
                            self.logger.error(f"Failed to report to API: {e}")

                    else:
                        self.logger.info(
                            f"✓ Normal density (threshold: {density_threshold})"
                        )

                    last_check_time = current_time

                # Display frame if enabled
                if self.config["display"]["show_video"]:
                    # Run detection for display
                    display_results = self.model.predict(
                        frame,
                        conf=location_config["confidence_threshold"],
                        verbose=False,
                    )

                    annotated_frame = display_results[0].plot()

                    # Add info text
                    cv2.putText(
                        annotated_frame,
                        f"Location: {location_name}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )

                    cv2.imshow(f"Traffic Monitor - {location_name}", annotated_frame)

                    # Break on 'q' key
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        self.logger.info("User requested stop")
                        break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.logger.info(f"Monitoring stopped for {location_name}")

    def run(self, location_index: int = 0):
        """
        Start monitoring a specific location

        Args:
            location_index: Index of location in config (default: 0)
        """
        locations = self.config["locations"]

        if location_index >= len(locations):
            self.logger.error(
                f"Invalid location index {location_index}. "
                f"Available: 0-{len(locations) - 1}"
            )
            return

        location = locations[location_index]
        self.monitor_location(location)

    def run_all_locations(self):
        """Monitor all configured locations sequentially"""
        self.logger.info(
            f"Starting monitoring for all {len(self.config['locations'])} locations"
        )

        for idx, location in enumerate(self.config["locations"]):
            self.logger.info(f"\n{'#' * 60}")
            self.logger.info(f"Location {idx + 1}/{len(self.config['locations'])}")
            self.logger.info(f"{'#' * 60}")

            self.monitor_location(location)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Traffic Density Monitor using YOLO")
    parser.add_argument(
        "--config",
        type=str,
        default="monitor_config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--location", type=int, default=0, help="Location index to monitor (default: 0)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Monitor all locations sequentially"
    )

    args = parser.parse_args()

    # Initialize monitor
    monitor = TrafficDensityMonitor(config_path=args.config)

    # Run monitoring
    if args.all:
        monitor.run_all_locations()
    else:
        monitor.run(location_index=args.location)


if __name__ == "__main__":
    main()
