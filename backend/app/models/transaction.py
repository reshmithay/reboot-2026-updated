"""
PostgreSQL models for transaction storage.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Enum as SQLEnum, DECIMAL, Text
from datetime import datetime
import enum

from app.models.base import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    COMPLETED = "COMPLETED"


class TransactionType(str, enum.Enum):
    TRANSFER = "transfer"
    SWAP = "swap"
    MINT = "mint"
    BURN = "burn"
    STAKE = "stake"
    CONTRACT_CALL = "contract_call"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    ESCROW = "ESCROW"


class Transaction(Base):
    """Transaction model for PostgreSQL."""
    
    __tablename__ = "transactions"
    
    # Primary identifiers
    id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    transaction_hash = Column(String, unique=True, index=True, nullable=False)
    
    # Transaction details
    transaction_type = Column(String, nullable=False, index=True)
    amount = Column(DECIMAL(10, 4), nullable=True)  # Allow NULL for transactions without amounts
    currency = Column(String, nullable=False, default='INR')
    transaction_timestamp = Column(DateTime, nullable=False, index=True)
    transaction_status = Column(String, nullable=False, index=True)
    on_chain_status = Column(String, nullable=True)
    
    # Account information
    from_account = Column(String, nullable=True)
    to_account = Column(String, nullable=True)
    from_wallet_address = Column(String, nullable=True, index=True)
    to_wallet_address = Column(String, nullable=True, index=True)
    wallet_address = Column(String, nullable=True, index=True)
    
    # Client information
    client_id = Column(String, nullable=True, index=True)
    client_name = Column(String, nullable=True)
    
    # Blockchain details
    blockchain_network = Column(String, default='Hyperledger Fabric')
    ledger_type = Column(String, default='Permissioned')
    chain_id = Column(Integer, nullable=True)
    block_number = Column(Integer, nullable=True, index=True)
    block_hash = Column(String, nullable=True)
    token_symbol = Column(String, nullable=True)
    
    # Gas and fees
    gas_fee = Column(DECIMAL(20, 8), nullable=True)
    gas_price = Column(DECIMAL(20, 2), nullable=True)
    
    # Metadata and correlation
    correlation_id = Column(String, nullable=True, index=True)
    tx_metadata = Column("metadata", JSON, nullable=True)  # Maps to 'metadata' column in DB
    
    # Category
    transaction_category = Column(String, nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "transaction_hash": self.transaction_hash,
            "transaction_type": self.transaction_type,
            "amount": float(self.amount) if self.amount else None,
            "currency": self.currency,
            "transaction_timestamp": self.transaction_timestamp.isoformat() if self.transaction_timestamp else None,
            "transaction_status": self.transaction_status,
            "on_chain_status": self.on_chain_status,
            "from_account": self.from_account,
            "to_account": self.to_account,
            "from_wallet_address": self.from_wallet_address,
            "to_wallet_address": self.to_wallet_address,
            "wallet_address": self.wallet_address,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "blockchain_network": self.blockchain_network,
            "ledger_type": self.ledger_type,
            "chain_id": self.chain_id,
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "token_symbol": self.token_symbol,
            "gas_fee": float(self.gas_fee) if self.gas_fee else None,
            "gas_price": float(self.gas_price) if self.gas_price else None,
            "correlation_id": self.correlation_id,
            "metadata": self.tx_metadata,
            "transaction_category": self.transaction_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
