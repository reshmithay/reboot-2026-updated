import numpy as np
import pandas as pd
from typing import Tuple


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive time-based features from transaction timestamps."""
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["from_address", "timestamp"])

    df["time_since_last_tx"] = (
        df.groupby("from_address")["timestamp"].diff().dt.total_seconds().fillna(3600)
    )
    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    return df


def add_address_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rolling address-level activity features."""
    df = df.sort_values("timestamp")

    # Count transactions per address in last 1 hour (approximate via rolling)
    df["tx_count_1h"] = (
        df.groupby("from_address")["timestamp"]
        .transform(lambda x: x.rolling("1h").count())
        .fillna(1)
    )
    df["unique_counterparties"] = (
        df.groupby("from_address")["to_address"]
        .transform("nunique")
        .fillna(1)
    )
    return df


def add_value_features(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and derive value-based anomaly signals."""
    df["value_log"] = np.log10(df["value"].clip(lower=0) + 1)
    df["value_zscore"] = (df["value"] - df["value"].mean()) / (df["value"].std() + 1e-9)
    df["is_large_transfer"] = (df["value"] > df["value"].quantile(0.99)).astype(int)
    return df


def build_feature_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, list]:
    """Return (X, feature_names) after all feature engineering steps."""
    df = add_temporal_features(df)
    df = add_address_features(df)
    df = add_value_features(df)

    feature_cols = [
        "value_log",
        "value_zscore",
        "tx_count_1h",
        "time_since_last_tx",
        "unique_counterparties",
        "gas_ratio",
        "is_contract",
        "hour_of_day",
        "is_weekend",
        "is_large_transfer",
    ]
    X = df[feature_cols].fillna(0).values
    return X, feature_cols
