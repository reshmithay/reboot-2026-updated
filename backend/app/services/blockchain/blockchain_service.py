from app.clients.blockchain.web3_client import Web3Client
from app.clients.blockchain.contract_client import ContractClient
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class BlockchainService:
    def __init__(self):
        self.web3 = Web3Client()
        self.contracts = ContractClient(self.web3)

    async def record_anomaly(self, anomaly_id: str, score: float, tx_hash: str) -> str:
        """Write anomaly detection result to AnomalyRegistry smart contract."""
        try:
            receipt = await self.contracts.anomaly_registry.record_anomaly(
                anomaly_id=anomaly_id,
                score=int(score * 100),  # store as integer 0-100
                tx_hash=tx_hash,
            )
            logger.info(f"Anomaly {anomaly_id} recorded on-chain: {receipt['transactionHash'].hex()}")
            return receipt["transactionHash"].hex()
        except Exception as e:
            logger.error(f"Failed to record anomaly on-chain: {e}")
            raise

    async def write_audit_trail(self, transaction_id: str, event_data: dict) -> str:
        """Append to immutable AuditTrail smart contract."""
        receipt = await self.contracts.audit_trail.log_event(
            transaction_id=transaction_id,
            event_type=event_data.get("event_type", "ANOMALY_DETECTED"),
            metadata=str(event_data),
        )
        return receipt["transactionHash"].hex()

    async def update_risk_score(self, address: str, score: int) -> str:
        """Update wallet risk score in RiskScoreRegistry."""
        receipt = await self.contracts.risk_registry.update_score(
            address=address,
            score=score,
        )
        return receipt["transactionHash"].hex()

    async def get_audit_trail(self, transaction_id: str) -> list:
        return await self.contracts.audit_trail.get_events(transaction_id)

    async def get_risk_score(self, address: str) -> dict:
        score = await self.contracts.risk_registry.get_score(address)
        return {"address": address, "risk_score": score}

    async def get_anomaly_registry(self, anomaly_id: str) -> dict:
        return await self.contracts.anomaly_registry.get_anomaly(anomaly_id)
