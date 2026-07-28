"""
Reconciliation break detector - rules-based.
Detects transactions that break reconciliation patterns.
"""
from typing import Dict, Any, List
from decimal import Decimal

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class ReconciliationDetector(BaseDetector):
    """Detects reconciliation breaks in paired transactions."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.tolerance = Decimal(str(self.config.get("tolerance", 0.001)))  # 0.1%
        self.lookback_minutes = self.config.get("lookback_minutes", 60)
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Check if transaction breaks expected reconciliation pairing.
        E.g., deposit followed by withdrawal should match, escrow in/out should balance.
        """
        tx_value = Decimal(str(transaction.get("amount", 0)))
        from_address = transaction.get("from_wallet_address")
        to_address = transaction.get("to_wallet_address")
        tx_type = transaction.get("tx_type", "transfer")
        
        # Get expected reconciliation from context/BigQuery
        expected_reconciliation = context.get("expected_reconciliation", {})
        
        # Check if this is part of a reconciliation pair
        is_reconciliation_tx = self._is_reconciliation_transaction(transaction, context)
        
        if not is_reconciliation_tx:
            return self._create_result(
                is_anomaly=False,
                confidence=0.0,
                reasons=["Not a reconciliation transaction"],
                metadata={}
            )
        
        # Find matching pair
        matching_tx = await self._find_matching_transaction(transaction, context)
        
        if matching_tx:
            # Check if values reconcile
            match_value = Decimal(str(matching_tx.get("amount", 0)))
            difference = abs(tx_value - match_value)
            percent_diff = (difference / tx_value * 100) if tx_value > 0 else 0
            
            if difference > (tx_value * self.tolerance):
                confidence = min(0.9, 0.6 + float(percent_diff) / 100)
                return self._create_result(
                    is_anomaly=True,
                    confidence=confidence,
                    anomaly_code="LEDGER_RECONCILIATION_BREAK",
                    reasons=[
                        f"Reconciliation break: difference of {difference} ({percent_diff:.2f}%)",
                        f"Expected: {match_value}, Actual: {tx_value}",
                        f"Paired transaction: {matching_tx.get('tx_hash', 'unknown')}"
                    ],
                    metadata={
                        "expected_value": float(match_value),
                        "actual_value": float(tx_value),
                        "difference": float(difference),
                        "percent_difference": float(percent_diff),
                        "paired_tx_hash": matching_tx.get("tx_hash")
                    }
                )
        else:
            # Missing reconciliation pair
            return self._create_result(
                is_anomaly=True,
                confidence=0.75,
                reasons=[
                    "Expected reconciliation transaction not found",
                    f"Unmatched {tx_type} of value {tx_value}"
                ],
                metadata={
                    "tx_type": tx_type,
                    "value": float(tx_value),
                    "missing_pair": True
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=["Reconciliation check passed"],
            metadata={"paired_tx_hash": matching_tx.get("tx_hash")}
        )
    
    def _is_reconciliation_transaction(self, tx: Dict, context: Dict) -> bool:
        """Check if transaction requires reconciliation."""
        tx_type = tx.get("tx_type", "")
        reconciliation_types = ["escrow_deposit", "escrow_withdrawal", "paired_transfer"]
        
        return tx_type in reconciliation_types or context.get("requires_reconciliation", False)
    
    async def _find_matching_transaction(self, tx: Dict, context: Dict) -> Dict[str, Any] | None:
        """Find the matching reconciliation transaction."""
        # Check context for pre-fetched pairs
        if "reconciliation_pairs" in context:
            tx_hash = tx.get("tx_hash")
            return context["reconciliation_pairs"].get(tx_hash)
        
        # Placeholder for BigQuery lookup
        return None
