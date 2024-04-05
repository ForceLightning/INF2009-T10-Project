"""Module for processing WiFi and Bluetooth signals.
"""

import logging
import math
from pathlib import Path
import re
import subprocess
from typing import Sequence

import pandas as pd

from deployment.config import DEVICE_IDX, TOTAL_DEVICES, TOP_N_APS


def process_signals(
    wifi_stdout: Sequence[str], bt_stdout: Sequence[str]
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
    :return: Top :math:`N` list of bssid, ssid, and signal strength results.
    :rtype: list[tuple[str, str, int]]
    """
    command = "sudo nmcli dev wifi rescan"
    subprocess.run(command, shell=True, check=True)
    command = rf"sudo nmcli -g in-use,bssid,ssid,signal dev wifi list | grep {ap}"
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    return result.stdout.decode().splitlines()


def parse_bt_data(bt_stdout: Sequence[str]) -> int:
    """Parses bluetooth data retrieved from :func:`get_bluetooth_data`

    :param bt_stdout: Bluetooth data from :func:`get_bluetooth_data`
    :type bt_stdout: Sequence[str]
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


def parse_wifi_data(wifi_stdout: Sequence[str], top_n: int = 5) -> list[int]:
    """Parses wifi data output from :func:`get_wifi_data`

    :param wifi_stdout: WiFi data output from :func:`get_wifi_data`
    :type wifi_stdout: Sequence[str]
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
                if not r:
                    continue
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


def get_and_parse_data(
    demo_env: bool = False, device_idx: int = 0, **kwargs
) -> tuple[list[int], int]:
    """Gets and parses WiFi and Bluetooth data.

    :param demo_env: In demo environment, it loads the data from file, defaults to False
    :type demo_env: bool, optional
    :param device_idx: Device index or id, defaults to 0
    :type device_idx: int, optional
    :param kwargs: Additional keyword arguments with the following keys:
        - koufu_csv_path: Path to the koufu csv file
        - total_devices: Total number of devices
        - top_n: Number of top APs to consider
    :type kwargs: dict
    :return: Tuple of WiFi and Bluetooth data from :func:`process_signals`
    :rtype: tuple[list[int], int]
    """
    if demo_env:
        return get_demo_data(device_idx, **kwargs, index=-1)
    wifi_data = get_wifi_data()
    bt_data = get_bluetooth_data()
    return process_signals(wifi_data, bt_data)


def get_demo_data(
    device_idx: int,
    koufu_csv_path: str | Path,
    total_devices: int = 4,
    top_n: int = 5,
    index: int = 0,
) -> tuple[list[int], int]:
    """Gets the demo data from the koufu csv file.

    :param device_idx: Device index or id
    :type device_idx: int
    :param koufu_csv_path: CSV file path
    :type koufu_csv_path: str | Path
    :param total_devices: Total number of devices, defaults to 4
    :type total_devices: int, optional
    :param top_n: Top :math:`N` APs in the file, defaults to 5
    :type top_n: int, optional
    :param index: Index of the row to retrieve, defaults to 0
    :type index: int, optional
    :return: Tuple of WiFi and Bluetooth data
    :rtype: tuple[list[int], int]
    """

    # Load the data from the csv file
    df = pd.read_csv(koufu_csv_path)

    # Wifi column indices
    wifi_col_idx = get_wifi_column_indices(device_idx, top_n=top_n)

    # Add the bluetooth column index
    bt_col_idx = get_bt_column_index(
        device_idx, total_devices=total_devices, top_n=top_n
    )

    # Add the bounding box column index
    # col_idx.append(1 + total_devices * (top_n + 1) + device_idx)

    return df.iloc[index, wifi_col_idx].astype(int).tolist(), math.ceil(
        df.iloc[index, bt_col_idx]
    )  # type: ignore


def get_wifi_column_indices(
    device_idx: int = DEVICE_IDX, column_offset: int = 1, top_n: int = TOP_N_APS
) -> list[int]:
    r"""Gets the column indices of the WiFi signal strengths.

    .. math::
        \texttt{column_indices} = \left[ \texttt{column_offset} + \text{top}_n \times \texttt{device_idx} + i \right]_{i=0}^{\text{top}_n}

    :param device_idx: Device index or id
    :type device_idx: int
    :param column_offset: Offset from the 0th indexed column usually if a
        timestamp column is the index, defaults to 1
    :type column_offset: int, optional
    :param top_n: Top :math:`N` APs used for training and inference, defaults to 5
    :type top_n: int, optional
    :return: List of column indices
    :rtype: list[int]
    """
    return [column_offset + top_n * device_idx + i for i in range(top_n)]


def get_bt_column_index(
    device_idx: int = DEVICE_IDX,
    column_offset: int = 1,
    total_devices: int = TOTAL_DEVICES,
    top_n: int = TOP_N_APS,
) -> int:
    r"""Gets the column index for the specified device for BT data.

    .. math::
        \texttt{column_index} = \text{column_offset} + \texttt{total_devices} \times \left( \text{top}_n + 1 \right) + \texttt{device_idx}

    :param device_idx: Device index or id, defaults to `DEVICE_IDX`
    :type device_idx: int
    :param column_offset: Offset from the 0th indexed column usually if a
        timestamp column is used as the index, defaults to 1
    :type column_offset: int, optional
    :param total_devices: Total number of edge devices, defaults to `TOTAL_DEVICES`
    :type total_devices: int, optional
    :param top_n: Top :math:`N` WiFi APs used for training and inference,
        defaults to `TOP_N_APS`
    :type top_n: int, optional
    :return: Column index for the BT data
    :rtype: int
    """
    return column_offset + total_devices * top_n + device_idx


def get_bbox_counts_column_index(
    device_idx: int = DEVICE_IDX,
    column_offset: int = 1,
    total_devices: int = TOTAL_DEVICES,
    top_n: int = TOP_N_APS,
) -> int:
    r"""Gets the column index for the bounding box counts for the specified device.

    .. math::
        \texttt{column_index} = \text{column_offset} + \texttt{total_devices} \times \left( \text{top}_n + 1 \right) + \texttt{device_idx}

    :param device_idx: Device index or id, defaults to `DEVICE_IDX`
    :type device_idx: int, optional
    :param column_offset: Offset from the 0th indexed column usually if a
        timestamp column is used as the index, defaults to 1
    :type column_offset: int, optional
    :param total_devices: Total number of edge devices, defaults to `TOTAL_DEVICES`
    :type total_devices: int, optional
    :param top_n: Top :math:`N` WiFi APs used for training and inference,
        defaults to `TOP_N_APS`
    :type top_n: int, optional
    :return: Column index for the bounding box counts
    :rtype: int
    """
    return column_offset + total_devices * (top_n + 1) + device_idx
