"""Stores the wifi signal strength and bluetoothctl output to a file.
"""

import os
import logging
import time
import subprocess
import re
import json

from dotenv import load_dotenv

from util.capture_image import take_picture
from util.people_detection import detect, get_people_count
from util.wifi_bt_processing import get_and_parse_data

load_dotenv()  # Load environment variables

DEVICE_IDX = os.getenv("DEVICE_IDX")
DEVICE_IDX = DEVICE_IDX if DEVICE_IDX else -1
USE_DEMO_DATA = os.getenv("USE_DEMO_DATA") is not None


def main():
    """Main function to log wifi signal strength and bluetoothctl output to a file."""
    # Create a log file handler.
    file_handler = logging.FileHandler(
        os.path.join(os.path.dirname(__file__), "app.log")
    )

    # Create a formatter and set the formatter for the handler.
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Create a logger and set the level.
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Add the handler to the logger.
    logger.addHandler(file_handler)

    # Check if image out directory exists
    output_directory = "images"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        logger.debug("Created directory: %s", output_directory)

    # Take a picture first.
    print("Taking a picture in 5 seconds.")
    for i in range(5):
        time.sleep(1)
        print(f"{4 - i}")
    bbox_count = get_people_count(detect(take_picture()))
    print(f"Number of people detected: {bbox_count}")
    # print("Picture taken and saved.")

    # Run nmcli command to get the wifi signal strength.
    print("Attempting to get wifi signal strength")
    command = "sudo nmcli dev wifi rescan"
    subprocess.run(command, shell=True, check=True)

    command = r"sudo nmcli -g in-use,bssid,ssid,signal dev wifi list | grep SIT-POLY"
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        out = result.stdout.decode()
        aps = out.split("\n")

        for ap in aps:
            try:
                # Now get the signal strength from the filtered output.
                print(ap)
                r = re.compile(
                    r"(\*)?:((?:(?:[0-9A-F]{2})\\:){5}[0-9A-F]{2}):(.*):(\d+)"
                ).search(ap)
                if not r:
                    continue
                _, bssid, ssid, signal_strength = r.groups()
                logger.info("SIT-WIFI %s Signal Strength: %s", bssid, signal_strength)

                with open("wifi_signal_strength.csv", "a", encoding="utf-8") as f:
                    bssid = bssid.replace("\\", "")
                    timenow = time.strftime("%Y%m%d%H%M%S")
                    f.write(f"{timenow},{bssid},{ssid},{signal_strength}\n")
                    logger.debug("Signal strength written to wifi_signal_strength.txt")
            except AttributeError:
                logger.error("Regex failed to match for SIT-WIFI %s", ap)
    except ValueError:
        logger.error("No signal strength found for SIT-WIFI")

    # Run bluetoothctl command to get scan output
    print("Attempting to get bluetoothctl output")
    command = "bluetoothctl scan le & sleep 5; kill $!"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
    with open("btoutput.txt", "a", encoding="utf-8") as f2:
        timenow = time.strftime("%Y%m%d%H%M%S")
        f2.write(f"{timenow} - Scan start\n")
        output = result.stdout.decode()
        for line in output.splitlines():
            timenow = time.strftime("%Y%m%d%H%M%S")
            f2.write(f"{timenow} - {line}\n")
            if not line:
                break
        timenow = time.strftime("%Y%m%d%H%M%S")
        f2.write(f"{timenow} - Scan end\n")
        logger.debug("Bluetoothctl output written to btoutput.txt")

    # Data formatting
    data = get_and_parse_data(USE_DEMO_DATA)
    if data:
        wifi_data, bt_data = data
    data_dict = {
        "wifi": wifi_data,
        "bluetooth": bt_data,
    }
    data_dict["bbox_count"] = bbox_count

    # Send data to the fog
    print("Sending data to the fog")
    payload = json.dumps(data_dict)

    print("Program terminated.")


if __name__ == "__main__":
    main()
