from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import csv
import io

from app.services.anomaly.orchestrator import AnomalyOrchestrator
from app.services.anomaly.anomaly_result_service import AnomalyResultService
from app.repositories.factory import RepositoryFactory
from app.core.database import get_async_session
from app.config.settings import Settings
from app.utilities.logger.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = Settings()


@router.post("/bulk-detect", status_code=status.HTTP_200_OK)
async def bulk_detect_anomalies(
    file: UploadFile = File(..., description="CSV file with a 'transaction_hash' column"),
    db_session: AsyncSession = Depends(get_async_session),
):
    """
    Run anomaly detection for every transaction hash in an uploaded CSV file.
    CSV must contain a header row with at least a 'transaction_hash' column.
    Returns a summary: total processed, anomalies found, clean transactions, per-row errors.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8-sig")  # handle BOM
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

    if len(hashes) > 500:
        raise HTTPException(status_code=422, detail="Maximum 500 transaction hashes per upload.")

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
