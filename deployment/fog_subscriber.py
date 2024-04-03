import paho.mqtt.client as mqtt
from config import BROKER_IP, TOPIC, CLIENT_RETRIEVAL_TOPIC

import cv2
import json
import time
import base64
import requests
import numpy as np
import pandas as pd
from io import StringIO

def decode_img(payload):

    binary_data = base64.b64decode(payload)
    np_data = np.frombuffer(binary_data, np.uint8)
    decoded_img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    return decoded_img

def on_message(client, userdata, message):

    received_data = json.loads(message.payload)
    device_id = received_data["device_id"]

    print(f"Received data from device: {device_id}")

    for data_type in stored_data.keys():
        if device_id not in stored_data[data_type].keys():

            if data_type == "images":
                image = decode_img(received_data["image"])
                stored_data[data_type][device_id] = image
                # cv2.imwrite(f"img_{received_data['timestamp']}.jpg", image)
            
            elif data_type == "wifi":
                wifi_data = received_data["wifi_strength"]
                stored_data[data_type][device_id] = wifi_data

            elif data_type == "bt":
                bt_data = received_data["bt_output"]
                stored_data[data_type][device_id] = bt_data

    current_crowd_status = model_inference()
    requests.post(
        "http://localhost:8000/api/update_crowd_status", 
        json = {"status": current_crowd_status, "timestamp": time.time()}
        )
    print("data sent")

def model_inference():
    
    # Get list of images
    images_list = list(stored_data["images"].values())

    # Get list of wifi data
    wifi_data_list = [pd.read_json(StringIO(df), orient="split") for df in stored_data["wifi"].values()]
    wifi_data_agg = pd.concat(wifi_data_list)

    # Get list of bluetooth data
    bt_data_list = [pd.read_json(StringIO(df), orient="split") for df in stored_data["bt"].values()]
    bt_data_agg = pd.concat(bt_data_list)

    # print(images_list)
    # print(wifi_data_agg)
    # print(bt_data_agg)

    # Perform model inference here

    return 1 # Dummy return value

if __name__ == "__main__":

    '''
        The fog device will keep a copy of the data received from each 
        edge device
    '''
    global stored_data

    stored_data = {
        "images": {},
        "wifi": {},
        "bt": {}
    }
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Subscriber")
    client.on_message = on_message
    client.connect(BROKER_IP, 1883)
    client.subscribe(TOPIC)
    client.loop_forever()
