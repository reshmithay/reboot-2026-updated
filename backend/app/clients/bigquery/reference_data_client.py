"""
BigQuery reference data client for fetching default thresholds, limits, and registries.
"""
from google.cloud import bigquery
from typing import Dict, Any, List, Set, Optional
from datetime import datetime, timedelta
import os

from app.config.settings import settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class BigQueryReferenceClient:
    """Client for fetching reference data from BigQuery."""
    
    def __init__(self):
        self.project_id = settings.BIGQUERY_PROJECT_ID
        self.dataset = settings.BIGQUERY_DATASET
        self.client: Optional[bigquery.Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize BigQuery client."""
        try:
            # If credentials are set, use them
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                self.client = bigquery.Client(project=self.project_id)
                logger.info("BigQuery client initialized successfully")
            else:
                logger.warning("BigQuery credentials not found, using fallback defaults")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            self.client = None
    
    async def get_account_limits(self, address: str) -> Dict[str, float]:
        """Fetch account-specific limits from BigQuery."""
        if not self.client:
            return self._get_default_limits()
        
        try:
            query = f"""
            SELECT
                daily_value_limit,
                daily_count_limit,
                per_address_value_limit
            FROM `{self.project_id}.{self.dataset}.account_limits`
            WHERE address = @address
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address.lower())
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                return {
                    "daily_value_limit": float(row.daily_value_limit),
                    "daily_count_limit": int(row.daily_count_limit),
                    "per_address_value_limit": float(row.per_address_value_limit)
                }
        except Exception as e:
            logger.error(f"Failed to fetch account limits from BigQuery: {e}")
        
        return self._get_default_limits()
    
    async def get_oracle_registry(self) -> Set[str]:
        """Fetch recognized oracle addresses from BigQuery."""
        if not self.client:
            return self._get_default_oracles()
        
        try:
            query = f"""
            SELECT DISTINCT oracle_address
            FROM `{self.project_id}.{self.dataset}.oracle_registry`
            WHERE is_active = TRUE
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            return {row.oracle_address.lower() for row in results}
        except Exception as e:
            logger.error(f"Failed to fetch oracle registry from BigQuery: {e}")
        
        return self._get_default_oracles()
    
    async def get_recent_transactions(
        self, address: str, lookback_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Fetch recent transactions for an address."""
        if not self.client:
            return []
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
            
            query = f"""
            SELECT
                tx_hash,
                from_address,
                to_address,
                value,
                timestamp,
                gas_ratio,
                is_contract_interaction,
                token_symbol
            FROM `{self.project_id}.{self.dataset}.transactions`
            WHERE from_address = @address
              AND timestamp >= @cutoff_time
            ORDER BY timestamp DESC
            LIMIT 1000
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address.lower()),
                    bigquery.ScalarQueryParameter("cutoff_time", "TIMESTAMP", cutoff_time)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            transactions = []
            for row in results:
                transactions.append({
                    "tx_hash": row.tx_hash,
                    "from_address": row.from_address,
                    "to_address": row.to_address,
                    "value": float(row.value),
                    "timestamp": row.timestamp.isoformat(),
                    "gas_ratio": float(row.gas_ratio) if row.gas_ratio else 0.5,
                    "is_contract_interaction": bool(row.is_contract_interaction),
                    "token_symbol": row.token_symbol
                })
            
            return transactions
        except Exception as e:
            logger.error(f"Failed to fetch transactions from BigQuery: {e}")
            return []
    
    async def get_account_balance(self, address: str) -> float:
        """Fetch current account balance."""
        if not self.client:
            return 0.0
        
        try:
            query = f"""
            SELECT balance
            FROM `{self.project_id}.{self.dataset}.account_balances`
            WHERE address = @address
            ORDER BY updated_at DESC
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("address", "STRING", address.lower())
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                return float(results[0].balance)
        except Exception as e:
            logger.error(f"Failed to fetch account balance from BigQuery: {e}")
        
        return 0.0
    
    def _get_default_limits(self) -> Dict[str, float]:
        """Default fallback limits."""
        return {
            "daily_value_limit": 50000.0,
            "daily_count_limit": 100,
            "per_address_value_limit": 25000.0
        }
    
    def _get_default_oracles(self) -> Set[str]:
        """Default recognized oracle addresses."""
        return {
            "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419",  # Chainlink ETH/USD
            "0xf4030086522a5beea4988f8ca5b36dbc97bee88c",  # Chainlink BTC/USD
            "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",  # Band Protocol
        }
    
    async def get_client_registry(self, wallet_address: str) -> Dict[str, Any]:
        """Fetch client registry information for a wallet address."""
        if not self.client:
            return self._get_default_client_registry()
        
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset}.client_registry`
            WHERE walletAddress = @wallet_address
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("wallet_address", "STRING", wallet_address.lower())
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                return {
                    "clientId": row.clientId,
                    "clientName": row.clientName,
                    "clientType": row.clientType,
                    "lei": row.lei if hasattr(row, 'lei') else "",
                    "industrySector": row.industrySector,
                    "countryOfIncorporation": row.countryOfIncorporation,
                    "riskTier": row.riskTier,
                    "relationshipManager": row.relationshipManager,
                    "walletAddress": row.walletAddress,
                    "walletType": row.walletType,
                    "facilityType": row.facilityType,
                    "creditLimit": float(row.creditLimit),
                    "dailyDepositLimit": float(row.dailyDepositLimit),
                    "dailyWithdrawalLimit": float(row.dailyWithdrawalLimit),
                    "expectedActivityWindow": row.expectedActivityWindow,
                    "authorizedSignatories": list(row.authorizedSignatories) if hasattr(row, 'authorizedSignatories') else [],
                    "kycStatus": row.kycStatus,
                    "amlStatus": row.amlStatus
                }
        except Exception as e:
            logger.error(f"Failed to fetch client registry from BigQuery: {e}")
        
        return self._get_default_client_registry()
    
    async def get_client_registry_by_id(self, client_id: str) -> Dict[str, Any]:
        """Fetch client registry information by client ID."""
        if not self.client:
            return self._get_default_client_registry()
        
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset}.client_registry`
            WHERE clientId = @client_id
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("client_id", "STRING", client_id)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                return {
                    "clientId": row.clientId,
                    "clientName": row.clientName,
                    "clientType": row.clientType,
                    "lei": row.lei if hasattr(row, 'lei') else "",
                    "industrySector": row.industrySector,
                    "countryOfIncorporation": row.countryOfIncorporation,
                    "riskTier": row.riskTier,
                    "relationshipManager": row.relationshipManager,
                    "walletAddress": row.walletAddress,
                    "walletType": row.walletType,
                    "facilityType": row.facilityType,
                    "creditLimit": float(row.creditLimit),
                    "dailyDepositLimit": float(row.dailyDepositLimit),
                    "dailyWithdrawalLimit": float(row.dailyWithdrawalLimit),
                    "expectedActivityWindow": row.expectedActivityWindow,
                    "authorizedSignatories": list(row.authorizedSignatories) if hasattr(row, 'authorizedSignatories') else [],
                    "kycStatus": row.kycStatus,
                    "amlStatus": row.amlStatus
                }
        except Exception as e:
            logger.error(f"Failed to fetch client registry by ID from BigQuery: {e}")
        
        return self._get_default_client_registry()
    
    async def get_anomaly_master(self) -> Dict[str, Dict[str, Any]]:
        """Fetch anomaly master table."""
        if not self.client:
            return self._get_default_anomaly_master()
        
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset}.anomaly_master`
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            master = {}
            for row in results:
                master[row.anomaly_code] = {
                    "anomaly_code": row.anomaly_code,
                    "category": row.category,
                    "severity": row.severity,
                    "risk_score": int(row.risk_score),
                    "description": row.description
                }
            
            return master if master else self._get_default_anomaly_master()
        except Exception as e:
            logger.error(f"Failed to fetch anomaly master from BigQuery: {e}")
        
        return self._get_default_anomaly_master()
    
    async def store_anomaly_detection(self, detection_result: Dict[str, Any]) -> bool:
        """Store anomaly detection result in BigQuery."""
        if not self.client:
            logger.warning("BigQuery client not available, cannot store detection")
            return False
        
        try:
            table_id = f"{self.project_id}.{self.dataset}.anomaly_detections"
            
            # Prepare row for insertion
            row = {
                "detection_id": detection_result.get("detection_id"),
                "tx_hash": detection_result.get("transaction_id"),
                "client_id": detection_result.get("client_registry", {}).get("clientId"),
                "wallet_address": detection_result.get("client_registry", {}).get("walletAddress"),
                "is_anomaly": detection_result.get("is_anomaly"),
                "overall_score": detection_result.get("overall_score"),
                "overall_severity": detection_result.get("overall_severity"),
                "risk_score": detection_result.get("risk_score", 0),
                "anomaly_count": detection_result.get("anomaly_count"),
                "anomaly_codes": detection_result.get("anomaly_codes", []),
                "detections": str(detection_result.get("detections")),
                "all_reasons": detection_result.get("all_reasons", []),
                "narrative": detection_result.get("narrative"),
                "client_registry": str(detection_result.get("client_registry")),
                "detected_at": detection_result.get("detected_at"),
                "reviewed": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            errors = self.client.insert_rows_json(table_id, [row])
            if errors:
                logger.error(f"Failed to insert anomaly detection: {errors}")
                return False
            
            logger.info(f"Stored anomaly detection: {row['detection_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to store anomaly detection: {e}")
            return False
    
    def _get_default_client_registry(self) -> Dict[str, Any]:
        """Default client registry for fallback."""
        return {
            "clientId": "UNKNOWN",
            "clientName": "Unknown Client",
            "clientType": "INDIVIDUAL",
            "lei": "",
            "industrySector": "UNKNOWN",
            "countryOfIncorporation": "US",
            "riskTier": "MEDIUM",
            "relationshipManager": "UNASSIGNED",
            "walletAddress": "",
            "walletType": "EOA",
            "facilityType": "STANDARD",
            "creditLimit": 100000.0,
            "dailyDepositLimit": 50000.0,
            "dailyWithdrawalLimit": 50000.0,
            "expectedActivityWindow": "09:00-17:00",
            "authorizedSignatories": [],
            "kycStatus": "PENDING",
            "amlStatus": "PENDING"
        }
    
    def _get_default_anomaly_master(self) -> Dict[str, Dict[str, Any]]:
        """Default anomaly master table."""
        anomalies = [
            {"anomaly_code": "OFF_HOURS_FULL_BALANCE_WITHDRAWAL", "category": "TRANSACTION", "severity": "HIGH", "risk_score": 95, "description": "100% position withdrawn outside business hours"},
            {"anomaly_code": "UNKNOWN_ORACLE_ADDRESS", "category": "BLOCKCHAIN", "severity": "HIGH", "risk_score": 90, "description": "Unregistered oracle used in transaction"},
            {"anomaly_code": "FAILED_MINT", "category": "BLOCKCHAIN", "severity": "HIGH", "risk_score": 85, "description": "Token minting failed after core banking posting"},
            {"anomaly_code": "LEDGER_RECONCILIATION_BREAK", "category": "RECONCILIATION", "severity": "HIGH", "risk_score": 85, "description": "Off-chain and on-chain balances mismatch"},
            {"anomaly_code": "DUPLICATE_ESCROW_FUNDING", "category": "FINANCING", "severity": "MEDIUM", "risk_score": 75, "description": "Same purchase order or invoice funded multiple times"},
            {"anomaly_code": "FULL_WITHDRAWAL", "category": "TRANSACTION", "severity": "MEDIUM", "risk_score": 70, "description": "Withdrawal of 90-100% of available balance"},
            {"anomaly_code": "THRESHOLD_AVOIDANCE_PATTERN", "category": "BEHAVIORAL", "severity": "MEDIUM", "risk_score": 65, "description": "Transaction amount intentionally structured below monitoring threshold"},
            {"anomaly_code": "DAILY_LIMIT_BREACH", "category": "LIMIT", "severity": "MEDIUM", "risk_score": 65, "description": "Client exceeds configured daily transaction or withdrawal limits"},
            {"anomaly_code": "OFF_HOURS_ACTIVITY", "category": "TRANSACTION", "severity": "MEDIUM", "risk_score": 60, "description": "Transactions executed outside expected customer activity windows"},
            {"anomaly_code": "STALE_PENDING_TRANSACTION", "category": "OPERATIONS", "severity": "MEDIUM", "risk_score": 60, "description": "Transaction pending beyond SLA threshold"},
            {"anomaly_code": "LARGE_NEAR_THRESHOLD_DEPOSIT", "category": "TRANSACTION", "severity": "MEDIUM", "risk_score": 60, "description": "Large deposit amount just below reporting or approval threshold"},
            {"anomaly_code": "CONCENTRATION_RISK", "category": "EXPOSURE", "severity": "LOW", "risk_score": 45, "description": "Client holds disproportionately large portion of facility"},
            {"anomaly_code": "RAPID_FUND_IN_OUT", "category": "BEHAVIORAL", "severity": "HIGH", "risk_score": 85, "description": "Funds withdrawn shortly after deposit"},
            {"anomaly_code": "ABNORMAL_TRANSACTION_VELOCITY", "category": "BEHAVIORAL", "severity": "HIGH", "risk_score": 80, "description": "Transaction frequency significantly exceeds historical baseline"},
            {"anomaly_code": "MULTIPLE_WALLETS_SAME_CLIENT", "category": "BEHAVIORAL", "severity": "MEDIUM", "risk_score": 70, "description": "Client activity spread across multiple linked wallets"},
            {"anomaly_code": "UNUSUAL_COUNTERPARTY", "category": "COUNTERPARTY", "severity": "MEDIUM", "risk_score": 70, "description": "Transaction with previously unseen or high-risk counterparty"},
            {"anomaly_code": "FACILITY_UTILIZATION_SPIKE", "category": "EXPOSURE", "severity": "MEDIUM", "risk_score": 65, "description": "Sudden increase in credit facility utilization"},
            {"anomaly_code": "REPEATED_FAILED_TRANSACTIONS", "category": "OPERATIONS", "severity": "MEDIUM", "risk_score": 55, "description": "Multiple consecutive failed transactions"},
            {"anomaly_code": "LEGITIMATE_ACTIVITY_PATTERN", "category": "EXCEPTION", "severity": "INFO", "risk_score": 10, "description": "Flagged activity subsequently explained by documented business rationale"}
        ]
        return {a["anomaly_code"]: a for a in anomalies}
