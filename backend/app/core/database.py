"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from typing import AsyncGenerator, Generator
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)
settings = Settings()

# Async PostgreSQL engine
async_engine = create_async_engine(
    settings.postgres_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync engine for migrations (optional - only if psycopg2 is installed)
try:
    sync_engine = create_engine(
        settings.postgres_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
except Exception as e:
    logger.warning(f"Sync PostgreSQL engine not available (psycopg2 not installed): {e}")
    sync_engine = None
    SessionLocal = None


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Generator[Session, None, None]:
    """Dependency for sync database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_db():
    """Initialize database tables."""
    from app.models.base import Base
    # Import models to register them with Base
    from app.models.transaction import Transaction
    from app.models.client_registry import ClientRegistry
    from app.models.anomaly_result import AnomalyResult
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")


async def close_db():
    """Close database connections."""
    await async_engine.dispose()
    logger.info("Database connections closed")
