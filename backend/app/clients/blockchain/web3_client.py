from web3 import Web3
from app.config.settings import settings
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class Web3Client:
    def __init__(self):
        self._w3: Web3 | None = None

    @property
    def w3(self) -> Web3:
        if self._w3 is None or not self._w3.is_connected():
            self._w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
            if not self._w3.is_connected():
                raise ConnectionError(f"Cannot connect to RPC: {settings.BLOCKCHAIN_RPC_URL}")
            logger.info(f"Web3 connected to chain {settings.BLOCKCHAIN_CHAIN_ID}")
        return self._w3

    def get_account(self):
        return self.w3.eth.account.from_key(settings.DEPLOYER_PRIVATE_KEY)

    async def get_block(self, block_number: int) -> dict:
        return dict(self.w3.eth.get_block(block_number))

    async def get_transaction(self, tx_hash: str) -> dict:
        return dict(self.w3.eth.get_transaction(tx_hash))

    async def get_transaction_receipt(self, tx_hash: str) -> dict:
        return dict(self.w3.eth.get_transaction_receipt(tx_hash))
