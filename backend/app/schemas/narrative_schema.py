from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class NarrativeType(str, Enum):
    ANOMALY_EXPLANATION = "anomaly_explanation"
    FRAUD_SUMMARY = "fraud_summary"
    EXECUTIVE_REPORT = "executive_report"
    RISK_ASSESSMENT = "risk_assessment"


class NarrativeRequest(BaseModel):
    anomaly_id: str
    narrative_type: NarrativeType = NarrativeType.ANOMALY_EXPLANATION
    include_recommendations: bool = True
    audience: str = Field("analyst", description="Target audience: analyst, executive, compliance")


class NarrativeResponse(BaseModel):
    id: str
    anomaly_id: str
    narrative_type: NarrativeType
    title: str
    summary: str
    detailed_explanation: str
    risk_factors: list[str]
    recommendations: list[str]
    confidence_score: float
    generated_at: datetime
    model_used: str

    class Config:
        from_attributes = True
