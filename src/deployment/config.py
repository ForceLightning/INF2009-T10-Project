"""Loads environment variables and sets global variables for the publisher.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Device ID set by environment variables
DEVICE_IDX = os.getenv("DEVICE_IDX")
DEVICE_IDX = int(DEVICE_IDX) if DEVICE_IDX else -1

# Whether to use demo data
USE_DEMO_DATA = os.getenv("USE_DEMO_DATA")
USE_DEMO_DATA = USE_DEMO_DATA == "True"

# Whether to return the image or not
RETURN_IMAGE = os.getenv("RETURN_IMAGE")
RETURN_IMAGE = RETURN_IMAGE == "True"

# Interval between each data retrieval
PUBLISHER_INTERVAL = os.getenv("PUBLISHER_INTERVAL")
PUBLISHER_INTERVAL = int(PUBLISHER_INTERVAL) if PUBLISHER_INTERVAL else 50

# IP address of the MQTT broker
BROKER_IP = os.getenv("BROKER_IP")
BROKER_IP = BROKER_IP if BROKER_IP else "localhost"

# Topic to publish collected data to
TOPIC = os.getenv("TOPIC")
TOPIC = TOPIC if TOPIC else "data"

# Topic to retrieve data from the client devices
CLIENT_RETRIEVAL_TOPIC = os.getenv("CLIENT_RETRIEVAL_TOPIC")
CLIENT_RETRIEVAL_TOPIC = (
    CLIENT_RETRIEVAL_TOPIC if CLIENT_RETRIEVAL_TOPIC else "client_data"
)

if __name__ == "__main__":
    print(
        f"DEVICE_IDX: {DEVICE_IDX}, {type(DEVICE_IDX)}",
        f"USE_DEMO_DATA: {USE_DEMO_DATA}, {type(USE_DEMO_DATA)}",
        f"RETURN_IMAGE: {RETURN_IMAGE}, {type(RETURN_IMAGE)}",
        f"PUBLISHER_INTERVAL: {PUBLISHER_INTERVAL}, {type(PUBLISHER_INTERVAL)}",
        f"BROKER_IP: {BROKER_IP}, {type(BROKER_IP)}",
        f"TOPIC: {TOPIC}, {type(TOPIC)}",
        f"CLIENT_RETRIEVAL_TOPIC: {CLIENT_RETRIEVAL_TOPIC}, {type(CLIENT_RETRIEVAL_TOPIC)}",
    )
