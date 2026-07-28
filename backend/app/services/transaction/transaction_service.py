from app.schemas.transaction_schema import TransactionIngest
from app.services.anomaly.anomaly_service import AnomalyService
from app.services.blockchain.blockchain_service import BlockchainService
from app.repositories.factory import RepositoryFactory
from app.core.database import get_async_session
from app.utilities.logger.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class TransactionService:
    def __init__(self, db_session=None):
        self.anomaly_service = AnomalyService()
        self.blockchain_service = BlockchainService()
        self.db_session = db_session
        self.repository = None

    async def _get_repository(self):
        """Get repository instance."""
        if self.repository is None:
            self.repository = RepositoryFactory.get_transaction_repository(self.db_session)
        return self.repository

    async def ingest_transaction(self, payload: TransactionIngest) -> dict:
        """
        Full ingestion pipeline:
        1. Persist transaction to DB
        2. Run anomaly detection
        3. If anomaly, record on blockchain + send notification
        """
        tx_id = str(uuid.uuid4())
        logger.info(f"Ingesting transaction {payload.transaction_hash}")

        # Persist to database via repository
        repo = await self._get_repository()
        transaction_data = {
            "id": tx_id,
            "transaction_id": payload.transaction_id,
            "transaction_hash": payload.transaction_hash,
            "transaction_type": payload.transaction_type,
            "amount": payload.amount,
            "currency": payload.currency,
            "transaction_timestamp": payload.transaction_timestamp or datetime.utcnow(),
            "transaction_status": payload.transaction_status,
            "on_chain_status": payload.on_chain_status,
            "from_account": payload.from_account,
            "to_account": payload.to_account,
            "from_wallet_address": payload.from_wallet_address,
            "to_wallet_address": payload.to_wallet_address,
            "wallet_address": payload.wallet_address,
            "client_id": payload.client_id,
            "client_name": payload.client_name,
            "blockchain_network": payload.blockchain_network,
            "ledger_type": payload.ledger_type,
            "chain_id": payload.chain_id,
            "block_number": payload.block_number,
            "block_hash": payload.block_hash,
            "token_symbol": payload.token_symbol,
            "gas_fee": payload.gas_fee,
            "gas_price": payload.gas_price,
            "correlation_id": payload.correlation_id,
            "tx_metadata": payload.metadata,
            "transaction_category": payload.transaction_category,
        }

        # Run anomaly detection
        anomaly_result = await self.anomaly_service.detect_and_record(
            transaction_id=payload.transaction_hash
        )

        is_anomaly = anomaly_result["score"] >= 0.5

        # Save to database
        created_transaction = await repo.create(transaction_data)

        # If anomaly detected, write audit trail on-chain
        if is_anomaly:
            try:
                await self.blockchain_service.write_audit_trail(
                    transaction_id=payload.transaction_hash,
                    event_data={
                        "event_type": "ANOMALY_DETECTED",
                        "score": anomaly_result["score"],
                        "severity": anomaly_result["severity"],
                    },
                )
            except Exception as e:
                logger.warning(f"Blockchain write failed (non-critical): {e}")

        return created_transaction

    async def list_transactions(self, page: int, page_size: int, is_anomaly=None, chain_id=None) -> dict:
        """List transactions with filters."""
        repo = await self._get_repository()
        return await repo.list(page, page_size, is_anomaly, chain_id)

    async def get_transaction_by_hash(self, tx_hash: str) -> dict | None:
        """Get transaction by hash."""
        repo = await self._get_repository()
        return await repo.get_by_hash(tx_hash)
