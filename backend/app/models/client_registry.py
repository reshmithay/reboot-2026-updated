"""
Client Registry model for PostgreSQL.
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, DECIMAL, Text
from datetime import datetime

from app.models.base import Base


class ClientRegistry(Base):
    """Client Registry model for PostgreSQL."""
    
    __tablename__ = "client_registry"
    
    # Primary identifier
    client_id = Column(String, primary_key=True, index=True)
    
    # Basic information
    client_name = Column(String, nullable=False, index=True)
    client_type = Column(String, nullable=True, index=True)
    lei = Column(String, nullable=True)  # Legal Entity Identifier
    industry_sector = Column(String, nullable=True, index=True)
    country_of_incorporation = Column(String, nullable=True)
    
    # Risk and relationship
    risk_tier = Column(String, nullable=True, index=True)
    relationship_manager = Column(String, nullable=True)
    
    # Wallet information
    wallet_address = Column(String, nullable=True, index=True)
    wallet_type = Column(String, nullable=True)
    
    # Facility details
    facility_type = Column(String, nullable=True)
    credit_limit = Column(DECIMAL(20, 2), nullable=True, default=0)
    daily_deposit_limit = Column(DECIMAL(20, 2), nullable=True, default=0)
    daily_withdrawal_limit = Column(DECIMAL(20, 2), nullable=True, default=0)
    
    # Operating parameters
    expected_activity_window = Column(String, nullable=True)  # e.g., "09:00-17:00 UTC"
    authorized_signatories = Column(JSON, nullable=True)  # Array of authorized persons
    
    # Compliance status
    kyc_status = Column(String, nullable=True, index=True)
    aml_status = Column(String, nullable=True, index=True)
    
    # Audit timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "client_type": self.client_type,
            "lei": self.lei,
            "industry_sector": self.industry_sector,
            "country_of_incorporation": self.country_of_incorporation,
            "risk_tier": self.risk_tier,
            "relationship_manager": self.relationship_manager,
            "wallet_address": self.wallet_address,
            "wallet_type": self.wallet_type,
            "facility_type": self.facility_type,
            "credit_limit": float(self.credit_limit) if self.credit_limit else 0.0,
            "daily_deposit_limit": float(self.daily_deposit_limit) if self.daily_deposit_limit else 0.0,
            "daily_withdrawal_limit": float(self.daily_withdrawal_limit) if self.daily_withdrawal_limit else 0.0,
            "expected_activity_window": self.expected_activity_window,
            "authorized_signatories": self.authorized_signatories,
            "kyc_status": self.kyc_status,
            "aml_status": self.aml_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
