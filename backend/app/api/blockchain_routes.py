from fastapi import APIRouter, HTTPException
from app.services.blockchain.blockchain_service import BlockchainService
from app.utilities.logger.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/audit/{transaction_id}")
async def get_audit_trail(transaction_id: str):
    """Fetch on-chain audit trail for a transaction."""
    try:
        service = BlockchainService()
        return await service.get_audit_trail(transaction_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-score/{address}")
async def get_risk_score(address: str):
    """Retrieve the on-chain risk score for a wallet address."""
    try:
        service = BlockchainService()
        return await service.get_risk_score(address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/{anomaly_id}")
async def get_anomaly_registry_entry(anomaly_id: str):
    """Fetch anomaly registry entry from smart contract."""
    try:
        service = BlockchainService()
        return await service.get_anomaly_registry(anomaly_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
