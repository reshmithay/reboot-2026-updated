"""
Configuration models using Pydantic for type safety and validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class RiskTier(str, Enum):
    """Client risk tier levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ClientType(str, Enum):
    """Client type classification."""
    INDIVIDUAL = "INDIVIDUAL"
    CORPORATE = "CORPORATE"
    INSTITUTIONAL = "INSTITUTIONAL"


class AnomalySeverity(str, Enum):
    """Anomaly severity levels."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyCategory(str, Enum):
    """Anomaly category classification."""
    TRANSACTION = "TRANSACTION"
    BEHAVIORAL = "BEHAVIORAL"
    BLOCKCHAIN = "BLOCKCHAIN"
    RECONCILIATION = "RECONCILIATION"
    FINANCING = "FINANCING"
    LIMIT = "LIMIT"
    COUNTERPARTY = "COUNTERPARTY"
    EXPOSURE = "EXPOSURE"
    OPERATIONS = "OPERATIONS"
    EXCEPTION = "EXCEPTION"


class DetectorConfig(BaseModel):
    """Base configuration for detectors."""
    enabled: bool = True
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    @field_validator('confidence_threshold')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
        return v


class OffHoursDetectorConfig(DetectorConfig):
    """Configuration for off-hours detector."""
    business_hours_start: int = Field(default=9, ge=0, le=23)
    business_hours_end: int = Field(default=17, ge=0, le=23)
    full_balance_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    model_path: str = "ml-engine/models/pycaret/time_anomaly"


class ThresholdDetectorConfig(DetectorConfig):
    """Configuration for threshold deposit detector."""
    thresholds: List[float] = Field(default=[10000, 5000, 3000])
    threshold_margin: float = Field(default=0.05, ge=0.0, le=0.2)
    min_pattern_count: int = Field(default=3, ge=1)
    pattern_lookback_days: int = Field(default=7, ge=1)


class DailyLimitDetectorConfig(DetectorConfig):
    """Configuration for daily limit detector."""
    default_daily_value_limit: float = 50000.0
    default_daily_count_limit: int = 100
    default_per_address_limit: float = 25000.0
    warning_threshold: float = Field(default=0.80, ge=0.0, le=1.0)


class OracleDetectorConfig(DetectorConfig):
    """Configuration for oracle detector."""
    recognized_oracles: List[str] = Field(default_factory=list)
    function_signatures: List[str] = Field(
        default_factory=lambda: [
            "0xfeaf968c",  # latestRoundData
            "0x9a6fc8f5",  # getRoundData
            "0x50d25bcd"   # latestAnswer
        ]
    )


class AnomalyDetectionConfig(BaseModel):
    """Main configuration for anomaly detection system."""
    off_hours: OffHoursDetectorConfig = Field(default_factory=OffHoursDetectorConfig)
    threshold_deposit: ThresholdDetectorConfig = Field(default_factory=ThresholdDetectorConfig)
    daily_limit: DailyLimitDetectorConfig = Field(default_factory=DailyLimitDetectorConfig)
    oracle: OracleDetectorConfig = Field(default_factory=OracleDetectorConfig)
    
    # Global settings
    enable_ml_models: bool = True
    enable_bigquery: bool = True
    store_results: bool = True
    parallel_execution: bool = True
    max_concurrent_detectors: int = Field(default=10, ge=1)
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class ClientRegistryModel(BaseModel):
    """Client registry data model."""
    clientId: str
    clientName: str
    clientType: ClientType
    lei: Optional[str] = ""
    industrySector: str
    countryOfIncorporation: str
    riskTier: RiskTier
    relationshipManager: str
    walletAddress: str
    walletType: str
    facilityType: str
    creditLimit: float = Field(ge=0)
    dailyDepositLimit: float = Field(ge=0)
    dailyWithdrawalLimit: float = Field(ge=0)
    expectedActivityWindow: str
    authorizedSignatories: List[str] = Field(default_factory=list)
    kycStatus: str
    amlStatus: str


class AnomalyMasterModel(BaseModel):
    """Anomaly master data model."""
    anomaly_code: str
    category: AnomalyCategory
    severity: AnomalySeverity
    risk_score: int = Field(ge=0, le=100)
    description: str
    remediation_guidance: Optional[str] = None
    sla_hours: Optional[int] = None
    requires_manual_review: bool = False
    auto_block_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)


class TransactionModel(BaseModel):
    """Transaction data model."""
    tx_hash: str
    from_address: str
    to_address: str
    value: float = Field(ge=0)
    timestamp: str
    gas_ratio: Optional[float] = Field(None, ge=0)
    is_contract_interaction: bool = False
    function_signature: Optional[str] = None
    token_symbol: Optional[str] = None
    block_number: Optional[int] = None
    
    @field_validator('tx_hash', 'from_address', 'to_address')
    @classmethod
    def validate_ethereum_address(cls, v: str) -> str:
        """Validate Ethereum address format."""
        if not v.startswith('0x'):
            raise ValueError("Address must start with 0x")
        return v.lower()


class DetectionResultModel(BaseModel):
    """Detection result data model."""
    detection_id: str
    transaction_id: str
    is_anomaly: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    overall_severity: AnomalySeverity
    risk_score: int = Field(ge=0, le=100)
    anomaly_count: int = Field(ge=0)
    anomaly_codes: List[str]
    detections: List[Dict[str, Any]]
    all_reasons: List[str]
    client_registry: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None
    detected_at: str
