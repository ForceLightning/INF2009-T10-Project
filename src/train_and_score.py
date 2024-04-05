"""Train and score linear regression models using tabular data.
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


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
    for train_timestamp_idx, test_timestamp_idx in kf.split(timestamps):
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
