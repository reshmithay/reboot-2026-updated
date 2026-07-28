import pickle
import numpy as np
from pathlib import Path
from app.config.settings import settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class AnomalyService:
    def __init__(self):
        self._isolation_forest = None
        self._threshold = settings.ANOMALY_THRESHOLD

    def _load_model(self):
        if self._isolation_forest is None:
            model_path = Path(settings.ML_MODEL_PATH) / settings.ISOLATION_FOREST_MODEL
            if model_path.exists():
                with open(model_path, "rb") as f:
                    self._isolation_forest = pickle.load(f)
                logger.info("Isolation Forest model loaded")
            else:
                logger.warning(f"Model not found at {model_path}, using mock scores")

    async def detect_and_record(self, transaction_id: str, force: bool = False) -> dict:
        """
        Run the full anomaly detection pipeline:
        1. Fetch transaction features
        2. Score with Isolation Forest + Autoencoder ensemble
        3. Persist result to DB
        4. If anomaly, write to blockchain audit trail
        5. Trigger Firebase notification if high severity
        """
        self._load_model()
        # TODO: fetch real features from transaction repository
        features = np.array([[0.5, 1000.0, 3, 0.2]])  # placeholder feature vector
        score = self._compute_score(features)
        severity = self._classify_severity(score)

        logger.info(f"Transaction {transaction_id}: score={score:.3f}, severity={severity}")
        return {
            "id": f"anom-{transaction_id[:8]}",
            "transaction_id": transaction_id,
            "score": score,
            "severity": severity,
            "status": "pending",
            "features": {"raw": features.tolist()},
            "detected_at": "2026-07-21T00:00:00Z",
        }

    def _compute_score(self, features: np.ndarray) -> float:
        if self._isolation_forest:
            raw = self._isolation_forest.decision_function(features)[0]
            # Normalize to [0, 1] where 1 = most anomalous
            return float(1 - (raw - (-0.5)) / 1.0)
        return 0.3  # fallback mock score

    def _classify_severity(self, score: float) -> str:
        if score >= 0.9:
            return "critical"
        elif score >= 0.75:
            return "high"
        elif score >= 0.5:
            return "medium"
        return "low"

    async def list_anomalies(self, page: int, page_size: int, severity: str = None) -> dict:
        # TODO: query anomaly repository
        return {"items": [], "total": 0, "page": page, "page_size": page_size}

    async def get_anomaly(self, anomaly_id: str) -> dict | None:
        # TODO: query anomaly repository
        return None

    async def get_stats(self) -> dict:
        return {
            "total_anomalies": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "false_positives": 0,
        }
