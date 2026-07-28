import numpy as np
from typing import Any
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)

# Feature weights for ensemble scoring
FEATURE_WEIGHTS = {
    "isolation_forest": 0.6,
    "autoencoder": 0.4,
}


def ensemble_score(if_score: float, ae_score: float) -> float:
    """Combine Isolation Forest and Autoencoder scores into a final risk score."""
    return (
        FEATURE_WEIGHTS["isolation_forest"] * if_score
        + FEATURE_WEIGHTS["autoencoder"] * ae_score
    )


def extract_features(transaction: dict) -> np.ndarray:
    """
    Extract numerical feature vector from a transaction for ML scoring.
    Features:
      - log10(value + 1)
      - tx_count_last_1h (address activity)
      - time_since_last_tx (seconds)
      - unique_counterparties
      - gas_ratio (gas_used / gas_limit)
      - is_contract_interaction (0/1)
    """
    value = float(transaction.get("amount", 0))
    tx_count = int(transaction.get("tx_count_last_1h", 0))
    time_since_last = float(transaction.get("time_since_last_tx", 3600))
    unique_counterparties = int(transaction.get("unique_counterparties", 1))
    gas_ratio = float(transaction.get("gas_ratio", 0.5))
    is_contract = 1.0 if transaction.get("is_contract_interaction", False) else 0.0

    features = np.array([
        np.log10(value + 1),
        tx_count,
        np.log10(time_since_last + 1),
        unique_counterparties,
        gas_ratio,
        is_contract,
    ], dtype=np.float32)

    return features.reshape(1, -1)
