"""
Time window detector - uses Isolation Forest for transactions outside expected patterns.
"""
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class TimeWindowDetector(BaseDetector):
    """Detects transactions outside expected time windows using ML."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model_path = Path(self.config.get("model_path", "ml-engine/models/isolation_forest.pkl"))
        self._model = None
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """Detect time-based anomalies using Isolation Forest."""
        tx_time = datetime.fromisoformat(transaction.get("transaction_timestamp", datetime.utcnow().isoformat()))
        
        # Extract temporal features
        features = self._extract_time_features(tx_time, transaction, context)
        
        # Get anomaly score from model
        anomaly_score = await self._get_anomaly_score(features)
        
        if anomaly_score > 0.7:
            reasons = self._explain_time_anomaly(tx_time, anomaly_score, context)
            
            return self._create_result(
                is_anomaly=True,
                confidence=anomaly_score,
                anomaly_code="OFF_HOURS_ACTIVITY",
                reasons=reasons,
                metadata={
                    "transaction_time": tx_time.isoformat(),
                    "hour_of_day": tx_time.hour,
                    "day_of_week": tx_time.strftime("%A"),
                    "is_weekend": tx_time.weekday() >= 5,
                    "anomaly_score": anomaly_score
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.2,
            reasons=["Transaction within expected time windows"],
            metadata={"anomaly_score": anomaly_score}
        )
    
    def _extract_time_features(self, tx_time: datetime, tx: Dict, context: Dict) -> np.ndarray:
        """Extract temporal features for ML model."""
        hour = tx_time.hour
        minute = tx_time.minute / 60.0
        weekday = tx_time.weekday()
        is_weekend = 1.0 if weekday >= 5 else 0.0
        day_of_month = tx_time.day
        
        # Cyclical encoding for hour
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        
        # Historical pattern deviation
        avg_hour = context.get("user_avg_transaction_hour", 12)
        hour_deviation = abs(hour - avg_hour) / 24.0
        
        features = np.array([[
            hour,
            minute,
            weekday,
            is_weekend,
            hour_sin,
            hour_cos,
            hour_deviation,
            day_of_month / 31.0
        ]])
        
        return features
    
    async def _get_anomaly_score(self, features: np.ndarray) -> float:
        """Get anomaly score from Isolation Forest."""
        if self._model is None:
            self._load_model()
        
        if self._model is None:
            # Fallback heuristic
            hour = int(features[0, 0])
            is_weekend = features[0, 3]
            
            if hour < 6 or hour > 22:
                return 0.85
            elif is_weekend > 0.5:
                return 0.65
            return 0.3
        
        try:
            raw_score = self._model.decision_function(features)[0]
            normalized = 1 - (raw_score + 0.5)
            return max(0.0, min(1.0, normalized))
        except Exception:
            return 0.5
    
    def _explain_time_anomaly(self, tx_time: datetime, score: float, context: Dict) -> list:
        """Generate human-readable reasons for time anomaly."""
        reasons = []
        hour = tx_time.hour
        
        if hour < 6:
            reasons.append(f"Very early morning transaction ({hour}:00)")
        elif hour > 22:
            reasons.append(f"Late night transaction ({hour}:00)")
        
        if tx_time.weekday() >= 5:
            reasons.append(f"Weekend transaction ({tx_time.strftime('%A')})")
        
        avg_hour = context.get("user_avg_transaction_hour")
        if avg_hour and abs(hour - avg_hour) > 6:
            reasons.append(f"Unusual time compared to typical pattern (avg: {avg_hour}:00)")
        
        reasons.append(f"Time anomaly score: {score:.2f}")
        
        return reasons
    
    def _load_model(self):
        """Load Isolation Forest model."""
        try:
            if self.model_path.exists():
                with open(self.model_path, "rb") as f:
                    self._model = pickle.load(f)
        except Exception:
            self._model = None
