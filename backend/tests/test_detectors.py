"""
Unit tests for anomaly detection system.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.anomaly.orchestrator import AnomalyOrchestrator
from app.models.detection_models import TransactionModel, AnomalyDetectionConfig


@pytest.fixture
def sample_transaction():
    """Sample transaction for testing."""
    return {
        "tx_hash": "0xabc123def456",
        "from_address": "0x742d35cc6634c0532925a3b844bc9e7595f0beb",
        "to_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
        "value": 9500.0,
        "timestamp": "2026-07-23T23:30:00Z",
        "gas_ratio": 0.85,
        "is_contract_interaction": False
    }


@pytest.fixture
def sample_context():
    """Sample context for testing."""
    return {
        "client_registry": {
            "clientId": "CLI-001",
            "clientName": "Test Client",
            "riskTier": "MEDIUM",
            "dailyWithdrawalLimit": 50000
        },
        "account_balance": {"0x742d35cc6634c0532925a3b844bc9e7595f0beb": 10000},
        "recent_transactions": [],
        "oracle_registry": set()
    }


@pytest.fixture
def mock_bq_client():
    """Mock BigQuery client."""
    client = AsyncMock()
    client.get_client_registry.return_value = {
        "clientId": "CLI-001",
        "clientName": "Test Client",
        "riskTier": "MEDIUM"
    }
    client.get_anomaly_master.return_value = {
        "OFF_HOURS_ACTIVITY": {
            "anomaly_code": "OFF_HOURS_ACTIVITY",
            "category": "TRANSACTION",
            "severity": "MEDIUM",
            "risk_score": 60
        }
    }
    client.get_account_balance.return_value = 10000.0
    client.get_recent_transactions.return_value = []
    client.store_anomaly_detection.return_value = True
    return client


class TestOrchestrator:
    """Tests for anomaly orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_bq_client):
        """Test orchestrator initializes correctly."""
        with patch('app.services.anomaly.orchestrator.BigQueryReferenceClient', return_value=mock_bq_client):
            orchestrator = AnomalyOrchestrator()
            await orchestrator.initialize()
            
            assert orchestrator.anomaly_master is not None
            assert len(orchestrator.detectors) == 8
    
    @pytest.mark.asyncio
    async def test_detect_all(self, sample_transaction, mock_bq_client):
        """Test full detection pipeline."""
        with patch('app.services.anomaly.orchestrator.BigQueryReferenceClient', return_value=mock_bq_client):
            orchestrator = AnomalyOrchestrator()
            await orchestrator.initialize()
            
            result = await orchestrator.detect_all(sample_transaction)
            
            assert "detection_id" in result
            assert "transaction_id" in result
            assert "is_anomaly" in result
            assert "client_registry" in result
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, sample_transaction, mock_bq_client):
        """Test detectors run in parallel."""
        config = {"parallel_execution": True}
        
        with patch('app.services.anomaly.orchestrator.BigQueryReferenceClient', return_value=mock_bq_client):
            orchestrator = AnomalyOrchestrator(config=config)
            await orchestrator.initialize()
            
            result = await orchestrator.detect_all(sample_transaction)
            
            assert result is not None


class TestTransactionModel:
    """Tests for transaction model validation."""
    
    def test_valid_transaction(self):
        """Test valid transaction creation."""
        tx = TransactionModel(
            tx_hash="0xabc123",
            from_address="0x742d35cc6634c0532925a3b844bc9e7595f0beb",
            to_address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
            value=1000.0,
            timestamp="2026-07-23T10:00:00Z"
        )
        
        assert tx.tx_hash == "0xabc123"
        assert tx.value == 1000.0
    
    def test_invalid_transaction_negative_value(self):
        """Test validation fails for negative value."""
        with pytest.raises(ValueError):
            TransactionModel(
                tx_hash="0xabc123",
                from_address="0x742d35cc6634c0532925a3b844bc9e7595f0beb",
                to_address="0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                value=-100.0,
                timestamp="2026-07-23T10:00:00Z"
            )
    
    def test_address_normalization(self):
        """Test addresses are normalized to lowercase."""
        tx = TransactionModel(
            tx_hash="0xABC123",
            from_address="0xABCDEF",
            to_address="0x123456",
            value=1000.0,
            timestamp="2026-07-23T10:00:00Z"
        )
        
        assert tx.from_address == "0xabcdef"
        assert tx.to_address == "0x123456"


class TestDetectorUtils:
    """Tests for detector utilities."""
    
    def test_normalize_address(self):
        """Test address normalization."""
        from app.utilities.detector_utils import normalize_address
        
        assert normalize_address("0xABCDEF") == "0xabcdef"
        assert normalize_address("ABCDEF") == "0xabcdef"
        assert normalize_address("") == ""
    
    def test_parse_time_window(self):
        """Test time window parsing."""
        from app.utilities.detector_utils import parse_time_window
        
        start, end = parse_time_window("09:00-17:00")
        assert start == 9
        assert end == 17
        
        with pytest.raises(ValueError):
            parse_time_window("invalid")
    
    def test_is_within_time_window(self):
        """Test time window checking."""
        from app.utilities.detector_utils import is_within_time_window
        
        # Monday 10:00 AM
        timestamp = datetime(2026, 7, 20, 10, 0, 0)
        
        assert is_within_time_window(timestamp, 9, 17, False) is True
        assert is_within_time_window(timestamp, 18, 22, False) is False
        
        # Saturday 10:00 AM
        weekend = datetime(2026, 7, 25, 10, 0, 0)
        assert is_within_time_window(weekend, 9, 17, False) is False
        assert is_within_time_window(weekend, 9, 17, True) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
