import pandas as pd
from sklearn.feature_extraction import FeatureHasher
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.compose import ColumnTransformer

HASH_DIM = 2**18


def _add_temporal(df: pd.DataFrame) -> pd.DataFrame:
    if "timestamp" in df.columns and "hour" not in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = ts.dt.hour.astype("Int8")
        df["dow"] = ts.dt.dayofweek.astype("Int8")
    return df


def _to_dict(X):
    if isinstance(X, pd.DataFrame):
        return X.astype(str).to_dict(orient="records")
    return pd.DataFrame(X).astype(str).to_dict(orient="records")


def _to_str(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.astype(str)


def build_vectorizer(df: pd.DataFrame):
    df = _add_temporal(df.copy())
    if "timestamp" in df.columns:
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        df["dow"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
    drop = [c for c in df.columns if c.endswith("_id")]
    df.drop(columns=[c for c in drop if c in df.columns], inplace=True)

    num_cols = df.select_dtypes(include=["number", "bool"]).columns
    cat_cols = [c for c in df.columns if c not in num_cols]

    return ColumnTransformer(
        [
            ("num", Pipeline([("scale", StandardScaler(with_mean=True))]), num_cols),
            (
                "cat",
                Pipeline(
                    [
                        ("to_dict", FunctionTransformer(_to_dict, validate=False)),
                        ("hash", FeatureHasher(n_features=HASH_DIM, input_type="dict")),
                    ]
                ),
                cat_cols,
            ),
        ],
        remainder="drop",
        sparse_threshold=0.3,
    )
