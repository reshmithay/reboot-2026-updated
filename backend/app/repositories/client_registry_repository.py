"""
Client Registry repository for PostgreSQL.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_registry import ClientRegistry
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class ClientRegistryRepository:
    """PostgreSQL repository for client registry operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client record."""
        try:
            client = ClientRegistry(**client_data)
            self.session.add(client)
            await self.session.flush()
            await self.session.refresh(client)
            
            logger.info(f"Created client {client.client_id} in PostgreSQL")
            return client.to_dict()
        except Exception as e:
            logger.error(f"Failed to create client: {e}")
            raise
    
    async def get_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID."""
        try:
            stmt = select(ClientRegistry).where(ClientRegistry.client_id == client_id)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            return client.to_dict() if client else None
        except Exception as e:
            logger.error(f"Failed to get client by ID: {e}")
            raise
    
    async def get_by_wallet(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get client by wallet address."""
        try:
            stmt = select(ClientRegistry).where(ClientRegistry.wallet_address == wallet_address)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            return client.to_dict() if client else None
        except Exception as e:
            logger.error(f"Failed to get client by wallet: {e}")
            raise
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_tier: Optional[str] = None,
        kyc_status: Optional[str] = None,
        aml_status: Optional[str] = None,
        client_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List clients with filters and pagination."""
        try:
            # Build filters
            filters = []
            if risk_tier:
                filters.append(ClientRegistry.risk_tier == risk_tier)
            if kyc_status:
                filters.append(ClientRegistry.kyc_status == kyc_status)
            if aml_status:
                filters.append(ClientRegistry.aml_status == aml_status)
            if client_type:
                filters.append(ClientRegistry.client_type == client_type)
            if search:
                # Search in client name, ID, or wallet address
                search_filter = or_(
                    ClientRegistry.client_name.ilike(f"%{search}%"),
                    ClientRegistry.client_id.ilike(f"%{search}%"),
                    ClientRegistry.wallet_address.ilike(f"%{search}%")
                )
                filters.append(search_filter)
            
            # Count total
            count_stmt = select(func.count(ClientRegistry.client_id))
            if filters:
                count_stmt = count_stmt.where(and_(*filters))
            total_result = await self.session.execute(count_stmt)
            total = total_result.scalar()
            
            # Get paginated results
            stmt = select(ClientRegistry).order_by(ClientRegistry.client_name)
            if filters:
                stmt = stmt.where(and_(*filters))
            
            stmt = stmt.offset((page - 1) * page_size).limit(page_size)
            result = await self.session.execute(stmt)
            clients = result.scalars().all()
            
            return {
                "items": [client.to_dict() for client in clients],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except Exception as e:
            logger.error(f"Failed to list clients: {e}")
            raise
    
    async def update(self, client_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update client record."""
        try:
            stmt = select(ClientRegistry).where(ClientRegistry.client_id == client_id)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            if not client:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if value is not None and hasattr(client, key):
                    setattr(client, key, value)
            
            client.updated_at = datetime.utcnow()
            await self.session.flush()
            await self.session.refresh(client)
            
            logger.info(f"Updated client {client.client_id}")
            return client.to_dict()
        except Exception as e:
            logger.error(f"Failed to update client: {e}")
            raise
    
    async def delete(self, client_id: str) -> bool:
        """Delete client record."""
        try:
            stmt = select(ClientRegistry).where(ClientRegistry.client_id == client_id)
            result = await self.session.execute(stmt)
            client = result.scalar_one_or_none()
            
            if not client:
                return False
            
            await self.session.delete(client)
            await self.session.flush()
            
            logger.info(f"Deleted client {client.client_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete client: {e}")
            raise
    
    async def count(
        self,
        risk_tier: Optional[str] = None,
        kyc_status: Optional[str] = None,
        aml_status: Optional[str] = None
    ) -> int:
        """Count clients with optional filters."""
        try:
            filters = []
            if risk_tier:
                filters.append(ClientRegistry.risk_tier == risk_tier)
            if kyc_status:
                filters.append(ClientRegistry.kyc_status == kyc_status)
            if aml_status:
                filters.append(ClientRegistry.aml_status == aml_status)
            
            stmt = select(func.count(ClientRegistry.client_id))
            if filters:
                stmt = stmt.where(and_(*filters))
            
            result = await self.session.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f"Failed to count clients: {e}")
            raise
