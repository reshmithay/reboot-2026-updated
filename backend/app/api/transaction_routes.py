from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.transaction_schema import TransactionIngest, TransactionResponse, TransactionListResponse
from app.services.transaction.transaction_service import TransactionService
from app.core.database import get_async_session
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = Settings()


def get_transaction_service(db_session: Optional[AsyncSession] = Depends(get_async_session)) -> TransactionService:
    """Dependency to get TransactionService with database session (PostgreSQL or BigQuery)."""
    logger.info(f"Creating TransactionService with DB_TYPE={settings.DB_TYPE}")
    return TransactionService(db_session=db_session if settings.DB_TYPE.lower() != "bigquery" else None)


@router.post("/ingest", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_transaction(
    payload: TransactionIngest,
    service: TransactionService = Depends(get_transaction_service),
):
    """Ingest a new transaction and trigger anomaly detection pipeline."""
    try:
        return await service.ingest_transaction(payload)
    except Exception as e:
        logger.error(f"Failed to ingest transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_anomaly: Optional[bool] = None,
    chain_id: Optional[int] = None,
    service: TransactionService = Depends(get_transaction_service),
):
    """List transactions with optional anomaly filter."""
    return await service.list_transactions(page, page_size, is_anomaly, chain_id)


@router.get("/{tx_hash}", response_model=TransactionResponse)
async def get_transaction(
    tx_hash: str,
    service: TransactionService = Depends(get_transaction_service),
):
    """Get a single transaction by hash."""
    result = await service.get_transaction_by_hash(tx_hash)
    if not result:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result
