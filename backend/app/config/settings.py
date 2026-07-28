from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "Blockchain Anomaly Detection"
    APP_VERSION: str = "1.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = "changeme"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Firebase
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""

    # BigQuery
    BIGQUERY_PROJECT_ID: str = "ltc-hack2026-team35"
    BIGQUERY_DATASET: str = "ltchack2026team35"
    BIGQUERY_TABLE: str = "transactions"
    BIGQUERY_ANOMALY_TABLE: str = "anomaly_results"
    BIGQUERY_CLIENT_TABLE: str = "client_registry"
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # Blockchain
    BLOCKCHAIN_RPC_URL: str = "https://polygon-rpc.com"
    BLOCKCHAIN_CHAIN_ID: int = 137
    DEPLOYER_PRIVATE_KEY: str = ""
    ANOMALY_REGISTRY_ADDRESS: str = ""
    AUDIT_TRAIL_ADDRESS: str = ""
    RISK_SCORE_REGISTRY_ADDRESS: str = ""

    # ML
    ML_MODEL_PATH: str = "ml-engine/models"
    ISOLATION_FOREST_MODEL: str = "isolation_forest.pkl"
    AUTOENCODER_MODEL: str = "autoencoder.pt"
    ANOMALY_THRESHOLD: float = 0.7
    ENABLE_PYCARET: bool = True

    # LLM Server (Deprecated - now using Cortex directly)
    LLM_SERVER_URL: str = "http://localhost:8001"

    # Cortex API Configuration (Lloyds Internal Gemini)
    CORTEX_API_KEY: str = "ck_dev_PjgvIybRQB_cc9Y-IbpBy6u2DieHqksA382pOeyc2K0"
    CORTEX_BASE_URL: str = "https://cortex.lloydsbanking.cloud/api"
    CORTEX_MODEL: str = "gemini-2.5-flash-lite"
    CORTEX_TEMPERATURE: float = 0.2
    CORTEX_TIMEOUT: int = 120

    # Database
    DB_TYPE: str = "postgresql"  # Options: "postgresql" or "bigquery"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432  # Using default PostgreSQL port
    POSTGRES_DB: str = "WorkforceOne"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres "

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Detection Settings
    MAX_CONCURRENT_DETECTORS: int = 10
    DETECTION_TIMEOUT_SECONDS: int = 30
    ENABLE_BIGQUERY_STORAGE: bool = True
    ENABLE_NARRATIVE_GENERATION: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # API
    API_V1_PREFIX: str = "/api/v1"

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
