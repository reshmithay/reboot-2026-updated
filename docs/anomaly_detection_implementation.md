# Anomaly Detection System - Complete Implementation

## Overview

Complete anomaly detection system with 8 specialized detectors, BigQuery integration, and LLM narrative generation.

## Architecture

```
Transaction → Orchestrator → [8 Detectors] → Aggregation → LLM Narrative → API Response
                    ↓
              BigQuery Context
```

## Detectors Implemented

### 1. **OffHoursWithdrawalDetector** (`off_hours_detector.py`)
- **Pattern**: Full-balance withdrawals during off-hours
- **Method**: Time-based rules + Isolation Forest
- **Config**: Business hours 9am-5pm, full withdrawal threshold 90%
- **BigQuery**: Account balances, transaction history

### 2. **ThresholdDepositDetector** (`threshold_deposit_detector.py`)
- **Pattern**: Deposits just below regulatory thresholds (structuring/smurfing)
- **Method**: Rules + Isolation Forest + statistical z-scores
- **Config**: Thresholds $10k/$5k/$3k, 5% margin, min pattern count 3
- **BigQuery**: Pattern detection across recent transactions

### 3. **DuplicateEscrowDetector** (`duplicate_escrow_detector.py`)
- **Pattern**: Duplicate escrow funding attempts
- **Method**: Cosine similarity + nearest neighbor search
- **Config**: 95% similarity threshold, 60min time window, 1% value tolerance
- **BigQuery**: Recent escrow transactions

### 4. **OracleDetector** (`oracle_detector.py`)
- **Pattern**: Unrecognized oracle addresses
- **Method**: Whitelist validation against registry
- **Config**: Chainlink/Band oracle addresses, function signature matching
- **BigQuery**: Oracle registry with fallback to defaults

### 5. **DailyLimitDetector** (`daily_limit_detector.py`)
- **Pattern**: Daily transaction limits exceeded
- **Method**: Rules-based with value/count/per-address limits
- **Config**: $50k daily value, 100 transactions, $25k per address
- **BigQuery**: Account-specific limits, recent transactions

### 6. **ReconciliationDetector** (`reconciliation_detector.py`)
- **Pattern**: Reconciliation breaks in paired transactions
- **Method**: Rules-based pairing validation
- **Config**: 0.1% tolerance, 60min lookback
- **BigQuery**: Reconciliation pairs

### 7. **FullWithdrawalDetector** (`full_withdrawal_detector.py`)
- **Pattern**: Full or near-full balance withdrawals (90-100%)
- **Method**: Rules + Isolation Forest
- **Config**: 90-100% threshold
- **BigQuery**: Account balances

### 8. **TimeWindowDetector** (`time_window_detector.py`)
- **Pattern**: Transactions outside expected time windows
- **Method**: Isolation Forest with cyclical time encoding
- **Config**: Hour/day pattern analysis
- **BigQuery**: User behavior profiles

## Files Created

```
backend/app/
├── services/anomaly/
│   ├── orchestrator.py               # Main orchestrator
│   ├── example_usage.py              # Usage examples
│   └── detectors/
│       ├── __init__.py
│       ├── base_detector.py          # Abstract base class
│       ├── off_hours_detector.py     # Patterns 4, 8
│       ├── threshold_deposit_detector.py  # Patterns 6, 11
│       ├── duplicate_escrow_detector.py   # Pattern 7
│       ├── oracle_detector.py        # Pattern 5
│       ├── daily_limit_detector.py   # Pattern 9
│       ├── reconciliation_detector.py     # Pattern 3
│       ├── full_withdrawal_detector.py    # Pattern 8
│       └── time_window_detector.py   # Pattern 10
├── clients/bigquery/
│   └── reference_data_client.py      # BigQuery integration
├── config/
│   └── detection_rules.py            # Default thresholds
└── services/
    └── anomaly_service.py            # Main service API
```

## Usage

### Single Transaction Analysis

