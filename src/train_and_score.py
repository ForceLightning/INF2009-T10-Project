"""Train and score regression models using collected data.
"""

import argparse
import os
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.base import RegressorMixin
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, DotProduct, WhiteKernel
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from dataset.build_dataframe import (
    get_bbox_df,
    get_bluetooth_dataframe,
    get_nearest_timestamp,
    get_population_count_df,
    get_top_N_wifi_aps_only,
    get_wifi_dataframe,
    merge_dfs,
    pivot_tables,
)
from deployment.config import TOP_N_APS


def train_and_score_tabular1(
    X: pd.DataFrame, y: pd.DataFrame, kf: KFold
) -> list[float]:
    """Train and score a linear regression model using tabular data.

    :param X: Input features
    :type X: pd.DataFrame
    :param y: Target variable
    :type y: pd.DataFrame
    :param kf: KFold object
    :type kf: KFold
    :return: List of scores
    :rtype: list[float]
    """
    scores = []
    for train_index, test_index in kf.split(X):
        x_train, x_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        reg = make_pipeline(StandardScaler(), LinearRegression())
        reg.fit(x_train, y_train)
        scores.append(reg.score(x_test, y_test))
    return scores


def train_and_score_tabular2(
    X: pd.DataFrame, Y: pd.DataFrame, kf: KFold, timestamps: pd.Series
) -> list[float]:
    """Trains and scores a linear regression model using tabular data.

    :param X: Input features
    :type X: pd.DataFrame
    :param Y: Target variable
    :type Y: pd.DataFrame
    :param kf: KFold object
    :type kf: KFold
    :param timestamps: Timestamps for splitting the data
    :type timestamps: pd.Series
    :return: List of scores
    :rtype: list[float]
    """

    scores = []
    for train_timestamp_idx, test_timestamp_idx in kf.split(timestamps):  # type: ignore
        train_timestamp = timestamps[train_timestamp_idx]
        test_timestamp = timestamps[test_timestamp_idx]
        x_train, y_train = (
            X.loc[X["binned_timestamp"].isin(train_timestamp)],
            Y.loc[Y["binned_timestamp"].isin(train_timestamp)],
        )
        x_test, y_test = (
            X.loc[X["binned_timestamp"].isin(test_timestamp)],
            Y.loc[Y["binned_timestamp"].isin(test_timestamp)],
        )
        x_train.drop(columns="binned_timestamp", inplace=True)
        x_test.drop(columns="binned_timestamp", inplace=True)
        y_train.drop(columns="binned_timestamp", inplace=True)
        y_test.drop(columns="binned_timestamp", inplace=True)
        reg = make_pipeline(StandardScaler(), LinearRegression())
        reg.fit(x_train, y_train)
        scores.append(reg.score(x_test, y_test))
    return scores


def fit_model_with_koufu_as_test(
    model: RegressorMixin,
    X: np.ndarray,
    y: np.ndarray,
    koufu_idx: int = 14,
) -> RegressorMixin:
    """Trains a model with the koufu data as the test set (optional).

    :param model: Model to train, must be a regressor
    :type model: RegressorMixin
    :param X: Input features.
    :type X: np.ndarray
    :param y: Target variable.
    :type y: np.ndarray
    :param koufu_idx: Start index of koufu data (or any test data), defaults to 14
    :type koufu_idx: int, optional
    :return: Trained model.
    :rtype: RegressorMixin
    """
    if koufu_idx >= len(X):
        koufu_idx = len(X) - 1
    X_train, X_test = X[0:koufu_idx], X[koufu_idx:]
    y_train, y_test = y[0:koufu_idx], y[koufu_idx:]
    model.fit(X_train, y_train)  # type: ignore
    print(f"Model score: {model.score(X_test, y_test)}")
    return model


