from pydantic import BaseModel, Field
from typing import List


class ShapContributor(BaseModel):
    """SHAP contributor for a feature."""
    feature: str
    actual_value: float
    shap_contribution: float
    direction: str  # "increased" or "decreased"


class ShapFeaturesResponse(BaseModel):
    """Response containing SHAP features for an anomaly."""
    anomaly_id: str
    transaction_hash: str
    prediction_probability: float = Field(..., description="Model confidence score")
    prediction_label: str = Field(default="High Risk")
    shap_contributors: List[ShapContributor]
    anomaly_score: float = Field(..., description="Anomaly score from detection")
    anomaly_category: str


class NarrativeGenerateRequest(BaseModel):
    """Request to generate narrative."""
    anomaly_id: str
    top_k: int = Field(default=5, ge=1, le=10)
    persona: str = Field(
        default="fraud-analyst",
        description="Role-based persona: compliance-officer, relationship-manager, auditor, regulator, fraud-analyst"
    )


class NarrativeResponse(BaseModel):
    """Generated narrative response."""
    anomaly_id: str
    narrative: str
    shap_contributors: List[ShapContributor]
    prediction_probability: float
    prediction_label: str
    model_used: str
    generated_at: str
