from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression


def train_and_score_tabular1(X, Y, kf) -> list[float]:
    scores = []
    for train_index, test_index in kf.split(X):
        x_train, x_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = Y.iloc[train_index], Y.iloc[test_index]
        reg = make_pipeline(StandardScaler(), LinearRegression())
        reg.fit(x_train, y_train)
        scores.append(reg.score(x_test, y_test))
    return scores


def train_and_score_tabular2(args) -> list[float]:
    X, Y, kf, timestamps = args
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
