from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import csv
import io

from app.schemas.anomaly_schema import (
    AnomalyDetectRequest,
    AnomalyResponse,
    AnomalyListResponse,
    AnomalyResultResponse,
    AnomalyResultListResponse
)
from app.schemas.narrative_schemas import (
    ShapFeaturesResponse,
    NarrativeGenerateRequest,
    NarrativeResponse
)
from app.services.anomaly.anomaly_service import AnomalyService
from app.services.anomaly.orchestrator import AnomalyOrchestrator
from app.services.anomaly.anomaly_result_service import AnomalyResultService
from app.services.shap_explainer_service import ShapExplainerService
from app.services.narrative_service import ShapNarrativeService
from app.repositories.factory import RepositoryFactory
from app.core.database import get_async_session
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)
settings = Settings()


def get_anomaly_result_repository(db_session: Optional[AsyncSession] = Depends(get_async_session)):
    """Dependency to get AnomalyResultRepository (PostgreSQL or BigQuery based on config)."""
    if settings.DB_TYPE.lower() == "bigquery":
        return RepositoryFactory.get_anomaly_repository()
    return RepositoryFactory.get_anomaly_repository(db_session)


def get_transaction_repository(db_session: Optional[AsyncSession] = Depends(get_async_session)):
    """Dependency to get TransactionRepository (PostgreSQL or BigQuery based on config)."""
    if settings.DB_TYPE.lower() == "bigquery":
        return RepositoryFactory.get_transaction_repository()
    return RepositoryFactory.get_transaction_repository(db_session)


