"""
Threshold deposit detector - detects deposits just below reporting thresholds.
Uses rules + Isolation Forest + statistical outlier detection.
"""
import numpy as np
from typing import Dict, Any, List
import pickle
from pathlib import Path

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class ThresholdDepositDetector(BaseDetector):
    """Detects deposits designed to evade threshold reporting (e.g., structuring/smurfing)."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Common regulatory thresholds
        self.thresholds = self.config.get("thresholds", [10000, 5000, 3000])
        self.threshold_margin = self.config.get("threshold_margin", 0.05)  # 5% below threshold
        self.pattern_lookback_days = self.config.get("lookback_days", 7)
        self.min_pattern_count = self.config.get("min_pattern_count", 3)
        self.model_path = Path(self.config.get("model_path", "ml-engine/models/isolation_forest.pkl"))
        self._model = None
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Detect threshold-avoidance patterns.
        """
        tx_value = float(transaction.get("amount", 0))
        from_address = transaction.get("from_wallet_address")
        to_address = transaction.get("to_wallet_address")
        
        # Rule 1: Check if just below threshold
        near_threshold_info = self._check_near_threshold(tx_value)
        
        # Rule 2: Pattern detection - multiple near-threshold deposits
        recent_txs = context.get("recent_transactions", [])
        pattern_detected, pattern_stats = self._detect_structuring_pattern(
            tx_value, recent_txs, from_address
        )
        
        # Statistical outlier detection
        is_statistical_outlier, z_score = self._statistical_outlier_check(tx_value, recent_txs)
        
        # ML: Isolation Forest score
        ml_score = await self._get_ml_anomaly_score(transaction, context)
        
        # Combine signals
        if near_threshold_info["is_near_threshold"] and pattern_detected:
            confidence = 0.9 + (ml_score * 0.1)
            return self._create_result(
                is_anomaly=True,
                confidence=min(confidence, 1.0),
                reasons=[
                    f"Deposit ${tx_value:.2f} is {near_threshold_info['percent_below']:.1f}% below ${near_threshold_info['threshold']:.0f} threshold",
                    f"Pattern: {pattern_stats['count']} similar deposits in {self.pattern_lookback_days} days",
                    f"Total structured amount: ${pattern_stats['total_value']:.2f}",
                    f"Statistical Z-score: {z_score:.2f}"
                ],
                metadata={
                    "threshold": near_threshold_info["threshold"],
                    "margin_below": near_threshold_info["amount_below"],
                    "pattern_count": pattern_stats["count"],
                    "pattern_total": pattern_stats["total_value"],
                    "z_score": z_score,
                    "ml_score": ml_score
                }
            )
        elif near_threshold_info["is_near_threshold"]:
            confidence = 0.6 + (ml_score * 0.2)
            return self._create_result(
                is_anomaly=True,
                confidence=confidence,
                reasons=[
                    f"Deposit just below ${near_threshold_info['threshold']:.0f} threshold",
                    "Possible threshold avoidance"
                ],
                metadata={
                    "threshold": near_threshold_info["threshold"],
                    "ml_score": ml_score
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=["No threshold avoidance pattern detected"],
            metadata={"ml_score": ml_score}
        )
    
    def _check_near_threshold(self, value: float) -> Dict[str, Any]:
        """Check if value is just below a known threshold."""
        for threshold in sorted(self.thresholds, reverse=True):
            lower_bound = threshold * (1 - self.threshold_margin)
            upper_bound = threshold
            
            if lower_bound <= value < upper_bound:
                amount_below = threshold - value
                percent_below = (amount_below / threshold) * 100
                return {
                    "is_near_threshold": True,
                    "threshold": threshold,
                    "amount_below": amount_below,
                    "percent_below": percent_below
                }
        
        return {"is_near_threshold": False}
    
    def _detect_structuring_pattern(
        self, current_value: float, recent_txs: List[Dict], address: str
    ) -> tuple[bool, Dict[str, Any]]:
        """Detect repeated near-threshold deposits (structuring/smurfing)."""
        near_threshold_txs = []
        
        for tx in recent_txs:
            if tx.get("from_wallet_address") == address:
                tx_value = float(tx.get("amount", 0))
                if self._check_near_threshold(tx_value)["is_near_threshold"]:
                    near_threshold_txs.append(tx_value)
        
        # Include current transaction
        if self._check_near_threshold(current_value)["is_near_threshold"]:
            near_threshold_txs.append(current_value)
        
        pattern_detected = len(near_threshold_txs) >= self.min_pattern_count
        
        stats_dict = {
            "count": len(near_threshold_txs),
            "total_value": sum(near_threshold_txs),
            "avg_value": np.mean(near_threshold_txs) if near_threshold_txs else 0,
            "std_value": np.std(near_threshold_txs) if len(near_threshold_txs) > 1 else 0
        }
        
        return pattern_detected, stats_dict
    
    def _statistical_outlier_check(self, value: float, recent_txs: List[Dict]) -> tuple[bool, float]:
        """Use z-score to detect statistical outliers."""
        if len(recent_txs) < 10:
            return False, 0.0
        
        values = [float(tx.get("amount", 0)) for tx in recent_txs]
        values.append(value)
        
        arr = np.array(values, dtype=float)
        mean, std = arr.mean(), arr.std()
        z_scores = np.abs((arr - mean) / std) if std > 0 else np.zeros_like(arr)
        current_z = z_scores[-1]
        
        is_outlier = current_z > 2.5  # 2.5 sigma threshold
        return is_outlier, float(current_z)
    
    async def _get_ml_anomaly_score(self, transaction: Dict, context: Dict) -> float:
        """Get anomaly score from Isolation Forest."""
        if self._model is None:
            self._load_model()
        
        # Extract features
        features = np.array([[
            np.log10(float(transaction.get("amount", 1)) + 1),
            float(context.get("tx_count_1h", 0)),
            float(context.get("unique_counterparties", 1)),
            float(transaction.get("gas_ratio", 0.5)),
        ]])
        
        if self._model is None:
            return 0.5  # Fallback
        
        try:
            raw_score = self._model.decision_function(features)[0]
            normalized = 1 - (raw_score + 0.5)
            return max(0.0, min(1.0, normalized))
        except Exception:
            return 0.5
    
    def _load_model(self):
        """Load Isolation Forest model."""
        try:
            if self.model_path.exists():
                with open(self.model_path, "rb") as f:
                    self._model = pickle.load(f)
        except Exception:
            self._model = None
