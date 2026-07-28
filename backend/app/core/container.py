"""
Dependency injection container for anomaly detection system.
"""
from typing import Optional
from functools import lru_cache

from app.config.settings import get_settings, Settings
from app.clients.bigquery.reference_data_client import BigQueryReferenceClient
from app.services.anomaly.orchestrator import AnomalyOrchestrator
from app.services.anomaly_service import AnomalyService
from app.models.detection_models import AnomalyDetectionConfig
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._bq_client: Optional[BigQueryReferenceClient] = None
        self._orchestrator: Optional[AnomalyOrchestrator] = None
        self._anomaly_service: Optional[AnomalyService] = None
        self._config: Optional[AnomalyDetectionConfig] = None
    
    @property
    def settings(self) -> Settings:
        """Get application settings."""
        if self._settings is None:
            self._settings = get_settings()
        return self._settings
    
    @property
    def detection_config(self) -> AnomalyDetectionConfig:
        """Get detection configuration."""
        if self._config is None:
            self._config = AnomalyDetectionConfig()
        return self._config
    
    @property
    def bigquery_client(self) -> BigQueryReferenceClient:
        """Get BigQuery client."""
        if self._bq_client is None:
            self._bq_client = BigQueryReferenceClient()
            logger.info("BigQuery client initialized")
        return self._bq_client
    
    @property
    def orchestrator(self) -> AnomalyOrchestrator:
        """Get anomaly orchestrator."""
        if self._orchestrator is None:
            config_dict = self.detection_config.model_dump()
            self._orchestrator = AnomalyOrchestrator(config=config_dict)
            logger.info("Anomaly orchestrator initialized")
        return self._orchestrator
    
    @property
    def anomaly_service(self) -> AnomalyService:
        """Get anomaly service."""
        if self._anomaly_service is None:
            self._anomaly_service = AnomalyService()
            logger.info("Anomaly service initialized")
        return self._anomaly_service
    
    async def initialize(self):
        """Initialize async components."""
        try:
            await self.orchestrator.initialize()
            logger.info("Container initialized successfully")
        except Exception as e:
            logger.error(f"Container initialization failed: {e}")
            raise
    
    def reset(self):
        """Reset all dependencies (useful for testing)."""
        self._settings = None
        self._bq_client = None
        self._orchestrator = None
        self._anomaly_service = None
        self._config = None
        logger.info("Container reset")


@lru_cache()
def get_container() -> Container:
    """Get singleton container instance."""
    return Container()


# Global container instance
container = get_container()
