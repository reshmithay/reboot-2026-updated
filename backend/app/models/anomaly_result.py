"""
Anomaly Results model for PostgreSQL.
"""
from sqlalchemy import Column, String, Float, DateTime, JSON, DECIMAL, Text
from datetime import datetime

from app.models.base import Base


class AnomalyResult(Base):
    """Anomaly detection results model for PostgreSQL."""
    
    __tablename__ = "anomaly_results"
    
    # Primary identifier
    anomaly_id = Column(String, primary_key=True, index=True)
    
    # Transaction references
    transaction_id = Column(String, nullable=False, index=True)
    transaction_hash = Column(String, nullable=False, index=True)
    client_id = Column(String, nullable=True, index=True)
    
    # Transaction details (denormalized for reporting)
    amount = Column(DECIMAL(10, 4), nullable=True)
    currency = Column(String, nullable=True)
    from_account = Column(String, nullable=True)
    to_account = Column(String, nullable=True)
    from_wallet_address = Column(String, nullable=True)
    to_wallet_address = Column(String, nullable=True)
    transaction_type = Column(String, nullable=True)
    
    # Anomaly detection results
    anomaly_score = Column(Float, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)  # HIGH, MEDIUM, LOW
    anomaly_category = Column(String, nullable=False, index=True)  # FRAUD, RISK, etc.
    anomaly_types = Column(JSON, nullable=False)  # Array of anomaly type codes
    anomaly_reasons = Column(JSON, nullable=False)  # Array of {reasonCode, description}
    confidence = Column(Float, nullable=False)
    
    # Model information
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    
    # Review and case management
    review_status = Column(String, nullable=False, default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, FALSE_POSITIVE
    assigned_to = Column(String, nullable=True, index=True)
    case_id = Column(String, nullable=True, index=True)
    
    # Timestamps
    detected_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "anomalyId": self.anomaly_id,
            "transactionId": self.transaction_id,
            "transactionHash": self.transaction_hash,
            "clientId": self.client_id,
            "amount": float(self.amount) if self.amount else None,
            "currency": self.currency,
            "fromAccount": self.from_account,
            "toAccount": self.to_account,
            "fromWalletAddress": self.from_wallet_address,
            "toWalletAddress": self.to_wallet_address,
            "transactionType": self.transaction_type,
            "anomalyScore": self.anomaly_score,
            "severity": self.severity,
            "anomalyCategory": self.anomaly_category,
            "anomalyTypes": self.anomaly_types,
            "anomalyReasons": self.anomaly_reasons,
            "confidence": self.confidence,
            "modelName": self.model_name,
            "modelVersion": self.model_version,
            "reviewStatus": self.review_status,
            "assignedTo": self.assigned_to,
            "caseId": self.case_id,
            "detectedAt": self.detected_at.isoformat() if self.detected_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
