"""Module for processing WiFi and Bluetooth signals.
"""

import logging
import re
import subprocess


def process_signals(
    wifi_stdout: list[tuple[str, str, int]], bt_stdout: list[str]
) -> tuple[list[int], int]:
    """Processes wifi and bluetooth outputs from :func:`get_bluetooth_data` and
    :func:`get_wifi_data`

    :param wifi_stdout: WiFi capture parsed stdout
    :type wifi_stdout: list[tuple[str, str, int]]
    :param bt_stdout: Bluetooth capture parsed stdout
    :type bt_stdout: list[str]
    :return: Tuple of WiFi and Bluetooth data
    :rtype: tuple[list[int], int]
    """
    wifi_data = parse_wifi_data(wifi_stdout)
    bt_data = parse_bt_data(bt_stdout)

    return wifi_data, bt_data


def get_bluetooth_data() -> list[str]:
    """Gets Bluetooth scan data using `bluetoothctl`.

    :return: Lines of stdout
    :rtype: list[str]
    """
    command = "bluetoothctl scan le & sleep 5; kill $!"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
    output = result.stdout.decode()
    output = output.splitlines()
    return output


def get_wifi_data(ap: str = "SIT-POLY") -> list[str]:
    """Retrieves the wireless AP signal strengths using `nmcli` that matches the AP SSID.

    :param ap: AP SSID to filter for
    :type ap: str
    :return: Top $N$ list of bssid, ssid, and signal strength results.
    :rtype: list[tuple[str, str, int]]
    """
    command = "sudo nmcli dev wifi rescan"
    subprocess.run(command, shell=True, check=True)
    command = rf"sudo nmcli -g in-use,bssid,ssid,signal dev wifi list | grep {ap}"
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    return result.stdout.decode()


def parse_bt_data(bt_stdout: list[str]) -> int:
    """Parses bluetooth data retrieved from :func:`get_bluetooth_data`

    :param bt_stdout: Bluetooth data from :func:`get_bluetooth_data`
    :type bt_stdout: list[str]
    :return: Number of bluetooth devices detected
    :rtype: int
    """
    r = re.compile(r"Device (\S+)")
    unique_bt_devices = []
    for line in bt_stdout:
        matches = re.findall(r, line)
        if matches:
            unique_bt_devices.append(*matches)

    num_devices = len(set(unique_bt_devices))
    return num_devices


def parse_wifi_data(
    wifi_stdout: list[tuple[str, str, int]], top_n: int = 5
) -> list[int]:
    """Parses wifi data output from :func:`get_wifi_data`

    :param wifi_stdout: WiFi data output from :func:`get_wifi_data`
    :type wifi_stdout: list[tuple[str, str, int]]
    :param top_n: Number of results to provide, -1 for all, defaults to 5
    :type top_n: int, optional
    :return: Signal strengths of APs
    :rtype: list[int]
    """
    logger = logging.getLogger()
    res = []
    try:
        pattern = re.compile(r"(\*)?:((?:(?:[0-9A-F]{2})\\:){5}[0-9A-F]{2}):(.*):(\d+)")
        for ap in wifi_stdout:
            try:
                r = pattern.search(ap)
                _, bssid, ssid, signal_strength = r.groups()
                signal_strength = int(signal_strength)
                res.append((bssid, ssid, signal_strength))
            except AttributeError:
                logger.error("Regex failed to match: %s", ap)
    except ValueError:
        logger.error("No signal strength found for SIT-WIFI")

    res = sorted(res, key=lambda x: x[2], reverse=True)
    if len(res) < top_n:
        for _ in range(len(res), top_n):
            res.append(["", "", 0])

    if top_n < 0:
        return res

    return res[:top_n]


def get_and_parse_data(demo_env: bool = False) -> tuple[list[int], int]:
    """Gets and parses WiFi and Bluetooth data.

    :param demo_env: In demo environment, it loads the data from file, defaults to False
    :type demo_env: bool, optional
    :return: Tuple of WiFi and Bluetooth data from :func:`process_signals`
    :rtype: tuple[list[int], int]
    """
    if demo_env:
        # TODO(chris): implement data loading from file
        return None
    wifi_data = get_wifi_data()
    bt_data = get_bluetooth_data()
    return process_signals(wifi_data, bt_data)
