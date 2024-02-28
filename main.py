"""Stores the wifi signal strength and bluetoothctl output to a file.
"""

import os
import logging
import time
import subprocess
import re

from util.capture_image import take_picture


def main():
    """Main function to log wifi signal strength and bluetoothctl output to a file."""
    # Create a log file handler.
    file_handler = logging.FileHandler(
        os.path.join(os.path.dirname(__file__), "app.log")
    )

    start_time = time.time()
    end_time = start_time + 5 * 60

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
        logger.debug(f"Created directory: {output_directory}")

    # Take a picture first.
    print("Taking a picture in 5 seconds.")
    for i in range(5):
        time.sleep(1)
        print(f"{4 - i}")
    take_picture("./images/")
    print("Picture taken and saved.")

    # Run nmcli command to get the wifi signal strength.
    print("Attempting to get wifi signal strength")
    command = "sudo nmcli dev wifi rescan"
    subprocess.run(command, shell=True, check=True)

    command = r"sudo nmcli -g in-use,bssid,ssid,signal dev wifi list"
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        out = result.stdout.decode()

        # Filter only the SIT-WIFI signal strength with BSSID.
        r = re.compile(r"(:88\\:9C\\:AD\\:E1\\:22\\:6D:.*)").search(out)
        out = r.group()

        # Now get the signal strength from the filtered output.
        r = re.compile(r"(\*)?:((?>(?>[0-9A-F]{2})\\:){5}[0-9A-F]{2}):(.*):(\d+)").search(out)
        in_use, bssid, ssid, signal_strength = r.groups()
        logger.info("SIT-WIFI Signal Strength: %s", signal_strength)

        with open("wifi_signal_strength.txt", "a", encoding="utf-8") as f:
            f.write(f"{time.time()} - {ssid} - {signal_strength}\n")
            logger.debug("Signal strength written to wifi_signal_strength.txt")
    except ValueError:
        logger.error("No signal strength found for SIT-WIFI")

    # Run bluetoothctl command to get scan output
    print("Attempting to get bluetoothctl output")
    command = "bluetoothctl scan le & sleep 5; kill $!"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
    with open("btoutput.txt", "a", encoding="utf-8") as f2:
        f2.write(f"{time.time()} - Scan start\n")
        output = result.stdout.decode()
        for line in output.splitlines():
            f2.write(f"{time.time()} - {line}\n")
            if not line:
                break
        f2.write(f"{time.time()} - Scan end\n")
        logger.debug("Bluetoothctl output written to btoutput.txt")

    print("Program terminated.")

if __name__ == "__main__":
    main()
