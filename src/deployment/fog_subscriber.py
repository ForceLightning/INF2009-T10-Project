import base64
import json
import time
from io import StringIO
from typing import Any

import cv2
import numpy as np
import paho.mqtt.client as mqtt
import pandas as pd
import requests

from deployment.config import BROKER_IP, TOPIC


def decode_img(payload: str) -> cv2.typing.MatLike:
    """Decodes an image from a base64 string.

    :param payload: Base64 encoded image
    :type payload: str
    :return: Decoded image
    :rtype: cv2.typing.MatLike
    """

    binary_data = base64.b64decode(payload)
    np_data = np.frombuffer(binary_data, np.uint8)
    decoded_img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    return decoded_img


def on_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
    """Handles the message received from the edge devices.

    :param client: Client instance for this callback, unused.
    :type client: mqtt.Client
    :param userdata: User data of any type, unused.
    :type userdata: Any
    :param message: The message received from the edge devices.
    :type message: mqtt.MQTTMessage
    """
    received_data = json.loads(message.payload)
    device_id = received_data["device_id"]

    print(f"Received data from device: {device_id}")

    for data_type, data in stored_data.items():
        if device_id not in data:
            if (
                data_type == "images"
                and isinstance(data, str)
                and received_data["return_image"]
            ):
                image = decode_img(data)
                data = image

    current_crowd_status = model_inference()
    requests.post(
        "http://localhost:8000/api/update_crowd_status",
        json={"status": current_crowd_status, "timestamp": time.time()},
        timeout=5.0,
    )
    print("data sent")


def model_inference():
    # TODO(chris): Perform model inference here
    # Get list of images
    images_list = list(stored_data["images"].values())

    # Get list of wifi data
    wifi_data_list = [
        pd.read_json(StringIO(df), orient="split")
        for df in stored_data["wifi"].values()
    ]
    wifi_data_agg = pd.concat(wifi_data_list)

    # Get list of bluetooth data
    bt_data_list = [
        pd.read_json(StringIO(df), orient="split") for df in stored_data["bt"].values()
    ]
    bt_data_agg = pd.concat(bt_data_list)

    # print(images_list)
    # print(wifi_data_agg)
    # print(bt_data_agg)

    # Perform model inference here

    return 1  # Dummy return value


def main():
    """
    The fog device will keep a copy of the data received from each
    edge device
    """
    global stored_data

    stored_data = {"images": {}, "wifi": {}, "bt": {}}

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Subscriber")  # type: ignore
    client.on_message = on_message
    client.user_data_set(stored_data)
    client.connect(BROKER_IP, 1883)
    client.subscribe(TOPIC)
    client.loop_forever()


if __name__ == "__main__":
    main()
