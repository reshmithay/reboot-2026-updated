"""
Client Registry API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.client_registry_schema import (
    ClientRegistryCreate,
    ClientRegistryUpdate,
    ClientRegistryResponse,
    ClientRegistryListResponse,
)
from app.services.client_registry.client_registry_service import ClientRegistryService
from app.repositories.factory import RepositoryFactory
from app.core.database import get_async_session
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = Settings()


def get_client_service(db_session: Optional[AsyncSession] = Depends(get_async_session)) -> ClientRegistryService:
    """Dependency to get ClientRegistryService (PostgreSQL or BigQuery based on config)."""
    try:
        logger.info(f"Creating ClientRegistryService with DB_TYPE={settings.DB_TYPE}")
        if settings.DB_TYPE.lower() == "bigquery":
            repository = RepositoryFactory.get_client_repository()
        else:
            repository = RepositoryFactory.get_client_repository(db_session)
        service = ClientRegistryService(repository)
        logger.info("ClientRegistryService created successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to create ClientRegistryService: {e}", exc_info=True)
        raise


@router.post("/", response_model=ClientRegistryResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientRegistryCreate,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Create a new client."""
    try:
        client_data = payload.dict()
        result = await service.create_client(client_data)
        return result
    except Exception as e:
        logger.error(f"Failed to create client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ClientRegistryListResponse)
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_tier: Optional[str] = None,
    kyc_status: Optional[str] = None,
    aml_status: Optional[str] = None,
    client_type: Optional[str] = None,
    search: Optional[str] = None,
    service: ClientRegistryService = Depends(get_client_service),
):
    """List clients with optional filters."""
    try:
        logger.info(f"Listing clients: page={page}, page_size={page_size}")
        result = await service.list_clients(
            page, page_size, risk_tier, kyc_status, aml_status, client_type, search
        )
        logger.info(f"Successfully listed {result.get('total', 0)} clients")
        return result
    except Exception as e:
        logger.error(f"Failed to list clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=ClientRegistryResponse)
async def get_client(
    client_id: str,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Get a client by ID."""
    result = await service.get_client(client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return result


@router.get("/wallet/{wallet_address}", response_model=ClientRegistryResponse)
async def get_client_by_wallet(
    wallet_address: str,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Get a client by wallet address."""
    result = await service.get_client_by_wallet(wallet_address)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return result


@router.put("/{client_id}", response_model=ClientRegistryResponse)
async def update_client(
    client_id: str,
    payload: ClientRegistryUpdate,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Update client information."""
    try:
        # Only include non-None values
        update_data = {k: v for k, v in payload.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = await service.update_client(client_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Delete a client."""
    success = await service.delete_client(client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return None


@router.get("/{client_id}/limits")
async def get_client_limits(
    client_id: str,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Get client transaction limits."""
    limits = await service.get_client_limits(client_id)
    if not limits:
        raise HTTPException(status_code=404, detail="Client not found")
    return limits


@router.get("/{client_id}/compliance")
async def get_client_compliance(
    client_id: str,
    service: ClientRegistryService = Depends(get_client_service),
):
    """Get client compliance status."""
    compliance = await service.check_compliance_status(client_id)
    if not compliance:
        raise HTTPException(status_code=404, detail="Client not found")
    return compliance
