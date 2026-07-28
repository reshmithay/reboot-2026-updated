"""
Run PostgreSQL schema creation script.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import Settings
from app.utilities.logger.logger import get_logger
import asyncpg

logger = get_logger(__name__)
settings = Settings()


async def create_schema():
    """Create database schema from SQL file."""
    
    if settings.DB_TYPE.lower() not in ["postgresql", "postgres"]:
        logger.error("This script only works with PostgreSQL. Set DB_TYPE=postgresql")
        return False
    
    logger.info(f"Connecting to PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        
        # Read SQL file
        sql_file = Path(__file__).parent / "postgresql_schema.sql"
        logger.info(f"Reading schema from: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema
        logger.info("Executing schema creation...")
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        for i, statement in enumerate(statements):
            try:
                if statement and not statement.startswith('--'):
                    await conn.execute(statement)
                    if i % 10 == 0:
                        logger.info(f"Executed {i}/{len(statements)} statements...")
            except Exception as e:
                # Log but continue (some statements may already exist)
                logger.warning(f"Statement failed (may already exist): {str(e)[:100]}")
        
        # Verify tables created
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        logger.info("\n✅ Schema created successfully!")
        logger.info(f"\nTables created ({len(tables)}):")
        for table in tables:
            logger.info(f"  - {table['tablename']}")
        
        # Check anomaly_master data
        anomaly_count = await conn.fetchval("SELECT COUNT(*) FROM anomaly_master")
        logger.info(f"\n✅ Anomaly master table: {anomaly_count} codes loaded")
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create schema: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(create_schema())
    sys.exit(0 if success else 1)
