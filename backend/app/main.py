from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.anomaly_routes import router as anomaly_router
from app.api.blockchain_routes import router as blockchain_router
from app.api.narrative_routes import router as narrative_router
from app.api.transaction_routes import router as transaction_router
from app.api.client_registry_routes import router as client_registry_router
from app.config.settings import settings
from app.core.database import init_db, close_db
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Blockchain Anomaly AI Backend...")
    
    # Initialize database if using PostgreSQL
    if settings.DB_TYPE.lower() in ["postgresql", "postgres"]:
        try:
            logger.info(f"Attempting to connect to PostgreSQL at {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
            await asyncio.wait_for(init_db(), timeout=10.0)
            logger.info("PostgreSQL database initialized successfully")
        except asyncio.TimeoutError:
            logger.error("Database initialization timed out after 10 seconds")
            logger.warning("Application will start without database connection")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            logger.warning("Application will start without database connection")
    
    yield
    
    # Cleanup
    if settings.DB_TYPE.lower() in ["postgresql", "postgres"]:
        try:
            await close_db()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Failed to close database: {e}")
    
    logger.info("Shutting down...")


app = FastAPI(
    title="Blockchain Anomaly AI",
    description="Real-time anomaly detection in financial transactions using ML and blockchain",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(transaction_router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(client_registry_router, prefix="/api/v1/clients", tags=["Client Registry"])
app.include_router(anomaly_router, prefix="/api/v1/anomalies", tags=["Anomalies"])
app.include_router(blockchain_router, prefix="/api/v1/blockchain", tags=["Blockchain"])
app.include_router(narrative_router, prefix="/api/v1/narratives", tags=["Narratives"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "blockchain-anomaly-ai-backend"}
