import json
from pathlib import Path
from app.config.settings import settings
from app.clients.blockchain.web3_client import Web3Client
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)

ARTIFACTS_PATH = Path(__file__).parent.parent.parent.parent.parent / "blockchain" / "artifacts" / "contracts"


def _load_abi(contract_name: str) -> list:
    abi_file = ARTIFACTS_PATH / f"{contract_name}.sol" / f"{contract_name}.json"
    if abi_file.exists():
        with open(abi_file) as f:
            return json.load(f)["abi"]
    logger.warning(f"ABI not found for {contract_name}, using empty ABI")
    return []


class ContractClient:
    def __init__(self, web3_client: Web3Client):
        self.web3 = web3_client
        self._anomaly_registry = None
        self._audit_trail = None
        self._risk_registry = None

    @property
    def anomaly_registry(self):
        if not self._anomaly_registry:
            abi = _load_abi("AnomalyRegistry")
            self._anomaly_registry = self.web3.w3.eth.contract(
                address=settings.ANOMALY_REGISTRY_ADDRESS,
                abi=abi,
            )
        return self._anomaly_registry

    @property
    def audit_trail(self):
        if not self._audit_trail:
            abi = _load_abi("AuditTrail")
            self._audit_trail = self.web3.w3.eth.contract(
                address=settings.AUDIT_TRAIL_ADDRESS,
                abi=abi,
            )
        return self._audit_trail

    @property
    def risk_registry(self):
        if not self._risk_registry:
            abi = _load_abi("RiskScoreRegistry")
            self._risk_registry = self.web3.w3.eth.contract(
                address=settings.RISK_SCORE_REGISTRY_ADDRESS,
                abi=abi,
            )
        return self._risk_registry
