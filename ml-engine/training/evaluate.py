import numpy as np
import pickle
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
)
from pathlib import Path
import pandas as pd

MODEL_PATH = Path(__file__).parent.parent / "models"


def load_model(name: str):
    with open(MODEL_PATH / name, "rb") as f:
        return pickle.load(f)


def evaluate(dataset_path: str, label_col: str = "is_fraud"):
    df = pd.read_csv(dataset_path)
    y_true = df[label_col].values

    # Load models
    scaler = load_model("scaler.pkl")
    model = load_model("isolation_forest.pkl")

    feature_cols = [
        "value", "tx_count_1h", "time_since_last_tx",
        "unique_counterparties", "gas_ratio", "is_contract",
    ]
    X = df[feature_cols].fillna(0).values
    X_scaled = scaler.transform(X)

    # Isolation Forest: -1 = anomaly, 1 = normal
    raw_scores = model.decision_function(X_scaled)
    y_score = 1 - (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min())
    y_pred = (y_score >= 0.5).astype(int)

    print("=== Classification Report ===")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Anomaly"]))

    roc = roc_auc_score(y_true, y_score)
    ap = average_precision_score(y_true, y_score)
    print(f"ROC-AUC:           {roc:.4f}")
    print(f"Average Precision: {ap:.4f}")

    return {"roc_auc": roc, "average_precision": ap}


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "datasets/labeled_transactions.csv"
    evaluate(path)
