from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    COMPLETED = "COMPLETED"


class TransactionType(str, Enum):
    TRANSFER = "transfer"
    SWAP = "swap"
    MINT = "mint"
    BURN = "burn"
    STAKE = "stake"
    CONTRACT_CALL = "contract_call"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    ESCROW = "ESCROW"


class TransactionIngest(BaseModel):
    """Schema for ingesting a new transaction."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    transaction_hash: str = Field(..., description="Blockchain transaction hash")
    transaction_type: str
    amount: float = Field(..., ge=0)
    currency: str = "INR"
    transaction_timestamp: Optional[datetime] = None
    transaction_status: str = "PENDING"
    on_chain_status: Optional[str] = None
    
    # Account information
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    from_wallet_address: Optional[str] = None
    to_wallet_address: Optional[str] = None
    wallet_address: Optional[str] = None
    
    # Client information
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    
    # Blockchain details
    blockchain_network: str = "Hyperledger Fabric"
    ledger_type: str = "Permissioned"
    chain_id: Optional[int] = None
    block_number: Optional[int] = None
    block_hash: Optional[str] = None
    token_symbol: Optional[str] = None
    
    # Gas and fees
    gas_fee: Optional[float] = None
    gas_price: Optional[float] = None
    
    # Metadata
    correlation_id: Optional[str] = None
    metadata: Optional[dict] = None
    transaction_category: Optional[str] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: str
    transaction_id: str
    transaction_hash: str
    transaction_type: str
    amount: Optional[float] = None
    currency: str
    transaction_timestamp: datetime
    transaction_status: str
    on_chain_status: Optional[str]
    
    # Account information
    from_account: Optional[str]
    to_account: Optional[str]
    from_wallet_address: Optional[str]
    to_wallet_address: Optional[str]
    wallet_address: Optional[str]
    
    # Client information
    client_id: Optional[str]
    client_name: Optional[str]
    
    # Blockchain details
    blockchain_network: Optional[str]
    ledger_type: Optional[str]
    chain_id: Optional[int]
    block_number: Optional[int]
    block_hash: Optional[str]
    token_symbol: Optional[str]
    
    # Gas and fees
    gas_fee: Optional[float]
    gas_price: Optional[float]
    
    # Metadata
    correlation_id: Optional[str]
    metadata: Optional[dict]
    transaction_category: Optional[str]
    
    # Timestamps
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
