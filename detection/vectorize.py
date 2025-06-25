import pandas as pd
from sklearn.feature_extraction import FeatureHasher
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.compose import ColumnTransformer

HASH_DIM = 2**16

def _to_str(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.astype(str)

def build_vectorizer(df: pd.DataFrame):
    df = df.copy()
    drop = ["timestamp"] + [c for c in df.columns if c.endswith("_id")]
    df.drop(columns=[c for c in drop if c in df.columns], inplace=True)

    num_cols = df.select_dtypes(include=["number", "bool"]).columns
    cat_cols = [c for c in df.columns if c not in num_cols]

    return ColumnTransformer(
        [
            ("num", Pipeline([("scale", StandardScaler(with_mean=False))]), num_cols),
            (
                "cat",
                Pipeline(
                    [
                        ("to_str", FunctionTransformer(_to_str,
                                               validate=False,
                                               feature_names_out="one-to-one")),
                        ("hash", FeatureHasher(n_features=HASH_DIM, input_type="pair")),
                    ]
                ),
                cat_cols,
            ),
        ],
        remainder="drop",
        sparse_threshold=0.3,
    )