def load_data(
    raw_data_path: str | os.PathLike | Path,
    bbox_csv_path: str | os.PathLike | Path,
    pop_count_csv_path: str | os.PathLike | Path,
    bbox_cols: Optional[list] = None,
    pop_count_cols: Optional[list] = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads the data from the specified paths and returns the DataFrames.

    :param raw_data_path: Path to raw collected data
    :type raw_data_path: str | os.PathLike | Path
    :param bbox_csv_path: Path to the bounding box inference results
    :type bbox_csv_path: str | os.PathLike | Path
    :param pop_count_csv_path: Population count CSV path
    :type pop_count_csv_path: str | os.PathLike | Path
    :param bbox_cols: Bounding Box DF desired column names, defaults to None
    :type bbox_cols: Optional[list], optional
    :param pop_count_cols: Population count DF desired column names, defaults to None
    :type pop_count_cols: Optional[list], optional
    :return: WiFi, Bluetooth, Bounding Box, and Population Count DataFrames
    :rtype: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
    """

    # Defaults
    bbox_cols = bbox_cols if bbox_cols else ["timestamp", "device_idx", "bbox_count"]
    pop_count_cols = (
        pop_count_cols if pop_count_cols else ["timestamp", "count", "comment"]
    )

    # Load DataFrames
    wifi_df = get_wifi_dataframe(raw_data_path)
    bt_df = get_bluetooth_dataframe(raw_data_path)
    bbox_df = get_bbox_df(bbox_csv_path, bbox_cols)
    population_count_df = get_population_count_df(pop_count_csv_path, pop_count_cols)

    for df in [wifi_df, bt_df, bbox_df]:
        df["timestamp"] = df["timestamp"].apply(
            lambda x: get_nearest_timestamp(x, population_count_df["timestamp"])
        )

    return wifi_df, bt_df, bbox_df, population_count_df


def main(
    top_n_aps: int = TOP_N_APS, model_out_dir: Optional[str | os.PathLike | Path] = None
):
    """Runs the main training and scoring pipeline.

    :param top_n_aps: Top :math:`N` WiFi APs to keep for training, defaults to TOP_N_APS
    :type top_n_aps: int, optional
    :param model_out_dir: Directory to save the model, defaults to None
    :type model_out_dir: Optional[str | os.PathLike | Path], optional
    """
    # Set paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    deployment_root = os.path.abspath(os.path.join(project_root, "src", "deployment"))
    raw_data_path = os.path.join(project_root, "data", "raw_data")
    bbox_csv_path = os.path.join(project_root, "data", "bbox_results.csv")
    pop_count_csv_path = os.path.join(project_root, "data", "manual_counts.csv")

    # Get DataFrames
    wifi_df, bt_df, bbox_df, population_count_df = load_data(
        raw_data_path, bbox_csv_path, pop_count_csv_path
    )

    # Combined DataFrames into tabular format
    top_n_wifi_aps = get_top_N_wifi_aps_only(wifi_df, top_n_aps)
    wifi_tabular, bt_tabular, bbox_tabular = pivot_tables(
        top_n_wifi_aps, bt_df, bbox_df
    )
    combined_tabular = merge_dfs(
        wifi_tabular, bt_tabular, bbox_tabular, population_count_df
    )

    # Set X and y
    X = combined_tabular.drop(columns=["timestamp", "count", "comment"]).to_numpy()
    y = combined_tabular["count"].to_numpy()

    # Train the model
    gpr = GaussianProcessRegressor(
        kernel=(DotProduct() + RBF() + WhiteKernel()), random_state=42
    )
    gpr = fit_model_with_koufu_as_test(gpr, X, y)

    # Check the model output directory
    if model_out_dir is None:
        model_out_dir = os.path.join(deployment_root, "models")

    # Create the directory if it does not exist
    if not os.path.exists(model_out_dir):
        os.makedirs(model_out_dir)

    # Pickle and dump the model
    with open(os.path.join(model_out_dir, "gpr.pkl"), "wb") as f:
        pickle.dump(gpr, f)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--top_n_aps", type=int, default=TOP_N_APS)
    args.add_argument("--model_out_dir", type=str, default=None)
    main(**vars(args.parse_args()))
