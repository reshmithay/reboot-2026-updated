from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.narrative_schema import NarrativeRequest, NarrativeResponse
from app.services.narrative.narrative_service import NarrativeService
from app.utilities.logger.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/generate", response_model=NarrativeResponse, status_code=status.HTTP_201_CREATED)
async def generate_narrative(
    payload: NarrativeRequest,
    service: NarrativeService = Depends(),
):
    """Generate a Gemini-powered narrative explanation for an anomaly."""
    try:
        return await service.generate_narrative(payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Narrative generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{anomaly_id}", response_model=NarrativeResponse)
async def get_narrative_by_anomaly(anomaly_id: str, service: NarrativeService = Depends()):
    """Get existing narrative for an anomaly."""
    result = await service.get_by_anomaly_id(anomaly_id)
    if not result:
        raise HTTPException(status_code=404, detail="Narrative not found")
    return result
