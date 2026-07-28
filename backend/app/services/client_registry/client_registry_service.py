"""
Client Registry service for business logic.
"""
from typing import Optional, Dict, Any
from app.repositories.client_registry_repository import ClientRegistryRepository
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class ClientRegistryService:
    """Service for client registry operations."""
    
    def __init__(self, repository: ClientRegistryRepository):
        self.repository = repository
    
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client."""
        logger.info(f"Creating client {client_data.get('client_id')}")
        return await self.repository.create(client_data)
    
    async def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID."""
        return await self.repository.get_by_id(client_id)
    
    async def get_client_by_wallet(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get client by wallet address."""
        return await self.repository.get_by_wallet(wallet_address)
    
    async def list_clients(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_tier: Optional[str] = None,
        kyc_status: Optional[str] = None,
        aml_status: Optional[str] = None,
        client_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List clients with filters."""
        return await self.repository.list(
            page, page_size, risk_tier, kyc_status, aml_status, client_type, search
        )
    
    async def update_client(
        self, client_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update client information."""
        logger.info(f"Updating client {client_id}")
        return await self.repository.update(client_id, update_data)
    
    async def delete_client(self, client_id: str) -> bool:
        """Delete a client."""
        logger.info(f"Deleting client {client_id}")
        return await self.repository.delete(client_id)
    
    async def get_client_limits(self, client_id: str) -> Optional[Dict[str, float]]:
        """Get client transaction limits."""
        client = await self.repository.get_by_id(client_id)
        if not client:
            return None
        
        return {
            "credit_limit": client.get("credit_limit", 0.0),
            "daily_deposit_limit": client.get("daily_deposit_limit", 0.0),
            "daily_withdrawal_limit": client.get("daily_withdrawal_limit", 0.0),
        }
    
    async def check_compliance_status(self, client_id: str) -> Optional[Dict[str, str]]:
        """Check client compliance status."""
        client = await self.repository.get_by_id(client_id)
        if not client:
            return None
        
        return {
            "kyc_status": client.get("kyc_status"),
            "aml_status": client.get("aml_status"),
            "risk_tier": client.get("risk_tier"),
        }
