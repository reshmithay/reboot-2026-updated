import httpx
from app.schemas.narrative_schema import NarrativeRequest, NarrativeResponse
from app.config.settings import settings
from app.utilities.logger.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class NarrativeService:
    def __init__(self):
        self._llm_url = settings.LLM_SERVER_URL

    async def generate_narrative(self, request: NarrativeRequest) -> dict:
        """
        Forward narrative generation request to the LLM narrative microservice.
        The microservice uses Gemini to generate human-readable explanations.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._llm_url}/api/v1/narratives/generate",
                json=request.model_dump(),
            )
            resp.raise_for_status()
            return resp.json()

    async def get_by_anomaly_id(self, anomaly_id: str) -> dict | None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._llm_url}/api/v1/narratives/{anomaly_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
