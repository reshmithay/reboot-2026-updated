"""
Database initialization script.
Run this to create tables and seed initial data.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db, close_db
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)
settings = Settings()


async def main():
    """Initialize database tables."""
    if settings.DB_TYPE.lower() not in ["postgresql", "postgres"]:
        logger.error("This script only works with PostgreSQL. Set DB_TYPE=postgresql in your .env")
        return
    
    logger.info("Initializing PostgreSQL database...")
    logger.info(f"Database: {settings.POSTGRES_DB}")
    logger.info(f"Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    
    try:
        await init_db()
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
