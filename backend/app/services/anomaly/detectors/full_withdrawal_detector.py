"""
Full withdrawal detector (90-100% of balance).
Combines rules with Isolation Forest.
"""
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, Any

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class FullWithdrawalDetector(BaseDetector):
    """Detects full or near-full balance withdrawals."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.min_threshold = self.config.get("min_threshold", 0.90)  # 90%
        self.max_threshold = self.config.get("max_threshold", 1.00)  # 100%
        self.model_path = Path(self.config.get("model_path", "ml-engine/models/isolation_forest.pkl"))
        self._model = None
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """Detect full balance withdrawals."""
        tx_value = float(transaction.get("amount", 0))
        from_address = transaction.get("from_wallet_address")
        
        # Get account balance
        account_balance = context.get("account_balance", {}).get(from_address)
        if account_balance is None:
            account_balance = await self._fetch_balance(from_address, context)
        
        if account_balance <= 0:
            return self._create_result(
                is_anomaly=False,
                confidence=0.0,
                reasons=["No balance available"],
                metadata={}
            )
        
        # Calculate withdrawal ratio
        withdrawal_ratio = tx_value / account_balance
        
        # Rule: Check if full withdrawal
        is_full_withdrawal = self.min_threshold <= withdrawal_ratio <= self.max_threshold
        
        if is_full_withdrawal:
            # Get ML anomaly score
            ml_score = await self._get_ml_score(transaction, context, withdrawal_ratio)
            
            confidence = 0.7 + (withdrawal_ratio - 0.9) * 2.0 + (ml_score * 0.2)
            confidence = min(confidence, 1.0)
            
            return self._create_result(
                is_anomaly=True,
                confidence=confidence,
                anomaly_code="FULL_WITHDRAWAL",
                reasons=[
                    f"Full withdrawal: {withdrawal_ratio*100:.1f}% of account balance",
                    f"Withdrawing ${tx_value:.2f} from ${account_balance:.2f}",
                    f"ML anomaly score: {ml_score:.2f}"
                ],
                metadata={
                    "withdrawal_ratio": withdrawal_ratio,
                    "account_balance": account_balance,
                    "withdrawal_amount": tx_value,
                    "ml_score": ml_score,
                    "is_exact_full": withdrawal_ratio >= 0.99
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=[f"Partial withdrawal: {withdrawal_ratio*100:.1f}% of balance"],
            metadata={"withdrawal_ratio": withdrawal_ratio}
        )
    
    async def _get_ml_score(self, tx: Dict, context: Dict, withdrawal_ratio: float) -> float:
        """Get anomaly score from Isolation Forest."""
        if self._model is None:
            self._load_model()
        
        features = np.array([[
            np.log10(float(tx.get("amount", 1)) + 1),
            withdrawal_ratio,
            float(context.get("tx_count_1h", 0)),
            float(context.get("unique_counterparties", 1)),
        ]])
        
        if self._model is None:
            return 0.5
        
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
    
    async def _fetch_balance(self, address: str, context: Dict) -> float:
        """Fetch account balance from BigQuery."""
        # Placeholder - implement with BigQueryClient
        return 0.0
