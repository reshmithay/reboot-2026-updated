"""
PostgreSQL reference data repository for fetching client registry, limits, and context data.
"""
from typing import Dict, Any, List, Set, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError

from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class PostgresReferenceDataRepository:
    """Repository for fetching reference data from PostgreSQL."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_client_registry(self, wallet_address: str) -> Dict[str, Any]:
        """Fetch client registry information for a wallet address."""
        try:
            query = text("""
                SELECT 
                    client_id,
                    client_name,
                    client_type,
                    lei,
                    industry_sector,
                    country_of_incorporation,
                    risk_tier,
                    relationship_manager,
                    wallet_address,
                    wallet_type,
                    facility_type,
                    credit_limit,
                    daily_deposit_limit,
                    daily_withdrawal_limit,
                    expected_activity_window,
                    authorized_signatories,
                    kyc_status,
                    aml_status
                FROM client_registry
                WHERE LOWER(wallet_address) = LOWER(:wallet_address)
                LIMIT 1
            """)
            
            result = await self.session.execute(
                query,
                {"wallet_address": wallet_address}
            )
            row = result.fetchone()
            
            if row:
                return {
                    "clientId": row[0],
                    "clientName": row[1],
                    "clientType": row[2],
                    "lei": row[3] or "",
                    "industrySector": row[4],
                    "countryOfIncorporation": row[5],
                    "riskTier": row[6],
                    "relationshipManager": row[7],
                    "walletAddress": row[8],
                    "walletType": row[9],
                    "facilityType": row[10],
                    "creditLimit": float(row[11]) if row[11] else 0.0,
                    "dailyDepositLimit": float(row[12]) if row[12] else 0.0,
                    "dailyWithdrawalLimit": float(row[13]) if row[13] else 0.0,
                    "expectedActivityWindow": row[14],
                    "authorizedSignatories": row[15] if row[15] else [],
                    "kycStatus": row[16],
                    "amlStatus": row[17]
                }
        except DBAPIError as e:
            await self.session.rollback()
            logger.error(f"Failed to fetch client registry from PostgreSQL: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch client registry from PostgreSQL: {e}")
        
        return self._get_default_client_registry()
    
    async def get_client_registry_by_id(self, client_id: str) -> Dict[str, Any]:
        """Fetch client registry by client ID."""
        try:
            query = text("""
                SELECT 
                    client_id,
                    client_name,
                    client_type,
                    lei,
                    industry_sector,
                    country_of_incorporation,
                    risk_tier,
                    relationship_manager,
                    wallet_address,
                    wallet_type,
                    facility_type,
                    credit_limit,
                    daily_deposit_limit,
                    daily_withdrawal_limit,
                    expected_activity_window,
                    authorized_signatories,
                    kyc_status,
                    aml_status
                FROM client_registry
                WHERE client_id = :client_id
                LIMIT 1
            """)
            
            result = await self.session.execute(
                query,
                {"client_id": client_id}
            )
            row = result.fetchone()
            
            if row:
                return {
                    "clientId": row[0],
                    "clientName": row[1],
                    "clientType": row[2],
                    "lei": row[3] or "",
                    "industrySector": row[4],
                    "countryOfIncorporation": row[5],
                    "riskTier": row[6],
                    "relationshipManager": row[7],
                    "walletAddress": row[8],
                    "walletType": row[9],
                    "facilityType": row[10],
                    "creditLimit": float(row[11]) if row[11] else 0.0,
                    "dailyDepositLimit": float(row[12]) if row[12] else 0.0,
                    "dailyWithdrawalLimit": float(row[13]) if row[13] else 0.0,
                    "expectedActivityWindow": row[14],
                    "authorizedSignatories": row[15] if row[15] else [],
                    "kycStatus": row[16],
                    "amlStatus": row[17]
                }
        except DBAPIError as e:
            await self.session.rollback()
            logger.error(f"Failed to fetch client registry by ID from PostgreSQL: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch client registry by ID from PostgreSQL: {e}")
        
        return self._get_default_client_registry()
    
    async def get_recent_transactions(
        self, wallet_address: str, lookback_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Fetch recent transactions for a wallet address."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=lookback_hours)
            
            query = text("""
                SELECT 
                    transaction_id,
                    transaction_hash,
                    from_wallet_address,
                    to_wallet_address,
                    amount,
                    currency,
                    transaction_type,
                    transaction_timestamp
                FROM transactions
                WHERE LOWER(from_wallet_address) = LOWER(:wallet_address)
                  AND transaction_timestamp >= :cutoff_time
                ORDER BY transaction_timestamp DESC
                LIMIT 100
            """)
            
            result = await self.session.execute(
                query,
                {
                    "wallet_address": wallet_address,
                    "cutoff_time": cutoff_time
                }
            )
            
            transactions = []
            for row in result:
                transactions.append({
                    "transaction_id": row[0],
                    "transaction_hash": row[1],
                    "from_address": row[2],
                    "to_address": row[3],
                    "amount": float(row[4]) if row[4] else 0.0,
                    "currency": row[5],
                    "transaction_type": row[6],
                    "timestamp": row[7].isoformat() if row[7] else None
                })
            
            return transactions
        except DBAPIError as e:
            await self.session.rollback()
            logger.error(f"Failed to fetch recent transactions from PostgreSQL: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch recent transactions from PostgreSQL: {e}")
            return []
    
    async def get_account_balance(self, wallet_address: str) -> float:
        """Fetch current account balance for a wallet address."""
        try:
            # Get sum of deposits minus withdrawals
            query = text("""
                SELECT 
                    COALESCE(SUM(
                        CASE 
                            WHEN transaction_type = 'DEPOSIT' THEN amount
                            WHEN transaction_type = 'WITHDRAWAL' THEN -amount
                            ELSE 0
                        END
                    ), 0) as balance
                FROM transactions
                WHERE LOWER(from_wallet_address) = LOWER(:wallet_address)
                   OR LOWER(to_wallet_address) = LOWER(:wallet_address)
            """)
            
            result = await self.session.execute(
                query,
                {"wallet_address": wallet_address}
            )
            row = result.fetchone()
            
            if row and row[0]:
                return float(row[0])
        except DBAPIError as e:
            await self.session.rollback()
            logger.error(f"Failed to fetch account balance from PostgreSQL: {e}")
        except Exception as e:
            logger.error(f"Failed to fetch account balance from PostgreSQL: {e}")
        
        return 0.0
    
    async def get_anomaly_master(self) -> Dict[str, Dict[str, Any]]:
        """Fetch anomaly master table."""
        try:
            query = text("""
                SELECT 
                    anomaly_code,
                    category,
                    severity,
                    risk_score,
                    description
                FROM anomaly_master
                WHERE is_active = true
            """)
            
            result = await self.session.execute(query)
            
            anomaly_master = {}
            for row in result:
                anomaly_master[row[0]] = {
                    "anomaly_code": row[0],
                    "category": row[1],
                    "severity": row[2],
                    "risk_score": int(row[3]) if row[3] else 50,
                    "description": row[4]
                }
            
            return anomaly_master
        except DBAPIError as e:
            await self.session.rollback()
            logger.error(f"Failed to fetch anomaly master from PostgreSQL: {e}")
            return self._get_default_anomaly_master()
        except Exception as e:
            logger.error(f"Failed to fetch anomaly master from PostgreSQL: {e}")
            return self._get_default_anomaly_master()
    
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
        return {
            "OFF_HOURS_ACTIVITY": {
                "anomaly_code": "OFF_HOURS_ACTIVITY",
                "category": "TRANSACTION",
                "severity": "MEDIUM",
                "risk_score": 60,
                "description": "Transactions outside expected activity windows"
            },
            "FULL_WITHDRAWAL": {
                "anomaly_code": "FULL_WITHDRAWAL",
                "category": "TRANSACTION",
                "severity": "MEDIUM",
                "risk_score": 70,
                "description": "Withdrawal of 90-100% of available balance"
            },
            "THRESHOLD_AVOIDANCE_PATTERN": {
                "anomaly_code": "THRESHOLD_AVOIDANCE_PATTERN",
                "category": "BEHAVIORAL",
                "severity": "MEDIUM",
                "risk_score": 65,
                "description": "Transaction structured below monitoring threshold"
            },
            "DAILY_LIMIT_BREACH": {
                "anomaly_code": "DAILY_LIMIT_BREACH",
                "category": "LIMIT",
                "severity": "MEDIUM",
                "risk_score": 65,
                "description": "Client exceeds configured daily limits"
            }
        }