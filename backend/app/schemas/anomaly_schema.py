from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AnomalyStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    UNDER_REVIEW = "UNDER_REVIEW"


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyCategory(str, Enum):
    FRAUD = "FRAUD"
    RISK = "RISK"
    COMPLIANCE = "COMPLIANCE"
    OPERATIONAL = "OPERATIONAL"
    SUSPICIOUS = "SUSPICIOUS"


class AnomalyReason(BaseModel):
    """Individual anomaly reason with code and description."""
    reasonCode: str
    description: str
    score: Optional[float] = Field(None, description="Confidence score for this reason (0-1)")


class AnomalyDetectRequest(BaseModel):
    transaction_hash: str = Field(..., description="Transaction hash to detect anomalies")
    force: bool = Field(False, description="Force re-analysis even if cached")


class AnomalyResultResponse(BaseModel):
    """Complete anomaly detection result."""
    anomalyId: str
    transactionId: str
    transactionHash: str
    clientId: Optional[str]
    
    # Transaction details
    amount: Optional[float]
    currency: Optional[str]
    fromAccount: Optional[str]
    toAccount: Optional[str]
    fromWalletAddress: Optional[str]
    toWalletAddress: Optional[str]
    transactionType: Optional[str]
    
    # Anomaly detection results
    anomalyScore: float = Field(..., ge=0.0, le=1.0, description="Anomaly score 0-1")
    severity: str
    anomalyCategory: str
    anomalyTypes: List[str]
    anomalyReasons: List[AnomalyReason]
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    
    # Model information
    modelName: Optional[str]
    modelVersion: Optional[str]
    
    # Review and case management
    reviewStatus: str
    assignedTo: Optional[str]
    caseId: Optional[str]
    
    # Timestamps
    detectedAt: datetime
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# Legacy response for backward compatibility
class AnomalyResponse(BaseModel):
    id: str
    transaction_id: str
    score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score 0-1")
    severity: str
    status: str
    features: dict
    detected_at: datetime
    blockchain_tx_hash: Optional[str] = None
    narrative_id: Optional[str] = None

    class Config:
        from_attributes = True


class AnomalyResultListResponse(BaseModel):
    """Paginated list of anomaly results."""
    items: List[AnomalyResultResponse]
    total: int
    page: int
    page_size: int


class AnomalyListResponse(BaseModel):
    """Legacy list response."""
    items: list[AnomalyResponse]
    total: int
    page: int
    page_size: int
