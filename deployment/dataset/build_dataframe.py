import os
import re
from typing import Optional

import numpy as np
import pandas as pd
from tqdm.auto import tqdm


def convert_timestamps_to_datetime(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    fmt: str = "%Y%m%d%H%M%S",
    preprocess: bool = True,
) -> pd.DataFrame:
    """Converts timestamps in the DataFrame to datetime objects

    :param df: DataFrame containing timestamps
    :type df: pd.DataFrame
    :param timestamp_col: Timestamp column name, defaults to "timestamp"
    :type timestamp_col: str, optional
    :param fmt: Format string, defaults to "%Y%m%d%H%M%S"
    :type fmt: str, optional
    :param preprocess: Converts column type if pandas did not automatically infer it, defaults to True
    :type preprocess: bool, optional
    :return: DataFrame with converted timestamps
    :rtype: pd.DataFrame
    """
    if preprocess:
        df[timestamp_col] = df[timestamp_col].apply(int).apply(str)
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], format=fmt)
    return df


def get_wifi_dataframe(
    raw_data_path: os.PathLike | str,
    columns: list[str] = None,
    collector_names: list[str] = None,
) -> pd.DataFrame:
    """Get WiFi DataFrame

    :param raw_data_path: Path to the raw data
    :type raw_data_path: os.PathLike | str
    :param columns: Column names, defaults to None
    :type columns: list[str], optional
    :param collector_names: Collector names in the raw data path, defaults to None
    :type collector_names: list[str], optional
    :return: DataFrame containing WiFi data
    :rtype: pd.DataFrame
    """

    assert os.path.exists(raw_data_path), f"{raw_data_path} does not exist."

    columns = (
        columns
        if columns is not None
        else ["timestamp", "bssid", "ssid", "signal_strength", "device_idx"]
    )

    collector_names = (
        collector_names
        if collector_names is not None
        else ["bryan", "chris", "jiayu", "jurgen"]
    )

    super_df = pd.DataFrame(columns=columns)
    for root, _, files in tqdm(os.walk(raw_data_path)):
        name = root.rsplit("/", 1)[-1]
        for file in files:
            if not file.endswith(".csv"):
                continue

            device_idx = collector_names.index(name)
            df = pd.read_csv(os.path.join(root, file), header=None, names=columns)
            df["device_idx"] = device_idx
            super_df = pd.concat([super_df, df], ignore_index=True)

    # Convert timestamps to datetime objects
    super_df = convert_timestamps_to_datetime(super_df)
    super_df["signal_strength"] = super_df["signal_strength"].apply(int)

    return super_df


def get_bluetooth_dataframe(
    raw_data_path: os.PathLike | str,
    columns: list[str] = None,
    collector_names: list[str] = None,
) -> pd.DataFrame:
    """Get Bluetooth DataFrame

    :param raw_data_path: Path to the raw data
    :type raw_data_path: os.PathLike | str
    :param columns: Column names, defaults to None
    :type columns: list[str], optional
    :param collector_names: Collector names in the raw data path, defaults to None
    :type collector_names: list[str], optional
    :return: DataFrame containing Bluetooth data
    :rtype: pd.DataFrame
    """
    assert os.path.exists(raw_data_path), f"{raw_data_path} does not exist."

    all_dfs = []
    pattern = r"(\d{14}) - .*?Device (\S+)"
    columns = (
        columns
        if columns is not None
        else ["timestamp", "bt_device_count", "device_idx"]
    )
    collector_names = (
        collector_names
        if collector_names is not None
        else ["bryan", "chris", "jiayu", "jurgen"]
    )

    for root, _, files in tqdm(os.walk(raw_data_path)):
        name = root.rsplit("/", 1)[-1]
        for file in files:
            if not file.endswith(".txt"):
                continue

            device_idx = collector_names.index(name)
            unique_bt_devices = {}
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                matches = re.findall(pattern, line)
                for timestamp, bt_device_id in matches:
                    if timestamp not in unique_bt_devices:
                        unique_bt_devices[timestamp] = {bt_device_id}
                    else:
                        unique_bt_devices[timestamp].add(bt_device_id)

            df = pd.DataFrame(
                [
                    (timestamp, len(devices), device_idx)
                    for timestamp, devices in unique_bt_devices.items()
                ],
                columns=columns,
            )
            all_dfs.append(df)

    bluetooth_df = pd.concat(all_dfs, ignore_index=True)
    bluetooth_df = convert_timestamps_to_datetime(bluetooth_df)
    return bluetooth_df


def get_population_count_df(
    csv_path: os.PathLike | str, columns: list[str] = None
) -> pd.DataFrame:
    """Get population count DataFrame

    :param csv_path: Path to the CSV file
    :type csv_path: os.PathLike | str
    :param columns: Column names, defaults to None
    :type columns: list[str], optional
    :return: DataFrame containing population count
    :rtype: pd.DataFrame
    """
    assert os.path.exists(csv_path), f"{csv_path} does not exist."
    if columns:
        df = pd.read_csv(csv_path, names=columns, header=1)
    else:
        df = pd.read_csv(csv_path)
    df = convert_timestamps_to_datetime(
        df, df.columns[0], "%d/%m/%Y %H:%M:%S", preprocess=False
    )
    return df


