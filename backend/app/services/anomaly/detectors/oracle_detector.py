"""
Oracle address validation detector - rules-based.
Detects transactions with unrecognized oracle addresses.
"""
from typing import Dict, Any, Set, List

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class OracleDetector(BaseDetector):
    """Detects interactions with unrecognized oracle addresses."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Default recognized oracles (Chainlink, Band, etc.)
        self.recognized_oracles = set(self.config.get("recognized_oracles", [
            "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  # Chainlink ETH/USD
            "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c",  # Chainlink BTC/USD
            "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",  # Band Protocol
            # Add more recognized oracle addresses
        ]))
        self.require_oracle_registry = self.config.get("require_registry", True)
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Check if oracle address is recognized.
        """
        to_address = transaction.get("to_wallet_address", "")
        from_address = transaction.get("from_wallet_address", "")
        
        # Check if transaction involves oracle interaction
        is_oracle_interaction = self._is_oracle_interaction(transaction, context)
        
        if not is_oracle_interaction:
            return self._create_result(
                is_anomaly=False,
                confidence=0.0,
                reasons=["Not an oracle interaction"],
                metadata={}
            )
        
        # Fetch recognized oracles from BigQuery if available
        if self.require_oracle_registry:
            registry_oracles = await self._fetch_oracle_registry(context)
            all_recognized = self.recognized_oracles.union(registry_oracles)
        else:
            all_recognized = self.recognized_oracles
        
        # Check if oracle is recognized
        oracle_address = to_address  # Assuming oracle is the recipient
        is_recognized = oracle_address.lower() in {addr.lower() for addr in all_recognized}
        
        if not is_recognized:
            confidence = 0.85
            return self._create_result(
                is_anomaly=True,
                confidence=confidence,
                reasons=[
                    f"Unrecognized oracle address: {oracle_address}",
                    f"Not in registry of {len(all_recognized)} known oracles",
                    "Potential malicious oracle or price manipulation risk"
                ],
                metadata={
                    "oracle_address": oracle_address,
                    "transaction_type": "oracle_interaction",
                    "recognized_oracle_count": len(all_recognized)
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=[f"Recognized oracle: {oracle_address}"],
            metadata={"oracle_address": oracle_address, "is_recognized": True}
        )
    
    def _is_oracle_interaction(self, transaction: Dict, context: Dict) -> bool:
        """Determine if transaction is an oracle interaction."""
        # Check metadata flags
        if transaction.get("is_oracle_call"):
            return True
        
        # Check function signature (e.g., latestRoundData, getRoundData)
        tx_input = transaction.get("input", "")
        oracle_signatures = [
            "0xfeaf968c",  # latestRoundData()
            "0x9a6fc8f5",  # getRoundData(uint80)
            "0x50d25bcd",  # latestAnswer()
        ]
        
        if any(tx_input.startswith(sig) for sig in oracle_signatures):
            return True
        
        # Check if to_address is tagged as oracle in context
        to_address = transaction.get("to_wallet_address", "")
        oracle_tags = context.get("address_tags", {}).get(to_address, [])
        if "oracle" in oracle_tags or "price_feed" in oracle_tags:
            return True
        
        return False
    
    async def _fetch_oracle_registry(self, context: Dict) -> Set[str]:
        """Fetch oracle registry from BigQuery or context."""
        # Try context first
        if "oracle_registry" in context:
            return set(context["oracle_registry"])
        
        # Fetch from BigQuery (placeholder)
        # This would query a table of known oracle addresses
        return set()
