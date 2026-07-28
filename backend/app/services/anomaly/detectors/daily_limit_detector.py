"""
Daily limit detector - rules-based.
Detects transactions that exceed daily transaction limits.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class DailyLimitDetector(BaseDetector):
    """Detects violations of daily transaction limits."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Default limits
        self.daily_value_limit = self.config.get("daily_value_limit", 50000)
        self.daily_count_limit = self.config.get("daily_count_limit", 100)
        self.per_address_value_limit = self.config.get("per_address_value_limit", 25000)
        self.lookback_hours = 24
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Check if transaction exceeds daily limits.
        """
        from_address = transaction.get("from_wallet_address")
        tx_value = float(transaction.get("amount", 0))
        tx_time = datetime.fromisoformat(transaction.get("transaction_timestamp", datetime.utcnow().isoformat()))
        
        # Get limits from BigQuery reference data or use defaults
        limits = await self._get_limits(from_address, context)
        
        # Get transactions from last 24 hours
        recent_txs = context.get("recent_transactions", [])
        if not recent_txs:
            recent_txs = await self._fetch_recent_24h(from_address, tx_time)
        
        # Calculate daily stats
        daily_stats = self._calculate_daily_stats(from_address, recent_txs, tx_value)
        
        violations = []
        
        # Check value limit
        if daily_stats["total_value"] > limits["daily_value_limit"]:
            violations.append(
                f"Daily value limit exceeded: ${daily_stats['total_value']:.2f} > ${limits['daily_value_limit']:.2f}"
            )
        
        # Check count limit
        if daily_stats["tx_count"] > limits["daily_count_limit"]:
            violations.append(
                f"Daily transaction count exceeded: {daily_stats['tx_count']} > {limits['daily_count_limit']}"
            )
        
        # Check per-address limit
        for addr, value in daily_stats["per_address_values"].items():
            if value > limits["per_address_value_limit"]:
                violations.append(
                    f"Per-address limit exceeded for {addr[:10]}...: ${value:.2f} > ${limits['per_address_value_limit']:.2f}"
                )
        
        if violations:
            confidence = min(0.95, 0.7 + len(violations) * 0.1)
            return self._create_result(
                is_anomaly=True,
                confidence=confidence,
                reasons=violations,
                metadata={
                    "daily_total_value": daily_stats["total_value"],
                    "daily_tx_count": daily_stats["tx_count"],
                    "limits": limits,
                    "violation_count": len(violations),
                    "per_address_breakdown": daily_stats["per_address_values"]
                }
            )
        
        # Warn if approaching limits
        if daily_stats["total_value"] > limits["daily_value_limit"] * 0.8:
            return self._create_result(
                is_anomaly=True,
                confidence=0.4,
                reasons=[
                    f"Approaching daily limit: {daily_stats['total_value']/limits['daily_value_limit']*100:.0f}% of limit used"
                ],
                metadata=daily_stats
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=["Within daily limits"],
            metadata=daily_stats
        )
    
    def _calculate_daily_stats(
        self, from_address: str, recent_txs: List[Dict], current_value: float
    ) -> Dict[str, Any]:
        """Calculate statistics for last 24 hours."""
        total_value = current_value
        tx_count = 1
        per_address_values = defaultdict(float)
        per_address_values[from_address] = current_value
        
        for tx in recent_txs:
            if tx.get("from_wallet_address") == from_address:
                value = float(tx.get("amount", 0))
                to_addr = tx.get("to_wallet_address")
                total_value += value
                tx_count += 1
                per_address_values[to_addr] += value
        
        return {
            "total_value": total_value,
            "tx_count": tx_count,
            "per_address_values": dict(per_address_values),
            "unique_recipients": len(per_address_values)
        }
    
    async def _get_limits(self, address: str, context: Dict) -> Dict[str, float]:
        """Get limits from BigQuery or use defaults."""
        # Try to get custom limits from context/BigQuery
        if "account_limits" in context and address in context["account_limits"]:
            return context["account_limits"][address]
        
        # Fetch from BigQuery reference table (placeholder)
        # This would query account-specific limits
        
        # Return defaults
        return {
            "daily_value_limit": self.daily_value_limit,
            "daily_count_limit": self.daily_count_limit,
            "per_address_value_limit": self.per_address_value_limit
        }
    
    async def _fetch_recent_24h(self, address: str, tx_time: datetime) -> List[Dict]:
        """Fetch transactions from last 24 hours."""
        # Placeholder - implement with BigQueryClient
        return []