```python
from app.services.anomaly_service import AnomalyService

service = AnomalyService()

transaction = {
    "tx_hash": "0xabc123...",
    "from_address": "0x742d35...",
    "to_address": "0x1f9840...",
    "value": 9500.0,
    "timestamp": "2026-07-21T23:30:00Z",
    "gas_ratio": 0.85,
    "is_contract_interaction": False
}

result = await service.analyze_transaction(transaction)
print(f"Is Anomaly: {result['is_anomaly']}")
print(f"Score: {result['overall_score']}")
print(f"Narrative: {result['narrative']}")
```

### Batch Analysis

```python
transactions = [tx1, tx2, tx3]
results = await service.batch_analyze(transactions)
```

### Direct Orchestrator Use

```python
from app.services.anomaly.orchestrator import AnomalyOrchestrator

orchestrator = AnomalyOrchestrator()
detection = await orchestrator.detect_all(transaction)
```

## Result Format

```json
{
  "transaction_id": "0xabc123...",
  "is_anomaly": true,
  "overall_score": 0.85,
  "overall_severity": "high",
  "anomaly_count": 3,
  "detections": [
    {
      "detector": "ThresholdDepositDetector",
      "confidence": 0.87,
      "severity": "high",
      "reasons": [
        "Deposit $9,500 just below $10,000 threshold (5% margin)",
        "Pattern of 4 near-threshold deposits in 7 days"
      ],
      "metadata": {
        "threshold": 10000,
        "value": 9500,
        "pattern_count": 4
      }
    }
  ],
  "all_reasons": [...],
  "narrative": "This transaction exhibits multiple suspicious characteristics...",
  "detected_at": "2026-07-21T23:35:00Z"
}
```

## Configuration

### Environment Variables

```bash
GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=blockchain_anomaly_detection
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Detector Configuration

```python
config = {
    "threshold_deposit": {
        "thresholds": [10000, 5000, 3000],
        "threshold_margin": 0.05
    }
}

orchestrator = AnomalyOrchestrator(config)
```

## BigQuery Integration

See [bigquery_schemas.md](bigquery_schemas.md) for:
- Table schemas
- Setup instructions
- Sample queries
- Service account configuration

### Fallback Behavior

All detectors gracefully fallback to hardcoded defaults from `detection_rules.py` when BigQuery is unavailable.

## Testing

### Run example

```bash
cd backend
python -m app.services.anomaly.example_usage
```

### Unit tests (create)

```bash
pytest tests/services/anomaly/test_detectors.py -v
```

## Performance Considerations

- **Parallel Execution**: All detectors run concurrently
- **BigQuery Optimization**: Queries use partitioning and clustering
- **Model Caching**: ML models loaded once at initialization
- **Async I/O**: All operations are async/await

## Next Steps

1. **ML Model Training**: Train Isolation Forest models with real data
2. **BigQuery Setup**: Create tables and load reference data
3. **API Integration**: Connect orchestrator to FastAPI endpoints
4. **Monitoring**: Add Prometheus metrics for detector performance
5. **Testing**: Create comprehensive test suite
6. **Tuning**: Adjust thresholds based on false positive rate

## Detection Coverage

| Pattern # | Description | Detector | Method |
|-----------|-------------|----------|--------|
| 2 | Legitimate explanations | - | Context enrichment |
| 3 | Reconciliation breaks | ReconciliationDetector | Rules |
| 4 | Off-hours withdrawals | OffHoursWithdrawalDetector | Rules + IF |
| 5 | Unrecognized oracles | OracleDetector | Rules |
| 6 | Below-threshold deposits | ThresholdDepositDetector | Rules + IF + Stats |
| 7 | Duplicate escrow | DuplicateEscrowDetector | Similarity |
| 8 | Full withdrawals | FullWithdrawalDetector | Rules + IF |
| 9 | Daily limits | DailyLimitDetector | Rules |
| 10 | Time windows | TimeWindowDetector | IF |
| 11 | Near-threshold | ThresholdDepositDetector | Rules + Stats |

**Coverage**: 8 specialized detectors covering 10 anomaly patterns
