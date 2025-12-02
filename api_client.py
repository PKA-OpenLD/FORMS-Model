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
API Client for sending sensor data to the flood/traffic monitoring service
"""

import requests
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SensorAPIClient:
    """Client for interacting with the sensor data API"""

    def __init__(self, endpoint: str, timeout: int = 10, retry_attempts: int = 3):
        """
        Initialize API client

        Args:
            endpoint: Base API endpoint URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts on failure
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.retry_attempts = retry_attempts

    def send_sensor_data(
        self, sensor_id: str, value: float, timestamp: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send sensor data to the API

        Args:
            sensor_id: Unique sensor identifier
            value: Sensor reading value (e.g., vehicle count)
            timestamp: Unix timestamp in milliseconds (optional)

        Returns:
            API response as dictionary

        Raises:
            requests.exceptions.RequestException: On API communication failure
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)

        payload = {"sensorId": sensor_id, "value": value, "timestamp": timestamp}

        logger.info(f"Sending data to API: sensorId={sensor_id}, value={value}")

        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout,
                )

                # Log response
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"✓ Data sent successfully: {result}")

                    # Log automation details if present
                    if "automation" in result:
                        auto = result["automation"]
                        logger.info(
                            f"  Automation: {auto.get('rulesTriggered', 0)} rules triggered, "
                            f"{len(auto.get('zonesCreated', []))} zones created"
                        )

                    return result

                elif response.status_code == 202:
                    result = response.json()
                    logger.warning(f"⚠ Sensor not found: {result.get('warning', '')}")
                    return result

                elif response.status_code == 400:
                    error_data = response.json()
                    logger.error(f"✗ Bad request: {error_data}")
                    raise requests.exceptions.RequestException(
                        f"Invalid request format: {error_data}"
                    )

                else:
                    logger.warning(
                        f"Unexpected status code {response.status_code}: {response.text}"
                    )
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt}/{self.retry_attempts} failed: {e}")

                if attempt < self.retry_attempts:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("All retry attempts failed")
                    raise

        raise requests.exceptions.RequestException(
            "Failed to send data after all retries"
        )

    def get_recent_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        Retrieve recent sensor data

        Args:
            limit: Maximum number of records to return

        Returns:
            API response with data array
        """
        try:
            response = requests.get(
                self.endpoint, params={"limit": limit}, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve data: {e}")
            raise


if __name__ == "__main__":
    # Test the API client
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Example usage
    client = SensorAPIClient(
        endpoint="http://localhost:3000/api/sensor-data", timeout=10, retry_attempts=3
    )

    try:
        # Send test data
        response = client.send_sensor_data(sensor_id="sensor-test-001", value=25.5)
        print(f"Response: {response}")

    except Exception as e:
        print(f"Error: {e}")
