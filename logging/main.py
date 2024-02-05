"""Stores the wifi signal strength and bluetoothctl output to a file.
"""

import os
import logging
import time
import subprocess


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

    while time.time() < end_time:
        # Run nmcli command to get the wifi signal strength.
        print("Attempting to get wifi signal strength")
        command = "sudo nmcli dev wifi rescan"
        subprocess.run(command, shell=True, check=True)

        command = "sudo nmcli -g ssid,signal dev wifi list | grep SIT-WIFI"
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        try:
            ssid, signal_strength = result.stdout.decode().strip().split(":")
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

if __name__ == "__main__":
    main()
