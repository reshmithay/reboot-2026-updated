"""
Client Registry schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ClientRegistryCreate(BaseModel):
    """Schema for creating a new client."""
    client_id: str = Field(..., description="Unique client identifier")
    client_name: str = Field(..., description="Client name")
    client_type: Optional[str] = None
    lei: Optional[str] = None
    industry_sector: Optional[str] = None
    country_of_incorporation: Optional[str] = None
    risk_tier: Optional[str] = None
    relationship_manager: Optional[str] = None
    wallet_address: Optional[str] = None
    wallet_type: Optional[str] = None
    facility_type: Optional[str] = None
    credit_limit: float = 0.0
    daily_deposit_limit: float = 0.0
    daily_withdrawal_limit: float = 0.0
    expected_activity_window: Optional[str] = None
    authorized_signatories: Optional[list] = None  # Can be list of strings or dicts
    kyc_status: Optional[str] = None
    aml_status: Optional[str] = None


class ClientRegistryUpdate(BaseModel):
    """Schema for updating client information."""
    client_name: Optional[str] = None
    client_type: Optional[str] = None
    lei: Optional[str] = None
    industry_sector: Optional[str] = None
    country_of_incorporation: Optional[str] = None
    risk_tier: Optional[str] = None
    relationship_manager: Optional[str] = None
    wallet_address: Optional[str] = None
    wallet_type: Optional[str] = None
    facility_type: Optional[str] = None
    credit_limit: Optional[float] = None
    daily_deposit_limit: Optional[float] = None
    daily_withdrawal_limit: Optional[float] = None
    expected_activity_window: Optional[str] = None
    authorized_signatories: Optional[list] = None  # Can be list of strings or dicts
    kyc_status: Optional[str] = None
    aml_status: Optional[str] = None


class ClientRegistryResponse(BaseModel):
    """Schema for client registry response."""
    client_id: str
    client_name: str
    client_type: Optional[str]
    lei: Optional[str]
    industry_sector: Optional[str]
    country_of_incorporation: Optional[str]
    risk_tier: Optional[str]
    relationship_manager: Optional[str]
    wallet_address: Optional[str]
    wallet_type: Optional[str]
    facility_type: Optional[str]
    credit_limit: float
    daily_deposit_limit: float
    daily_withdrawal_limit: float
    expected_activity_window: Optional[str]
    authorized_signatories: Optional[list]  # Can be list of strings or dicts
    kyc_status: Optional[str]
    aml_status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ClientRegistryListResponse(BaseModel):
    """Schema for paginated client list response."""
    items: List[ClientRegistryResponse]
    total: int
    page: int
    page_size: int
