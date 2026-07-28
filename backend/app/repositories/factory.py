"""
Repository factory for switching between database backends.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseTransactionRepository
from app.repositories.postgres_repository import PostgresTransactionRepository
from app.repositories.bigquery_repository import BigQueryTransactionRepository
from app.repositories.anomaly_result_repository import AnomalyResultRepository
from app.repositories.bigquery_anomaly_repository import BigQueryAnomalyRepository
from app.repositories.client_registry_repository import ClientRegistryRepository
from app.repositories.bigquery_client_repository import BigQueryClientRepository
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)
settings = Settings()


class RepositoryFactory:
    """Factory for creating repositories based on configuration."""
    
    @staticmethod
    def get_transaction_repository(
        db_session: Optional[AsyncSession] = None
    ) -> BaseTransactionRepository:
        """
        Get the appropriate transaction repository based on configuration.
        
        Args:
            db_session: Optional PostgreSQL session (required if using PostgreSQL)
        
        Returns:
            BaseTransactionRepository implementation
        """
        db_type = settings.DB_TYPE.lower()
        
        if db_type == "postgresql" or db_type == "postgres":
            if db_session is None:
                raise ValueError("PostgreSQL session required for PostgreSQL repository")
            logger.info("Using PostgreSQL transaction repository")
            return PostgresTransactionRepository(db_session)
        
        elif db_type == "bigquery":
            logger.info("Using BigQuery transaction repository")
            return BigQueryTransactionRepository()
        
        else:
            logger.warning(f"Unknown DB_TYPE '{db_type}', defaulting to PostgreSQL")
            if db_session is None:
                raise ValueError("PostgreSQL session required for PostgreSQL repository")
            return PostgresTransactionRepository(db_session)
    
    @staticmethod
    def get_anomaly_repository(
        db_session: Optional[AsyncSession] = None
    ):
        """
        Get the appropriate anomaly results repository based on configuration.
        
        Args:
            db_session: Optional PostgreSQL session (required if using PostgreSQL)
        
        Returns:
            Anomaly repository implementation
        """
        db_type = settings.DB_TYPE.lower()
        
        if db_type == "postgresql" or db_type == "postgres":
            if db_session is None:
                raise ValueError("PostgreSQL session required for PostgreSQL repository")
            logger.info("Using PostgreSQL anomaly repository")
            return AnomalyResultRepository(db_session)
        
        elif db_type == "bigquery":
            logger.info("Using BigQuery anomaly repository")
            return BigQueryAnomalyRepository()
        
        else:
            logger.warning(f"Unknown DB_TYPE '{db_type}', defaulting to PostgreSQL")
            if db_session is None:
                raise ValueError("PostgreSQL session required for PostgreSQL repository")
            return AnomalyResultRepository(db_session)
    
    @staticmethod
    def get_client_repository(
        db_session: Optional[AsyncSession] = None
    ):
        """
        Get the appropriate client registry repository based on configuration.
        
        Args:
            db_session: Optional PostgreSQL session (required if using PostgreSQL)
        
        Returns:
            Client repository implementation
        """
        db_type = settings.DB_TYPE.lower()
        
        if db_type == "postgresql" or db_type == "postgres":
            if db_session is None:
                raise ValueError("PostgreSQL session required for PostgreSQL repository")
            logger.info("Using PostgreSQL client repository")
            return ClientRegistryRepository(db_session)
        
        elif db_type == "bigquery":
            logger.info("Using BigQuery client repository")
            return BigQueryClientRepository()
        
        else:
            logger.warning(f"Unknown DB_TYPE '{db_type}', defaulting to PostgreSQL")
            if db_session is None:
                raise ValueError("PostgreSQL session required for PostgreSQL repository")
            return ClientRegistryRepository(db_session)



async def get_transaction_repository(
    db_session: Optional[AsyncSession] = None
) -> BaseTransactionRepository:
    """
    FastAPI dependency for getting transaction repository.
    
    Usage in routes:
        @router.get("/")
        async def list_transactions(
            repo: BaseTransactionRepository = Depends(get_transaction_repository)
        ):
            ...
    """
    return RepositoryFactory.get_transaction_repository(db_session)