def get_bbox_df(
    csv_path: os.PathLike | str, columns: Optional[list[str]] = None
) -> pd.DataFrame:
    """Get bounding box counts DataFrame

    :param csv_path: Path to the CSV file
    :type csv_path: os.PathLike | str
    :param columns: Column names, defaults to None
    :type columns: list[str], optional
    :return: DataFrame containing bounding box counts
    :rtype: pd.DataFrame
    """
    assert os.path.exists(csv_path), f"{csv_path} does not exist."
    if columns:
        df = pd.read_csv(csv_path, names=columns, header=1)
    else:
        df = pd.read_csv(csv_path)
    df = convert_timestamps_to_datetime(df, df.columns[0])
    return df


def get_nearest_timestamp(
    x: pd.Timestamp,
    ref_timestamps: (
        np.ndarray[pd.Timestamp | np.datetime64] | pd.Series | list[pd.Timestamp]
    ),
) -> pd.Timestamp:
    """Returns the nearest timestamp in ref_timestamps to x

    :param x: Timestamp to find nearest reference timestamp to
    :type x: pd.Timestamp
    :param ref_timestamps: Series of reference timestamps
    :type ref_timestamps: np.ndarray[pd.Timestamp  |  np.datetime64] | pd.Series | list[pd.Timestamp]
    :return: Nearest timestamp in ref_timestamps to x
    :rtype: pd.Timestamp
    """
    return ref_timestamps[np.argmin(np.abs(ref_timestamps - x))]


def get_top_N_wifi_aps_only(df: pd.DataFrame, N: int = 5) -> pd.DataFrame:
    """Gets the top N wifi ap signal strengths, grouped by timestamp and device_idx

    :param df: DataFrame containing wifi data
    :type df: pd.DataFrame
    :param N: Number of top AP signal strengths to return, defaults to 5
    :type N: int, optional
    :return: DataFrame containing top N wifi ap signal strengths, grouped by timestamp and device_idx
    :rtype: pd.DataFrame
    """
    groupedby_df = df.groupby(["timestamp", "device_idx"]).apply(
        lambda x: x.nlargest(N, "signal_strength")
    )

    reindexed_wifi_df = groupedby_df.set_index(
        ["timestamp", "device_idx", "signal_strength"]
    )
    reindexed_wifi_df = (
        reindexed_wifi_df.groupby(["timestamp", "device_idx"]).cumcount() + 1
    )
    reindexed_wifi_df = reindexed_wifi_df.reset_index()
    reindexed_wifi_df.rename(columns={0: "rank"}, inplace=True)
    return reindexed_wifi_df


def pivot_tables(
    wifi_df: pd.DataFrame, bt_df: pd.DataFrame, bbox_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Pivot the three dataframes to tabular form.

    :param wifi_df: Wifi DataFrame with top N APs
    :type wifi_df: pd.DataFrame
    :param bt_df: Bluetooth DataFrame
    :type bt_df: pd.DataFrame
    :param bbox_df: Bounding Box counts DataFrame
    :type bbox_df: pd.DataFrame
    :return: Pivoted DataFrames
    :rtype: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
    """

    wifi_tabular = wifi_df.pivot_table(
        index=["timestamp"],
        columns=["device_idx", "rank"],
        values=["signal_strength"],
        observed=True,
        fill_value=0,
        aggfunc="mean",
        dropna=False,
    )
    wifi_tabular = pd.DataFrame(wifi_tabular.to_records())

    bt_tabular = bt_df.pivot_table(
        index=["timestamp"],
        columns=["device_idx"],
        values=["bt_device_count"],
        observed=True,
        fill_value=0,
        aggfunc="mean",
        dropna=False,
    )
    bt_tabular = pd.DataFrame(bt_tabular.to_records())

    bbox_tabular = bbox_df.pivot_table(
        index=["timestamp"],
        columns=["device_idx"],
        values=["bbox_count"],
        observed=True,
        fill_value=0,
        aggfunc="max",
        dropna=False,
    )
    bbox_tabular = pd.DataFrame(bbox_tabular.to_records())

    return wifi_tabular, bt_tabular, bbox_tabular


def merge_dfs(
    wifi_tabular: pd.DataFrame,
    bt_tabular: pd.DataFrame,
    bbox_tabular: pd.DataFrame,
    pop_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge the 4 DataFrames from :func:`pivot_tables`

    :param wifi_tabular: Tabular wifi DataFrame
    :type wifi_tabular: pd.DataFrame
    :param bt_tabular: Tabular bluetooth DataFrame
    :type bt_tabular: pd.DataFrame
    :param bbox_tabular: Tabular bounding boxes DataFrame
    :type bbox_tabular: pd.DataFrame
    :param pop_df: Population count DataFrame
    :type pop_df: pd.DataFrame
    :return: Combined DataFrame
    :rtype: pd.DataFrame
    """

    combined_tabular = pd.merge(wifi_tabular, bt_tabular, how="left", on="timestamp")
    combined_tabular = pd.merge(
        combined_tabular, bbox_tabular, how="left", on="timestamp"
    )
    combined_tabular = pd.merge(combined_tabular, pop_df, how="left", on="timestamp")

    # Remove NaNs in the population count
    combined_tabular = combined_tabular[combined_tabular["count"].notna()]

    # Fill NaNs remaining
    combined_tabular = combined_tabular.fillna(0)

    return combined_tabular
