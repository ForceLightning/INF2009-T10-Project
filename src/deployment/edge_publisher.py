"""Edge publisher module for the edge device.
"""

import json
import os
import time

import paho.mqtt.client as mqtt

from deployment.config import (
    BROKER_IP,
    DEVICE_IDX,
    PUBLISHER_INTERVAL,
    TOPIC,
    USE_DEMO_DATA,
)
from util.capture_image import encode_image, take_picture
from util.people_detection import detect
from util.wifi_bt_processing import get_and_parse_data


def retrieve_data(device_id: int = DEVICE_IDX, return_image: bool = False) -> str:
    """Retrieves data from the camera, wifi and bluetooth devices.

    :param device_id: Device ID set by environment variables, defaults to DEVICE_IDX
    :type device_id: int, optional
    :param return_image: Whether to return the image or not, defaults to False
    :type return_image: bool, optional
    :return: JSON string containing the image, timestamp, wifi signal strength, bluetooth output and device ID
    :rtype: str
    """

    # Get the wifi signal strength
    wifi_strength, bt_output = get_and_parse_data(
        USE_DEMO_DATA,
        device_id,
        koufu_csv_path=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "demo/koufu.csv"
        ),
        total_devices=4,
        top_n=5,
    )

    if USE_DEMO_DATA:
        image = take_picture(
            None,
            USE_DEMO_DATA,
            filename=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f"demo/image_{device_id}.jpg",
            ),
        )
    else:
        # Capture an image from the camera
        image = take_picture()

    if return_image:
        image_inference = encode_image(image)
    else:
        preds = detect(image)
        image_inference = len(preds)

    return json.dumps(
        {
            "image": image_inference,
            "timestamp": time.time(),
            "wifi_strength": wifi_strength,
            "bt_output": bt_output,
            "device_id": device_id,
            "return_image": return_image,
        }
    )


def main():
    """Main function for publishing data to the MQTT broker."""
    device_id = DEVICE_IDX

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Publisher")  # type: ignore
    client.connect(BROKER_IP, 1883)

    while True:
        data = retrieve_data(device_id)
        client.publish(TOPIC, data)
        time.sleep(PUBLISHER_INTERVAL)


if __name__ == "__main__":
    main()
