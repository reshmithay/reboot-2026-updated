"""
Anomaly detection service - coordinates detection, LLM narrative, and alerting.
"""
from typing import Dict, Any, List
from datetime import datetime

from app.services.anomaly.orchestrator import AnomalyOrchestrator
from app.clients.llm_client import LLMClient
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class AnomalyService:
    """Main service for anomaly detection workflow."""
    
    def __init__(self):
        self.orchestrator = AnomalyOrchestrator()
        self.llm_client = LLMClient()
    
    async def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete anomaly analysis pipeline:
        1. Run all detectors
        2. Generate LLM narrative if anomalous
        3. Return enriched result
        """
        logger.info(f"Analyzing transaction: {transaction.get('tx_hash')}")
        
        # Step 1: Run anomaly detectors
        detection_result = await self.orchestrator.detect_all(transaction)
        
        # Step 2: Generate narrative if anomaly detected
        if detection_result["is_anomaly"]:
            narrative = await self._generate_narrative(detection_result)
            detection_result["narrative"] = narrative
            
            # Log critical anomalies
            if detection_result["overall_severity"] in ["critical", "high"]:
                logger.warning(
                    f"Critical anomaly detected: {transaction.get('tx_hash')} "
                    f"- Score: {detection_result['overall_score']:.2f}"
                )
        else:
            detection_result["narrative"] = "No anomalies detected. Transaction appears normal."
        
        return detection_result
    
    async def batch_analyze(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple transactions in batch."""
        results = []
        for tx in transactions:
            try:
                result = await self.analyze_transaction(tx)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {tx.get('tx_hash')}: {e}")
                results.append({
                    "transaction_id": tx.get("tx_hash"),
                    "is_anomaly": False,
                    "error": str(e)
                })
        
        return results
    
    async def _generate_narrative(self, detection_result: Dict[str, Any]) -> str:
        """Generate human-readable narrative using LLM."""
        try:
            # Prepare context for LLM
            context = {
                "anomaly_count": detection_result["anomaly_count"],
                "severity": detection_result["overall_severity"],
                "score": detection_result["overall_score"],
                "detections": detection_result["detections"],
                "transaction": detection_result["transaction_summary"]
            }
            
            # Call LLM service
            narrative = await self.llm_client.generate_narrative(
                anomaly_type="multi_pattern_detection",
                context=context
            )
            
            return narrative
        except Exception as e:
            logger.error(f"Failed to generate narrative: {e}")
            return "Narrative generation failed. Multiple anomalies detected."
