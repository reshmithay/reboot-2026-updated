"""
Base detector interface for all anomaly detection models.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class AnomalyResult:
    """Standard result format for all detectors."""
    
    def __init__(
        self,
        is_anomaly: bool,
        detector_name: str,
        confidence: float,
        severity: str,
        anomaly_code: str,
        reasons: List[str],
        metadata: Dict[str, Any],
        detected_at: Optional[datetime] = None
    ):
        self.is_anomaly = is_anomaly
        self.detector_name = detector_name
        self.confidence = confidence  # 0.0 to 1.0
        self.severity = severity  # low, medium, high, critical
        self.anomaly_code = anomaly_code  # Maps to anomaly_master table
        self.reasons = reasons
        self.metadata = metadata
        self.detected_at = detected_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_anomaly": self.is_anomaly,
            "detector_name": self.detector_name,
            "confidence": self.confidence,
            "severity": self.severity,
            "anomaly_code": self.anomaly_code,
            "reasons": self.reasons,
            "metadata": self.metadata,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None
        }


class BaseDetector(ABC):
    """Abstract base class for all anomaly detectors."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Detect anomalies in a transaction.
        
        Args:
            transaction: Transaction data with fields like value, from_address, to_address, timestamp, etc.
            context: Additional context like historical transactions, reference data, etc.
        
        Returns:
            AnomalyResult with detection outcome
        """
        pass
    
    def _create_result(
        self,
        is_anomaly: bool,
        confidence: float,
        reasons: List[str],
        metadata: Dict[str, Any] = None,
        anomaly_code: str = ""
    ) -> AnomalyResult:
        """Helper to create standardized result."""
        severity = self._calculate_severity(confidence, is_anomaly)
        return AnomalyResult(
            is_anomaly=is_anomaly,
            detector_name=self.name,
            confidence=confidence,
            severity=severity,
            anomaly_code=anomaly_code,
            reasons=reasons,
            metadata=metadata or {},
            detected_at=datetime.utcnow()
        )
    
    def _calculate_severity(self, confidence: float, is_anomaly: bool) -> str:
        """Calculate severity based on confidence."""
        if not is_anomaly:
            return "low"
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.75:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        return "low"
