"""
Base repository interface for transaction storage.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class BaseTransactionRepository(ABC):
    """Abstract base class for transaction repositories."""
    
    @abstractmethod
    async def create(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction record."""
        pass
    
    @abstractmethod
    async def get_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID."""
        pass
    
    @abstractmethod
    async def get_by_hash(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction by hash."""
        pass
    
    @abstractmethod
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        is_anomaly: Optional[bool] = None,
        chain_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """List transactions with filters and pagination."""
        pass
    
    @abstractmethod
    async def update(self, transaction_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update transaction record."""
        pass
    
    @abstractmethod
    async def delete(self, transaction_id: str) -> bool:
        """Delete transaction record."""
        pass
    
    @abstractmethod
    async def count(self, is_anomaly: Optional[bool] = None, chain_id: Optional[int] = None) -> int:
        """Count transactions with optional filters."""
        pass
