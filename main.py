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


tags_metadata = [
    {
        "name": "Anomalies",
        "description": (
            "Core anomaly detection endpoints. "
            "**Single detection**: `POST /detect` — run all 6 detectors on one transaction hash. "
            "**Bulk screening**: `POST /detect/bulk` — upload a CSV file with a `transaction_hash` column "
            "to screen up to 500 transactions in one request. "
            "Results endpoints let you list, filter, and retrieve stored anomaly records."
        ),
    },
    {
        "name": "Transactions",
        "description": "Ingest, list, and retrieve financial transactions.",
    },
    {
        "name": "Client Registry",
        "description": "Manage client profiles linked to transactions and anomaly results.",
    },
    {
        "name": "Narratives",
        "description": (
            "Generate human-readable AI narratives for anomaly results using SHAP explainability "
            "and Cortex/Gemini LLM integration."
        ),
    },
    {
        "name": "Blockchain",
        "description": "Blockchain transaction verification and on-chain record management.",
    },
    {
        "name": "Health",
        "description": "Service health check.",
    },
]

app = FastAPI(
    title="Blockchain Anomaly AI",
    description=(
        "## Real-time anomaly detection for financial transactions\n\n"
        "This API provides:\n"
        "- **Single-transaction anomaly detection** across 6 specialized rule-based detectors "
        "(Off-Hours, Threshold, Daily Limit, Reconciliation, Full Withdrawal, Time Window)\n"
        "- **Bulk CSV screening** — upload a CSV and detect anomalies for every transaction hash in one call\n"
        "- **SHAP explainability** — feature-level explanations for each anomaly score\n"
        "- **AI narratives** — LLM-generated compliance narratives per persona\n"
        "- **Blockchain verification** — on-chain record anchoring\n\n"
        "### Bulk Screening\n"
        "Upload a CSV file to `POST /api/v1/anomalies/detect/bulk`. "
        "The file must have a `transaction_hash` header column. Maximum **500 rows** per upload.\n\n"
        "```\ntransaction_hash\n0x001\n0x002\n0x003\n```"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
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
