import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from pathlib import Path
import json

MODEL_OUTPUT_PATH = Path(__file__).parent.parent / "models"
MODEL_OUTPUT_PATH.mkdir(exist_ok=True)


def load_dataset(path: str) -> pd.DataFrame:
    """Load transaction dataset from CSV."""
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} transactions from {path}")
    return df


def prepare_features(df: pd.DataFrame) -> np.ndarray:
    """
    Build feature matrix from transaction dataframe.
    Expected columns: value, tx_count_1h, time_since_last_tx,
                      unique_counterparties, gas_ratio, is_contract
    """
    feature_cols = [
        "value",
        "tx_count_1h",
        "time_since_last_tx",
        "unique_counterparties",
        "gas_ratio",
        "is_contract",
    ]
    df["value"] = np.log10(df["value"].clip(lower=0) + 1)
    df["time_since_last_tx"] = np.log10(df["time_since_last_tx"].clip(lower=0) + 1)

    X = df[feature_cols].fillna(0).values
    return X


def train_isolation_forest(X: np.ndarray, contamination: float = 0.05) -> IsolationForest:
    """Train Isolation Forest anomaly detector."""
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)
    print(f"Isolation Forest trained on {X.shape[0]} samples, {X.shape[1]} features")
    return model


def save_model(model, name: str):
    path = MODEL_OUTPUT_PATH / name
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {path}")


def save_metadata(meta: dict):
    with open(MODEL_OUTPUT_PATH / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)


if __name__ == "__main__":
    import sys

    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "datasets/transactions.csv"

    df = load_dataset(dataset_path)
    X = prepare_features(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = train_isolation_forest(X_scaled)

    save_model(model, "isolation_forest.pkl")
    save_model(scaler, "scaler.pkl")
    save_metadata({
        "n_samples": X.shape[0],
        "n_features": X.shape[1],
        "contamination": 0.05,
        "model": "IsolationForest",
    })

    print("Training complete.")