@router.post("/detect", response_model=AnomalyResultResponse, status_code=status.HTTP_201_CREATED)
async def detect_anomaly(
    payload: AnomalyDetectRequest,
    db_session: AsyncSession = Depends(get_async_session),
):
    """
    Run anomaly detection on a **single transaction** by its hash.

    Executes all 6 detectors in parallel:
    - **Off-Hours** — transaction outside business hours
    - **Threshold** — amount near reporting thresholds (structuring)
    - **Daily Limit** — cumulative daily volume breach
    - **Reconciliation** — unmatched or delayed counterpart transaction
    - **Full Withdrawal** — complete balance drain
    - **Time Window** — burst activity within a short window

    Results are stored and returned in `anomaly_results` format.
    Use `force=true` to re-run detection even if a result already exists.
    """
    try:
        if settings.DB_TYPE.lower() == "bigquery":
            transaction_repo = RepositoryFactory.get_transaction_repository()
            anomaly_result_repo = RepositoryFactory.get_anomaly_repository()
        else:
            # Force both repositories to share the exact same request-scoped session.
            transaction_repo = RepositoryFactory.get_transaction_repository(db_session)
            anomaly_result_repo = RepositoryFactory.get_anomaly_repository(db_session)

        # Initialize anomaly result service for storage
        anomaly_result_service = AnomalyResultService(anomaly_result_repo)
        
        # Initialize orchestrator with the service for storage and db_session
        orchestrator = AnomalyOrchestrator(
            config={"store_results": True},
            anomaly_result_service=anomaly_result_service,
            db_session=db_session  # Pass session for PostgreSQL reference data
        )
        
        # Run detection by transaction hash
        result = await orchestrator.detect_by_transaction_hash(
            transaction_hash=payload.transaction_hash,
            transaction_repo=transaction_repo
        )
        
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect/bulk", status_code=status.HTTP_200_OK)
async def bulk_detect_anomalies(
    file: UploadFile = File(..., description="CSV file with a 'transaction_hash' column"),
    db_session: AsyncSession = Depends(get_async_session),
):
    """
    Screen **multiple transactions** by uploading a CSV file.

    **CSV format requirements:**
    - Must have a header row containing `transaction_hash`
    - Maximum **100 rows** per upload.
    - UTF-8 or Latin-1 encoding, BOM is handled automatically

    **Example CSV:**
    ```
    transaction_hash
    0xabc123...
    0xdef456...
    ```

    **Response includes:**
    - `total` — number of hashes processed
    - `anomalies_found` — transactions flagged as anomalous
    - `clean` — transactions with no anomaly detected
    - `errors` — hashes that could not be processed (not found, etc.)
    - `results` — per-hash breakdown with `anomaly_id`, `anomaly_score`, `severity`
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw_bytes.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if "transaction_hash" not in (reader.fieldnames or []):
        raise HTTPException(
            status_code=422,
            detail="CSV must contain a 'transaction_hash' column header.",
        )

    hashes: List[str] = [
        row["transaction_hash"].strip()
        for row in reader
        if row.get("transaction_hash", "").strip()
    ]

    if not hashes:
        raise HTTPException(status_code=422, detail="No transaction hashes found in the CSV file.")
    if len(hashes) > 100:
        raise HTTPException(status_code=422, detail="Maximum 100 transaction hashes per upload.")

    if settings.DB_TYPE.lower() == "bigquery":
        transaction_repo = RepositoryFactory.get_transaction_repository()
        anomaly_result_repo = RepositoryFactory.get_anomaly_repository()
    else:
        transaction_repo = RepositoryFactory.get_transaction_repository(db_session)
        anomaly_result_repo = RepositoryFactory.get_anomaly_repository(db_session)

    anomaly_result_service = AnomalyResultService(anomaly_result_repo)
    orchestrator = AnomalyOrchestrator(
        config={"store_results": True},
        anomaly_result_service=anomaly_result_service,
        db_session=db_session,
    )

    total = len(hashes)
    anomalies_found = 0
    clean = 0
    errors: List[dict] = []
    results: List[dict] = []

    for tx_hash in hashes:
        try:
            result = await orchestrator.detect_by_transaction_hash(
                transaction_hash=tx_hash,
                transaction_repo=transaction_repo,
            )
            is_anomaly = result.get("isAnomaly", False)
            if is_anomaly:
                anomalies_found += 1
            else:
                clean += 1
            results.append({
                "transaction_hash": tx_hash,
                "anomaly_id": result.get("anomalyId"),
                "is_anomaly": is_anomaly,
                "anomaly_score": result.get("anomalyScore"),
                "severity": result.get("severity"),
            })
        except Exception as exc:
            logger.warning(f"bulk-detect: failed for hash {tx_hash}: {exc}")
            errors.append({"transaction_hash": tx_hash, "error": str(exc)})

    return {
        "status": "completed",
        "total": total,
        "anomalies_found": anomalies_found,
        "clean": clean,
        "error_count": len(errors),
        "errors": errors,
        "results": results,
    }


@router.get("/results/", response_model=AnomalyResultListResponse)
async def list_anomaly_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    severity: str = Query(None),
    review_status: str = Query(None),
    anomaly_category: str = Query(None),
    client_id: str = Query(None),
    start_date: Optional[str] = Query(None, description="Filter by created_at >= start_date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by created_at <= end_date (ISO format)"),
    repo = Depends(get_anomaly_result_repository),
):
    """List anomaly detection results with filters and date range."""
    try:
        # Parse date strings to datetime objects (strip timezone for PostgreSQL compatibility)
        start_datetime = None
        end_datetime = None
        if start_date:
            from datetime import datetime
            parsed = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            start_datetime = parsed.replace(tzinfo=None)  # Strip timezone for TIMESTAMP WITHOUT TIME ZONE
        if end_date:
            from datetime import datetime
            parsed = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            end_datetime = parsed.replace(tzinfo=None)  # Strip timezone for TIMESTAMP WITHOUT TIME ZONE
        
        result = await repo.list(
            page=page,
            page_size=page_size,
            severity=severity,
            review_status=review_status,
            anomaly_category=anomaly_category,
            client_id=client_id,
            start_date=start_datetime,
            end_date=end_datetime
        )
        return result
    except Exception as e:
        logger.error(f"Failed to list anomaly results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{anomaly_id}", response_model=AnomalyResultResponse)
async def get_anomaly_result(
    anomaly_id: str,
    repo = Depends(get_anomaly_result_repository),
):
    """Get anomaly result by ID."""
    result = await repo.get_by_id(anomaly_id)
    if not result:
        raise HTTPException(status_code=404, detail="Anomaly result not found")
    return result


@router.get("/results/transaction/{transaction_id}", response_model=AnomalyResultResponse)
async def get_anomaly_by_transaction(
    transaction_id: str,
    repo = Depends(get_anomaly_result_repository),
):
    """Get anomaly result by transaction ID."""
    result = await repo.get_by_transaction_id(transaction_id)
    if not result:
        raise HTTPException(status_code=404, detail="No anomaly found for this transaction")
    return result


@router.get("/", response_model=AnomalyListResponse)
async def list_anomalies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: str = Query(None),
    service: AnomalyService = Depends(),
):
    """List detected anomalies with optional severity filter (legacy endpoint)."""
    return await service.list_anomalies(page, page_size, severity)


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: str, service: AnomalyService = Depends()):
    """Get anomaly details by ID (legacy endpoint)."""
    result = await service.get_anomaly(anomaly_id)
    if not result:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return result


@router.get("/stats/summary")
async def anomaly_stats(
    repo = Depends(get_anomaly_result_repository),
):
    """Get anomaly detection statistics."""
    try:
        by_severity = await repo.count_by_severity()
        by_status = await repo.count_by_review_status()
        total = await repo.get_total_count()
        avg_score = await repo.get_avg_anomaly_score()
        
        return {
            "total_anomalies": total,
            "critical": by_severity.get("CRITICAL", 0),
            "high": by_severity.get("HIGH", 0),
            "medium": by_severity.get("MEDIUM", 0),
            "low": by_severity.get("LOW", 0),
            "under_review": by_status.get("UNDER_REVIEW", 0),
            "pending": by_status.get("PENDING", 0),
            "approved": by_status.get("APPROVED", 0),
            "rejected": by_status.get("REJECTED", 0),
            "avg_anomaly_score": avg_score,
            "by_severity": by_severity,
            "by_review_status": by_status,
        }
    except Exception as e:
        logger.error(f"Failed to get anomaly stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shap/{anomaly_id}", response_model=ShapFeaturesResponse)
async def get_shap_features(
    anomaly_id: str,
    top_k: int = Query(5, ge=1, le=10),
    anomaly_repo = Depends(get_anomaly_result_repository),
    transaction_repo = Depends(get_transaction_repository),
):
    """
    Get SHAP feature contributions for an anomaly.
    
    This endpoint computes or retrieves SHAP values that explain
    which features contributed most to the anomaly detection.
    """
    try:
        # Fetch anomaly result
        anomaly = await anomaly_repo.get_by_id(anomaly_id)
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        # Fetch transaction
        transaction = await transaction_repo.get_by_hash(anomaly.get("transactionHash"))
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Extract transaction features
        # Parse timestamp if it's a string
        tx_timestamp = transaction.get("transaction_timestamp")
        if tx_timestamp:
            if isinstance(tx_timestamp, str):
                try:
                    tx_timestamp = datetime.fromisoformat(tx_timestamp.replace('Z', '+00:00'))
                except:
                    tx_timestamp = datetime.utcnow()
            transaction_hour = tx_timestamp.hour
        else:
            transaction_hour = 12
        
        # Encode transaction type as numeric (for SHAP)
        tx_type = transaction.get("transaction_type", "").upper()
        tx_type_encoded = 0  # Default
        if "WITHDRAWAL" in tx_type:
            tx_type_encoded = 2
        elif "TRANSFER" in tx_type:
            tx_type_encoded = 1
        elif "DEPOSIT" in tx_type:
            tx_type_encoded = 0
        
        transaction_features = {
            "amount": float(transaction.get("amount", 0)),
            "transaction_hour": transaction_hour,
            "transaction_type": tx_type_encoded,
            "daily_transaction_count": int(transaction.get("daily_transaction_count", 0)),
            "account_balance": float(transaction.get("account_balance", 0)),
            "withdrawal_percentage": float(transaction.get("withdrawal_percentage", 0)),
            "time_since_last_transaction": int(transaction.get("time_since_last_transaction", 0)),
        }
        
        # Initialize SHAP explainer service
        shap_service = ShapExplainerService()
        
        # Compute SHAP values
        shap_contributors = shap_service.compute_shap_values(
            transaction_features=transaction_features,
            anomaly_score=anomaly.get("anomalyScore", 0.0),
            top_k=top_k,
        )
        
        # Determine risk label
        anomaly_score = anomaly.get("anomalyScore", 0.0)
        if anomaly_score >= 0.8:
            risk_label = "Critical Risk"
        elif anomaly_score >= 0.6:
            risk_label = "High Risk"
        elif anomaly_score >= 0.4:
            risk_label = "Medium Risk"
        else:
            risk_label = "Low Risk"
        
        return ShapFeaturesResponse(
            anomaly_id=anomaly_id,
            transaction_hash=anomaly.get("transactionHash", ""),
            prediction_probability=anomaly_score,
            prediction_label=risk_label,
            shap_contributors=shap_contributors,
            anomaly_score=anomaly_score,
            anomaly_category=anomaly.get("anomalyCategory", "Unknown"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compute SHAP features: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/narrative/generate", response_model=NarrativeResponse)
async def generate_narrative(
    request: NarrativeGenerateRequest,
    anomaly_repo = Depends(get_anomaly_result_repository),
    transaction_repo = Depends(get_transaction_repository),
):
    """
    Generate AI narrative for an anomaly using SHAP values and Cortex/Gemini.
    
    This endpoint:
    1. Fetches SHAP features for the anomaly
    2. Calls local narrative service (Cortex AI)
    3. Returns the generated explanation
    """
    try:
        # First, get anomaly and transaction data
        anomaly = await anomaly_repo.get_by_id(request.anomaly_id)
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        transaction = await transaction_repo.get_by_hash(anomaly.get("transactionHash"))
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Extract features and compute SHAP
        # Parse timestamp if it's a string
        tx_timestamp = transaction.get("transaction_timestamp")
        if tx_timestamp:
            if isinstance(tx_timestamp, str):
                try:
                    tx_timestamp = datetime.fromisoformat(tx_timestamp.replace('Z', '+00:00'))
                except:
                    tx_timestamp = datetime.utcnow()
            transaction_hour = tx_timestamp.hour
        else:
            transaction_hour = 12
        
        # Encode transaction type as numeric (for SHAP)
        tx_type = transaction.get("transaction_type", "").upper()
        tx_type_encoded = 0  # Default
        if "WITHDRAWAL" in tx_type:
            tx_type_encoded = 2
        elif "TRANSFER" in tx_type:
            tx_type_encoded = 1
        elif "DEPOSIT" in tx_type:
            tx_type_encoded = 0
        
        transaction_features = {
            "amount": float(transaction.get("amount", 0)),
            "transaction_hour": transaction_hour,
            "transaction_type": tx_type_encoded,
            "daily_transaction_count": int(transaction.get("daily_transaction_count", 0)),
            "account_balance": float(transaction.get("account_balance", 0)),
            "withdrawal_percentage": float(transaction.get("withdrawal_percentage", 0)),
            "time_since_last_transaction": int(transaction.get("time_since_last_transaction", 0)),
        }
        
        shap_service = ShapExplainerService()
        shap_contributors = shap_service.compute_shap_values(
            transaction_features=transaction_features,
            anomaly_score=anomaly.get("anomalyScore", 0.0),
            top_k=request.top_k,
        )
        
        # Determine risk label
        anomaly_score = anomaly.get("anomalyScore", 0.0)
        if anomaly_score >= 0.8:
            risk_label = "Critical Risk"
        elif anomaly_score >= 0.6:
            risk_label = "High Risk"
        elif anomaly_score >= 0.4:
            risk_label = "Medium Risk"
        else:
            risk_label = "Low Risk"
        
        # Generate narrative using local service with persona
        narrative_service = ShapNarrativeService()
        response = narrative_service.generate_narrative(
            anomaly_id=request.anomaly_id,
            shap_contributors=shap_contributors,
            prediction_probability=anomaly_score,
            prediction_label=risk_label,
            top_k=request.top_k,
            persona=request.persona,  # Use persona from request
        )
        
        return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate narrative: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
