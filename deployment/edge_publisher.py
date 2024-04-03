import paho.mqtt.client as mqtt
import time
import json
import uuid
from config import PUBLISHER_INTERVAL, BROKER_IP, TOPIC
from data_collection import capture_image, get_wifi_strength, get_btoutput
from preprocessing import process_wifi_data, process_bt_data

def retrieve_data(device_id) -> dict:
    
    # Capture an image from the camera
    image_capture = capture_image()

    # Get the wifi signal strength
    wifi_strength = get_wifi_strength()
    wifi_processed = process_wifi_data(wifi_strength).to_json(orient="split")

    # Get the bluetooth output
    bt_output = get_btoutput()
    bt_processed = process_bt_data(bt_output).to_json(orient="split")

    return json.dumps({"image": image_capture, 
                       "timestamp": time.time(), 
                       "wifi_strength": wifi_processed,
                       "bt_output": bt_processed,
                       "device_id": device_id})

if __name__ == "__main__":

    device_id = str(uuid.uuid1())

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Publisher")
    client.connect(BROKER_IP, 1883)

    while True:

        data = retrieve_data(device_id)

        client.publish(TOPIC, data)
        time.sleep(PUBLISHER_INTERVAL)
