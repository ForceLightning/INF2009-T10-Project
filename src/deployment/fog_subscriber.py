import base64
import datetime
import json
import os
import pickle
import math
from collections import OrderedDict
from pathlib import Path
from typing import Any, TypedDict

import cv2
import numpy as np
import paho.mqtt.client as mqtt
import requests

from deployment.config import BROKER_IP, TOP_N_APS, TOPIC, TOTAL_DEVICES
from util.people_detection import detect
from util.wifi_bt_processing import (
    get_bbox_counts_column_index,
    get_bt_column_index,
    get_wifi_column_indices,
)


class DataFromEdge(TypedDict):
    """Data received from the edge devices.

    :param device_id: Device ID
    :type device_id: int
    :param return_image: Whether to return the image or not
    :type return_image: bool
    :param image: Image data or bounding box counts
    :type image: cv2.typing.MatLike | int
    :param wifi_data: WiFi signal strength data
    :type wifi_data: list[int]
    :param bt_data: Bluetooth output data
    :type bt_data: int
    """

    device_id: int
    return_image: bool
    image: cv2.typing.MatLike | int
    wifi_data: list[int]
    bt_data: int


class CrowdStatus(TypedDict):
    """Crowd status data stored by the fog device.

    :param status: Number of people in the crowd
    :type status: int
    :param err: Error in the crowd status prediction (if any)
    :type err: float | None
    :param timestamp: Timestamp of the crowd status
    :type timestamp: datetime.datetime
    :param data: Data received from the edge devices
    :type data: dict[int, DataFromEdge]
    :param numpy_data: Numpy data for the crowd status prediction
    :type numpy_data: np.ndarray
    """

    status: int
    err: float | None
    timestamp: datetime.datetime
    data: dict[int, DataFromEdge]
    numpy_data: np.ndarray


base_numpy_data = np.zeros((1, TOP_N_APS * TOTAL_DEVICES + 2 * TOTAL_DEVICES))
stored_data = CrowdStatus(
    status=0,
    err=None,
    timestamp=datetime.datetime.fromtimestamp(0.0),
    data={},
    numpy_data=base_numpy_data,
)


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

    client_data_typed = DataFromEdge(
        device_id=device_id,
        return_image=received_data["return_image"],
        image=received_data["image"],
        wifi_data=received_data["wifi_data"],
        bt_data=received_data["bt_data"],
    )

    # Perform inference on the image if it is returned.
    if client_data_typed["return_image"] and isinstance(
        client_data_typed["image"], str
    ):
        image = decode_img(client_data_typed["image"])
        bbox_counts = len(detect(image))
        client_data_typed["image"] = bbox_counts

    stored_data["data"][device_id] = client_data_typed

    current_crowd_status = model_inference()
    if isinstance(current_crowd_status, tuple):
        current_crowd_status, err = current_crowd_status
        stored_data["err"] = err

    stored_data["status"] = current_crowd_status

    requests.post(
        "http://localhost:8000/api/update_crowd_status",
        json={
            "status": stored_data["status"],
            "err": stored_data["err"],
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        },
        timeout=5.0,
    )
    print("data sent")


def model_inference(
    crowd_status: CrowdStatus = stored_data,
    models_dir: str | Path = "models",
    model_name: str = "gpr",
) -> int | tuple[int, float]:
    # Get the numpy data from the stored data
    prod_data = parse_data_into_numpy(crowd_status)

    # Load the model
    with open(os.path.join(models_dir, f"{model_name}.pkl"), "rb") as f:
        model = pickle.load(f)

    # Perform inference
    if model_name == "gpr":
        pred, std = model.predict(prod_data, return_std=True)
        std = std[0]
    else:
        pred = model.predict(prod_data)

    pred = math.ceil(pred[0])

    return pred if std is None else (pred, std)


def parse_data_into_numpy(crowd_status: CrowdStatus = stored_data) -> np.ndarray:
    data = OrderedDict(crowd_status["data"])
    for device_id, data_from_device in data.items():
        wifi_col_idx = get_wifi_column_indices(
            device_id, top_n=TOP_N_APS, column_offset=0
        )
        bt_col_idx = get_bt_column_index(
            device_id, total_devices=TOTAL_DEVICES, top_n=TOP_N_APS, column_offset=0
        )
        bbox_col_idx = get_bbox_counts_column_index(
            device_id, total_devices=TOTAL_DEVICES, top_n=TOP_N_APS, column_offset=0
        )
        stored_data["numpy_data"][0, wifi_col_idx] = data_from_device["wifi_data"]
        stored_data["numpy_data"][0, bt_col_idx] = data_from_device["bt_data"]
        stored_data["numpy_data"][0, bbox_col_idx] = data_from_device["image"]

    return stored_data["numpy_data"]


def main():
    """
    The fog device will keep a copy of the data received from each
    edge device
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Subscriber")  # type: ignore
    client.on_message = on_message
    client.user_data_set(stored_data)
    client.connect(BROKER_IP, 1883)
    client.subscribe(TOPIC)
    client.loop_forever()


if __name__ == "__main__":
    main()
