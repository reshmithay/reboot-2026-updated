"""
Helper service for storing anomaly detection results.
"""
from typing import Dict, Any, List
from datetime import datetime
import uuid

from app.repositories.anomaly_result_repository import AnomalyResultRepository
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class AnomalyResultService:
    """Service for managing anomaly detection results."""
    
    def __init__(self, repository: AnomalyResultRepository):
        self.repository = repository
    
    async def store_anomaly_result(
        self,
        transaction: Dict[str, Any],
        anomaly_score: float,
        anomaly_types: List[str],
        anomaly_reasons: List[Dict[str, str]],
        confidence: float,
        model_name: str = "Ensemble",
        model_version: str = "v1.0"
    ) -> Dict[str, Any]:
        """
        Store anomaly detection result in the database.
        
        Args:
            transaction: Transaction data dict
            anomaly_score: Computed anomaly score (0-1)
            anomaly_types: List of detected anomaly type codes
            anomaly_reasons: List of {reasonCode, description} dicts
            confidence: Model confidence score (0-1)
            model_name: Name of the ML model used
            model_version: Version of the model
            
        Returns:
            Created anomaly result as dict
        """
        try:
            # Generate anomaly ID
            anomaly_id = f"ANM{str(uuid.uuid4().hex)[:8].upper()}"
            
            # Determine severity based on score
            severity = self._classify_severity(anomaly_score)
            
            # Determine category based on anomaly types
            anomaly_category = self._classify_category(anomaly_types)
            
            # Prepare anomaly data
            anomaly_data = {
                "anomaly_id": anomaly_id,
                "transaction_id": transaction.get("transaction_id"),
                "transaction_hash": transaction.get("transaction_hash"),
                "client_id": transaction.get("client_id"),
                
                # Transaction details (denormalized)
                "amount": transaction.get("amount"),
                "currency": transaction.get("currency", "INR"),
                "from_account": transaction.get("from_account"),
                "to_account": transaction.get("to_account"),
                "from_wallet_address": transaction.get("from_wallet_address"),
                "to_wallet_address": transaction.get("to_wallet_address"),
                "transaction_type": transaction.get("transaction_type"),
                
                # Detection results
                "anomaly_score": anomaly_score,
                "severity": severity,
                "anomaly_category": anomaly_category,
                "anomaly_types": anomaly_types,
                "anomaly_reasons": anomaly_reasons,
                "confidence": confidence,
                
                # Model info
                "model_name": model_name,
                "model_version": model_version,
                
                # Review status
                "review_status": "PENDING",
                "assigned_to": None,
                "case_id": None,
                
                # Timestamps
                "detected_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            result = await self.repository.create(anomaly_data)
            logger.info(f"Stored anomaly result {anomaly_id} for transaction {transaction.get('transaction_id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to store anomaly result: {e}", exc_info=True)
            raise
    
    def _classify_severity(self, score: float) -> str:
        """Classify severity based on anomaly score."""
        if score >= 0.9:
            return "CRITICAL"
        elif score >= 0.75:
            return "HIGH"
        elif score >= 0.5:
            return "MEDIUM"
        return "LOW"
    
    def _classify_category(self, anomaly_types: List[str]) -> str:
        """Classify anomaly category based on detected types."""
        # Fraud indicators
        fraud_types = ["MULTI_TRANSACTION_CYCLING", "DUPLICATE_ESCROW", "STRUCTURING"]
        if any(t in fraud_types for t in anomaly_types):
            return "FRAUD"
        
        # Compliance indicators
        compliance_types = ["OFF_HOURS_ACTIVITY", "UNRECOGNIZED_ORACLE", "LEDGER_RECONCILIATION_BREAK"]
        if any(t in compliance_types for t in anomaly_types):
            return "COMPLIANCE"
        
        # Risk indicators
        risk_types = ["THRESHOLD_DEPOSIT", "DAILY_LIMIT_BREACH", "FULL_WITHDRAWAL"]
        if any(t in risk_types for t in anomaly_types):
            return "RISK"
        
        # Default
        return "SUSPICIOUS"
    
    async def update_review_status(
        self,
        anomaly_id: str,
        review_status: str,
        assigned_to: str = None,
        case_id: str = None
    ) -> Dict[str, Any]:
        """Update review status of an anomaly."""
        update_data = {
            "review_status": review_status,
            "updated_at": datetime.utcnow()
        }
        
        if assigned_to:
            update_data["assigned_to"] = assigned_to
        if case_id:
            update_data["case_id"] = case_id
        
        result = await self.repository.update(anomaly_id, update_data)
        if not result:
            raise ValueError(f"Anomaly {anomaly_id} not found")
        
        return result
