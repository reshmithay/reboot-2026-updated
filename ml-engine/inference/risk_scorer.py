import numpy as np
from enum import Enum
from ml_engine.inference.predictor import AnomalyPredictor

predictor = AnomalyPredictor()


class RiskLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


RISK_THRESHOLDS = {
    RiskLevel.CRITICAL: 0.90,
    RiskLevel.HIGH: 0.75,
    RiskLevel.MEDIUM: 0.50,
    RiskLevel.LOW: 0.25,
    RiskLevel.SAFE: 0.0,
}


def classify_risk(score: float) -> RiskLevel:
    for level, threshold in RISK_THRESHOLDS.items():
        if score >= threshold:
            return level
    return RiskLevel.SAFE


def score_transaction(features: np.ndarray) -> dict:
    """
    Full risk scoring pipeline.
    Returns score, risk level, and contributing factors.
    """
    result = predictor.predict(features)
    score = result["ensemble_score"]
    risk = classify_risk(score)

    contributing_factors = []
    if result["isolation_forest_score"] > 0.6:
        contributing_factors.append("Unusual transaction pattern (Isolation Forest)")
    if result["autoencoder_score"] > 0.6:
        contributing_factors.append("High reconstruction error (Autoencoder)")

    return {
        **result,
        "risk_level": risk.value,
        "contributing_factors": contributing_factors,
        "risk_score_100": int(score * 100),
    }
