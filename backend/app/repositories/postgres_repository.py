"""
PostgreSQL repository implementation for transactions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseTransactionRepository
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class PostgresTransactionRepository(BaseTransactionRepository):
    """PostgreSQL implementation of transaction repository."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction record."""
        try:
            # Convert enum strings to enums if needed
            if "status" in transaction_data and isinstance(transaction_data["status"], str):
                transaction_data["status"] = TransactionStatus(transaction_data["status"])
            if "tx_type" in transaction_data and isinstance(transaction_data["tx_type"], str):
                transaction_data["tx_type"] = TransactionType(transaction_data["tx_type"])
            
            transaction = Transaction(**transaction_data)
            self.session.add(transaction)
            await self.session.flush()
            await self.session.refresh(transaction)
            
            logger.info(f"Created transaction {transaction.transaction_hash} in PostgreSQL")
            return transaction.to_dict()
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            raise
    
    async def get_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID."""
        try:
            stmt = select(Transaction).where(Transaction.id == transaction_id)
            result = await self.session.execute(stmt)
            transaction = result.scalar_one_or_none()
            
            return transaction.to_dict() if transaction else None
        except Exception as e:
            logger.error(f"Failed to get transaction by ID: {e}")
            raise
    
    async def get_by_hash(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction by hash."""
        try:
            stmt = select(Transaction).where(Transaction.transaction_hash == tx_hash)
            result = await self.session.execute(stmt)
            transaction = result.scalar_one_or_none()
            
            return transaction.to_dict() if transaction else None
        except Exception as e:
            logger.error(f"Failed to get transaction by hash: {e}")
            raise
    
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
        try:
            # Build filters
            filters = []
            if is_anomaly is not None:
                # Note: anomaly fields not in schema, skip for now
                pass
            if chain_id is not None:
                filters.append(Transaction.chain_id == chain_id)
            if start_date:
                filters.append(Transaction.transaction_timestamp >= start_date)
            if end_date:
                filters.append(Transaction.transaction_timestamp <= end_date)
            
            # Count total
            count_stmt = select(func.count(Transaction.id))
            if filters:
                count_stmt = count_stmt.where(and_(*filters))
            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar()
            
            # Get paginated results
            stmt = select(Transaction).order_by(Transaction.transaction_timestamp.desc())
            if filters:
                stmt = stmt.where(and_(*filters))
            
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            result = await self.session.execute(stmt)
            transactions = result.scalars().all()
            
            return {
                "items": [tx.to_dict() for tx in transactions],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except Exception as e:
            logger.error(f"Failed to list transactions: {e}")
            raise
    
    async def update(self, transaction_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update transaction record."""
        try:
            stmt = select(Transaction).where(Transaction.id == transaction_id)
            result = await self.session.execute(stmt)
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            transaction.updated_at = datetime.utcnow()
            await self.session.flush()
            await self.session.refresh(transaction)
            
            logger.info(f"Updated transaction {transaction.transaction_hash}")
            return transaction.to_dict()
        except Exception as e:
            logger.error(f"Failed to update transaction: {e}")
            raise
    
    async def delete(self, transaction_id: str) -> bool:
        """Delete transaction record."""
        try:
            stmt = select(Transaction).where(Transaction.id == transaction_id)
            result = await self.session.execute(stmt)
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                return False
            
            await self.session.delete(transaction)
            await self.session.flush()
            
            logger.info(f"Deleted transaction {transaction.transaction_hash}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete transaction: {e}")
            raise
    
    async def count(self, is_anomaly: Optional[bool] = None, chain_id: Optional[int] = None) -> int:
        """Count transactions with optional filters."""
        try:
            filters = []
            # Anomaly field not in schema
            if chain_id is not None:
                filters.append(Transaction.chain_id == chain_id)
            
            stmt = select(func.count(Transaction.id))
            if filters:
                stmt = stmt.where(and_(*filters))
            
            result = await self.session.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f"Failed to count transactions: {e}")
            raise
