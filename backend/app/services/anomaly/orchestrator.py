"""
Anomaly detection orchestrator - runs all detectors and aggregates results.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import asyncio

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult
from app.services.anomaly.detectors.off_hours_detector import OffHoursWithdrawalDetector
from app.services.anomaly.detectors.threshold_deposit_detector import ThresholdDepositDetector
from app.services.anomaly.detectors.duplicate_escrow_detector import DuplicateEscrowDetector
from app.services.anomaly.detectors.oracle_detector import OracleDetector
from app.services.anomaly.detectors.daily_limit_detector import DailyLimitDetector
from app.services.anomaly.detectors.reconciliation_detector import ReconciliationDetector
from app.services.anomaly.detectors.full_withdrawal_detector import FullWithdrawalDetector
from app.services.anomaly.detectors.time_window_detector import TimeWindowDetector
from app.clients.bigquery.reference_data_client import BigQueryReferenceClient
from app.repositories.reference_data_repository import PostgresReferenceDataRepository
from app.config.settings import settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class AnomalyOrchestrator:
    """Orchestrates multiple anomaly detectors and aggregates results."""
    
    def __init__(self, config: Dict[str, Any] = None, anomaly_result_service=None, db_session=None):
        self.config = config or {}
        self.anomaly_result_service = anomaly_result_service  # Optional PostgreSQL storage
        self.anomaly_master: Dict[str, Dict[str, Any]] = {}
        
        # Initialize reference data client based on DB_TYPE setting
        if settings.DB_TYPE.lower() == "postgresql":
            if db_session is None:
                logger.warning("PostgreSQL session not provided, falling back to BigQuery")
                self.ref_client = BigQueryReferenceClient()
            else:
                self.ref_client = PostgresReferenceDataRepository(db_session)
                logger.info("Using PostgreSQL for reference data")
        else:
            self.ref_client = BigQueryReferenceClient()
            logger.info("Using BigQuery for reference data")
        self.anomaly_result_service = anomaly_result_service  # Optional PostgreSQL storage
        
        # Initialize all detectors (for CSV upload)
        self.all_detectors: List[BaseDetector] = [
            OffHoursWithdrawalDetector(self.config.get("off_hours", {})),
            ThresholdDepositDetector(self.config.get("threshold_deposit", {})),
            DuplicateEscrowDetector(self.config.get("duplicate_escrow", {})),
            OracleDetector(self.config.get("oracle", {})),
            DailyLimitDetector(self.config.get("daily_limit", {})),
            ReconciliationDetector(self.config.get("reconciliation", {})),
            FullWithdrawalDetector(self.config.get("full_withdrawal", {})),
            TimeWindowDetector(self.config.get("time_window", {})),
        ]
        
        # API detectors (6 specified detectors for API-based detection)
        self.api_detectors: List[BaseDetector] = [
            OffHoursWithdrawalDetector(self.config.get("off_hours", {})),
            ThresholdDepositDetector(self.config.get("threshold_deposit", {})),
            DailyLimitDetector(self.config.get("daily_limit", {})),
            ReconciliationDetector(self.config.get("reconciliation", {})),
            FullWithdrawalDetector(self.config.get("full_withdrawal", {})),
            TimeWindowDetector(self.config.get("time_window", {})),
        ]
        
        # Default to all detectors (for CSV)
        self.detectors = self.all_detectors
        
        logger.info(f"Initialized {len(self.all_detectors)} detectors (CSV), {len(self.api_detectors)} detectors (API)")
    
    async def initialize(self):
        """Initialize anomaly master table."""
        self.anomaly_master = await self.ref_client.get_anomaly_master()
        logger.info(f"Loaded {len(self.anomaly_master)} anomaly codes from {settings.DB_TYPE}")
    
    async def detect_by_transaction_hash(
        self,
        transaction_hash: str,
        transaction_repo=None
    ) -> Dict[str, Any]:
        """
        Detect anomalies for a transaction identified by hash.
        Uses 6 specialized detectors for API-based detection.
        
        Args:
            transaction_hash: Transaction hash to analyze
            transaction_repo: Transaction repository (PostgreSQL or BigQuery)
            
        Returns:
            Anomaly detection result in anomaly_results table format
        """
        # Ensure anomaly master is loaded
        if not self.anomaly_master:
            await self.initialize()
        
        # Fetch transaction from database
        if transaction_repo is None:
            raise ValueError("Transaction repository is required")
        
        transaction_data = await transaction_repo.get_by_hash(transaction_hash)
        if not transaction_data:
            raise ValueError(f"Transaction not found for hash: {transaction_hash}")
        
        logger.info(f"Running API-based anomaly detection for transaction hash: {transaction_hash}")
        logger.info(f"Using {len(self.api_detectors)} specialized detectors for API detection")
        
        # Prepare context with reference data
        try:
            context = await self._prepare_context(transaction_data)
        except Exception as e:
            logger.error(f"Failed to prepare context: {e}")
            context = {"client_registry": {}}
        
        # Run API detectors (6 specialized detectors)
        results: List[AnomalyResult] = []
        for detector in self.api_detectors:
            try:
                result = await detector.detect(transaction_data, context)
                results.append(result)
                if result.is_anomaly:
                    logger.info(f"  {detector.name}: ANOMALY (confidence: {result.confidence:.2f})")
            except Exception as e:
                logger.error(f"{detector.name} failed: {e}", exc_info=True)
                # Continue with other detectors
        
        # Aggregate results
        aggregated = self._aggregate_results(transaction_data, results, context)
        
        # Store results in BigQuery and PostgreSQL
        if aggregated.get("is_anomaly"):
            await self._store_results(aggregated)
        
        # Convert to anomaly_results table format
        return self._convert_to_anomaly_result_format(aggregated, transaction_data)
    
    async def detect_all(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all detectors on a transaction and aggregate results.
        Uses all 8 detectors for CSV-based detection.
        
        Args:
            transaction: Transaction data to analyze
            
        Returns:
            Aggregated anomaly report with individual detector results
        """
        # Ensure anomaly master is loaded
        if not self.anomaly_master:
            await self.initialize()
        
        logger.info(f"Running CSV-based anomaly detection with {len(self.detectors)} detectors")
        
        # Prepare context with reference data from BigQuery
        try:
            context = await self._prepare_context(transaction)
        except Exception as e:
            logger.error(f"Failed to prepare context: {e}")
            context = {"client_registry": {}}
        
        # Run all detectors
        results: List[AnomalyResult] = []
        for detector in self.detectors:
            try:
                result = await detector.detect(transaction, context)
                results.append(result)
            except Exception as e:
                logger.error(f"{detector.name} failed: {e}")
                # Continue with other detectors
        
        # Aggregate results
        aggregated = self._aggregate_results(transaction, results, context)
        
        # Store in BigQuery
        if self.config.get("store_results", True):
            await self._store_results(aggregated)
        
        return aggregated
    
    async def _prepare_context(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context data for detectors using configured data source (PostgreSQL or BigQuery)."""
        from_address = transaction.get("from_wallet_address")
        client_id = transaction.get("client_id")
        
        context = {}
        
        try:
            # Fetch client registry (respects DB_TYPE setting)
            if client_id:
                client_registry = await self.ref_client.get_client_registry_by_id(client_id)
            else:
                client_registry = await self.ref_client.get_client_registry(from_address)
            
            # Store in context with both formats for detector compatibility
            context["client_registry"] = {client_id or from_address: client_registry}
            
            # Use client-specific limits from registry
            context["account_limits"] = {
                from_address: {
                    "daily_value_limit": client_registry.get("dailyWithdrawalLimit", 50000),
                    "daily_count_limit": 100,
                    "per_address_value_limit": client_registry.get("dailyWithdrawalLimit", 25000)
                }
            }
            
            # Fetch recent transactions
            recent_txs = await self.ref_client.get_recent_transactions(from_address, lookback_hours=24)
            context["recent_transactions"] = recent_txs
            
            # Fetch account balance
            balance = await self.ref_client.get_account_balance(from_address)
            context["account_balance"] = {from_address: balance}
            
            # Oracle registry (only if BigQuery client supports it)
            if hasattr(self.ref_client, 'get_oracle_registry'):
                context["oracle_registry"] = await self.ref_client.get_oracle_registry()
            else:
                context["oracle_registry"] = set()
            
            # Calculate derived metrics
            if recent_txs:
                context["tx_count_1h"] = len([
                    tx for tx in recent_txs 
                    if (datetime.utcnow() - datetime.fromisoformat(tx["timestamp"])).total_seconds() < 3600
                ])
                context["unique_counterparties"] = len(set(tx["to_address"] for tx in recent_txs))
            
        except Exception as e:
            logger.warning(f"Failed to fetch complete context: {e}")
        
        return context
    
    def _aggregate_results(self, transaction: Dict, results: List[AnomalyResult], context: Dict) -> Dict[str, Any]:
        """Aggregate detection results into final report."""
        # Filter anomalies
        anomalies = [r for r in results if r.is_anomaly]
        
        detection_id = str(uuid.uuid4())
        client_registry = context.get("client_registry", {})
        
        if not anomalies:
            return {
                "detection_id": detection_id,
                "transaction_id": transaction.get("transaction_hash") or transaction.get("tx_hash"),
                "is_anomaly": False,
                "overall_score": 0.0,
                "overall_severity": "low",
                "risk_score": 0,
                "anomaly_count": 0,
                "anomaly_codes": [],
                "detections": [],
                "all_reasons": [],
                "detailed_reasons": [],
                "client_registry": client_registry,
                "detected_at": datetime.utcnow().isoformat()
            }
        
        # Calculate overall score (max confidence)
        overall_score = max(r.confidence for r in anomalies)
        
        # Collect anomaly codes and enrich with master data
        anomaly_codes = [r.anomaly_code for r in anomalies if r.anomaly_code]
        
        # Calculate risk score from anomaly master
        total_risk_score = 0
        for code in anomaly_codes:
            if code in self.anomaly_master:
                total_risk_score += self.anomaly_master[code].get("risk_score", 50)
        
        avg_risk_score = total_risk_score // len(anomaly_codes) if anomaly_codes else 0
        
        # Calculate overall severity
        severity_priority = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        overall_severity = max(anomalies, key=lambda r: severity_priority[r.severity]).severity
        
        # Collect all reasons with scores
        all_reasons = []
        detailed_reasons = []
        for result in anomalies:
            all_reasons.extend(result.reasons)
            # Add detailed reasons with scores
            for reason in result.reasons:
                detailed_reasons.append({
                    "reasonCode": result.anomaly_code or "ANOMALY",
                    "description": reason,
                    "score": result.confidence
                })
        
        # Build detection summary with anomaly master enrichment
        detections = []
        for r in anomalies:
            detection = {
                "detector": r.detector_name,
                "confidence": r.confidence,
                "severity": r.severity,
                "anomaly_code": r.anomaly_code,
                "reasons": r.reasons,
                "metadata": r.metadata
            }
            
            # Enrich with master data
            if r.anomaly_code and r.anomaly_code in self.anomaly_master:
                master = self.anomaly_master[r.anomaly_code]
                detection["category"] = master.get("category")
                detection["risk_score"] = master.get("risk_score")
                detection["description"] = master.get("description")
            
            detections.append(detection)
        
        return {
            "detection_id": detection_id,
            "transaction_id": transaction.get("transaction_hash") or transaction.get("tx_hash"),
            "is_anomaly": True,
            "overall_score": overall_score,
            "overall_severity": overall_severity,
            "risk_score": avg_risk_score,
            "anomaly_count": len(anomalies),
            "anomaly_codes": anomaly_codes,
            "detections": detections,
            "all_reasons": all_reasons,
            "detailed_reasons": detailed_reasons,  # Reasons with scores
            "client_registry": client_registry,
            "detected_at": datetime.utcnow().isoformat(),
            "transaction_summary": {
                "from": transaction.get("from_wallet_address") or transaction.get("from_address"),
                "to": transaction.get("to_wallet_address") or transaction.get("to_address"),
                "value": transaction.get("amount") or transaction.get("value"),
                "timestamp": transaction.get("transaction_timestamp") or transaction.get("timestamp")
            }
        }
    
    async def _store_results(self, aggregated: Dict[str, Any]):
        """Store detection results in BigQuery and optionally PostgreSQL."""
        try:
            await self.bq_client.store_anomaly_detection(aggregated)
        except Exception as e:
            logger.error(f"Failed to store detection results in BigQuery: {e}")
        
        # Also store in PostgreSQL anomaly_results table if service available
        if self.anomaly_result_service and aggregated.get("is_anomaly"):
            try:
                # Extract anomaly types and reasons from detections
                anomaly_types = aggregated.get("anomaly_codes", [])
                # Use detailed_reasons which includes scores
                anomaly_reasons = aggregated.get("detailed_reasons", [])
                
                # Get transaction summary
                tx_summary = aggregated.get("transaction_summary", {})
                
                # Prepare transaction dict for storage
                transaction_data = {
                    "transaction_id": aggregated.get("transaction_id"),
                    "transaction_hash": aggregated.get("transaction_id"),
                    "client_id": aggregated.get("client_registry", {}).get("client_id"),
                    "amount": tx_summary.get("value"),
                    "currency": "INR",
                    "from_wallet_address": tx_summary.get("from"),
                    "to_wallet_address": tx_summary.get("to"),
                    "transaction_type": "BLOCKCHAIN",
                }
                
                await self.anomaly_result_service.store_anomaly_result(
                    transaction=transaction_data,
                    anomaly_score=aggregated.get("overall_score", 0.0),
                    anomaly_types=anomaly_types,
                    anomaly_reasons=anomaly_reasons,
                    confidence=aggregated.get("overall_score", 0.0),
                    model_name="Ensemble",
                    model_version="v1.0"
                )
                logger.info(f"Stored anomaly result in PostgreSQL for transaction {transaction_data['transaction_id']}")
            except Exception as e:
                logger.error(f"Failed to store anomaly result in PostgreSQL: {e}", exc_info=True)
    
    def _convert_to_anomaly_result_format(
        self,
        aggregated: Dict[str, Any],
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert aggregated detection results to anomaly_results table format.
        
        Args:
            aggregated: Aggregated detection results
            transaction_data: Original transaction data
            
        Returns:
            Anomaly result in anomaly_results table format
        """
        # Extract client info
        client_id = transaction_data.get("client_id") or aggregated.get("client_registry", {}).get("client_id")
        
        # Determine anomaly category from codes
        anomaly_codes = aggregated.get("anomaly_codes", [])
        anomaly_category = "FRAUD"  # Default
        if anomaly_codes:
            # Map first code to category using anomaly master
            first_code = anomaly_codes[0]
            if first_code in self.anomaly_master:
                anomaly_category = self.anomaly_master[first_code].get("category", "FRAUD")
        
        # Severity mapping
        severity_map = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW"
        }
        
        return {
            "anomalyId": aggregated.get("detection_id"),
            "transactionId": transaction_data.get("transaction_id"),
            "transactionHash": transaction_data.get("transaction_hash"),
            "clientId": client_id,
            "amount": float(transaction_data.get("amount", 0)),
            "currency": transaction_data.get("currency", "INR"),
            "fromAccount": transaction_data.get("from_account"),
            "toAccount": transaction_data.get("to_account"),
            "fromWalletAddress": transaction_data.get("from_wallet_address"),
            "toWalletAddress": transaction_data.get("to_wallet_address"),
            "transactionType": transaction_data.get("transaction_type", "BLOCKCHAIN"),
            "anomalyScore": aggregated.get("overall_score", 0.0),
            "severity": severity_map.get(aggregated.get("overall_severity", "low"), "LOW"),
            "anomalyCategory": anomaly_category,
            "anomalyTypes": anomaly_codes,
            "anomalyReasons": aggregated.get("detailed_reasons", []),
            "confidence": aggregated.get("overall_score", 0.0),
            "modelName": "Ensemble",
            "modelVersion": "v1.0",
            "reviewStatus": "PENDING",
            "assignedTo": None,
            "caseId": None,
            "detectedAt": aggregated.get("detected_at"),
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
        }
