# Enhanced Anomaly Detection System - Implementation Guide

## Overview

Fully integrated anomaly detection system with:
- ✅ **PyCaret/scikit-learn ML models**
- ✅ **Client Registry integration**
- ✅ **Anomaly Master table** with 20 predefined anomaly codes
- ✅ **BigQuery storage** of detection results
- ✅ **Risk scoring** based on anomaly master
- ✅ **8 specialized detectors** covering 10 anomaly patterns

## Architecture

```
Transaction Input
       ↓
[Orchestrator]
       ↓
┌──────────────────────────────────────┐
│  Fetch Context (BigQuery):           │
│  - Client Registry                   │
│  - Anomaly Master Table              │
│  - Recent Transactions               │
│  - Account Balances                  │
│  - Client Limits                     │
└──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────┐
│  Run 8 Detectors in Parallel:        │
│  1. OffHoursWithdrawalDetector       │
│  2. ThresholdDepositDetector         │
│  3. DuplicateEscrowDetector          │
│  4. OracleDetector                   │
│  5. DailyLimitDetector               │
│  6. ReconciliationDetector           │
│  7. FullWithdrawalDetector           │
│  8. TimeWindowDetector               │
└──────────────────────────────────────┘
       ↓
[Aggregate Results]
  - Map to Anomaly Master Codes
  - Calculate Risk Score
  - Enrich with Client Data
       ↓
[Store in BigQuery]
       ↓
[Generate LLM Narrative]
       ↓
[Return to API]
```

## Client Registry Format

Each wallet has an associated client profile:

```json
{
  "clientId": "CLI-001",
  "clientName": "Acme Trading Corp",
  "clientType": "CORPORATE",
  "lei": "549300ABC123DEF45678",
  "industrySector": "COMMODITIES_TRADING",
  "countryOfIncorporation": "US",
  "riskTier": "LOW",
  "relationshipManager": "john.doe@bank.com",
  "walletAddress": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "walletType": "MULTISIG",
  "facilityType": "PREMIUM",
  "creditLimit": 5000000,
  "dailyDepositLimit": 1000000,
  "dailyWithdrawalLimit": 500000,
  "expectedActivityWindow": "08:00-18:00",
  "authorizedSignatories": ["0xsigner1", "0xsigner2"],
  "kycStatus": "APPROVED",
  "amlStatus": "CLEARED"
}
```

## Anomaly Master Table (20 Codes)

| Code | Category | Severity | Risk Score | Description |
|------|----------|----------|------------|-------------|
| OFF_HOURS_FULL_BALANCE_WITHDRAWAL | TRANSACTION | HIGH | 95 | 100% withdrawal outside hours |
| UNKNOWN_ORACLE_ADDRESS | BLOCKCHAIN | HIGH | 90 | Unregistered oracle |
| FAILED_MINT | BLOCKCHAIN | HIGH | 85 | Token mint failed |
| LEDGER_RECONCILIATION_BREAK | RECONCILIATION | HIGH | 85 | Balance mismatch |
| RAPID_FUND_IN_OUT | BEHAVIORAL | HIGH | 85 | Quick withdrawal after deposit |
| ABNORMAL_TRANSACTION_VELOCITY | BEHAVIORAL | HIGH | 80 | High frequency |
| DUPLICATE_ESCROW_FUNDING | FINANCING | MEDIUM | 75 | Same PO funded twice |
| MULTIPLE_WALLETS_SAME_CLIENT | BEHAVIORAL | MEDIUM | 70 | Multi-wallet usage |
| UNUSUAL_COUNTERPARTY | COUNTERPARTY | MEDIUM | 70 | New/high-risk counterparty |
| FULL_WITHDRAWAL | TRANSACTION | MEDIUM | 70 | 90-100% withdrawal |
| THRESHOLD_AVOIDANCE_PATTERN | BEHAVIORAL | MEDIUM | 65 | Structuring |
| DAILY_LIMIT_BREACH | LIMIT | MEDIUM | 65 | Limit exceeded |
| FACILITY_UTILIZATION_SPIKE | EXPOSURE | MEDIUM | 65 | Credit spike |
| OFF_HOURS_ACTIVITY | TRANSACTION | MEDIUM | 60 | Off-hours transaction |
| STALE_PENDING_TRANSACTION | OPERATIONS | MEDIUM | 60 | SLA breach |
| LARGE_NEAR_THRESHOLD_DEPOSIT | TRANSACTION | MEDIUM | 60 | Just below threshold |
| REPEATED_FAILED_TRANSACTIONS | OPERATIONS | MEDIUM | 55 | Multiple failures |
| CONCENTRATION_RISK | EXPOSURE | LOW | 45 | Portfolio concentration |
| LEGITIMATE_ACTIVITY_PATTERN | EXCEPTION | INFO | 10 | Explained activity |

## Detector to Anomaly Code Mapping

| Detector | Anomaly Code(s) |
|----------|----------------|
| OffHoursWithdrawalDetector | OFF_HOURS_FULL_BALANCE_WITHDRAWAL |
| ThresholdDepositDetector | THRESHOLD_AVOIDANCE_PATTERN, LARGE_NEAR_THRESHOLD_DEPOSIT |
| DuplicateEscrowDetector | DUPLICATE_ESCROW_FUNDING |
| OracleDetector | UNKNOWN_ORACLE_ADDRESS |
| DailyLimitDetector | DAILY_LIMIT_BREACH |
| ReconciliationDetector | LEDGER_RECONCILIATION_BREAK |
| FullWithdrawalDetector | FULL_WITHDRAWAL |
| TimeWindowDetector | OFF_HOURS_ACTIVITY |

## PyCaret Models

### Model Types

1. **Isolation Forest** (velocity, time, value anomalies)
2. **K-Nearest Neighbors** (pattern detection)
3. **Local Outlier Factor** (clustering)
4. **PCA** (dimensionality-based detection)

### Training

```bash
# Train all models
cd blockchain-anomaly-ai
python scripts/train_models.py
```

### Features Used

**Velocity Model:**
- Log(value)
- Transaction count (1h)
- Unique counterparties

**Time Model:**
- Hour (sin/cos cyclical encoding)
- Day of week
- Is weekend

**Value Model:**
- Log(value)
- Gas ratio

**Pattern Model:**
- Transaction count
- Counterparty diversity
- Contract interaction flag

## Result Format

```json
{
  "detection_id": "550e8400-e29b-41d4-a716-446655440000",
  "transaction_id": "0xabc123...",
  "is_anomaly": true,
  "overall_score": 0.87,
  "overall_severity": "HIGH",
  "risk_score": 80,
  "anomaly_count": 2,
  "anomaly_codes": [
    "OFF_HOURS_ACTIVITY",
    "THRESHOLD_AVOIDANCE_PATTERN"
  ],
  "detections": [
    {
      "detector": "TimeWindowDetector",
      "confidence": 0.87,
      "severity": "high",
      "anomaly_code": "OFF_HOURS_ACTIVITY",
      "category": "TRANSACTION",
      "risk_score": 60,
      "description": "Transactions executed outside expected customer activity windows",
      "reasons": ["Transaction executed outside expected activity window", ...],
      "metadata": {...}
    }
  ],
  "all_reasons": [...],
  "client_registry": {
    "clientId": "CLI-001",
    "clientName": "Acme Trading Corp",
    "riskTier": "LOW",
    ...
  },
  "narrative": "This transaction from Acme Trading Corp exhibits...",
  "detected_at": "2026-07-23T10:30:00Z"
}
```

## BigQuery Schema

### Tables Created

1. **client_registry** - Client profiles and limits
2. **anomaly_master** - Anomaly code definitions
3. **anomaly_detections** - Detection results with client context
4. **transactions** - Transaction history
5. **account_balances** - Current balances
6. **oracle_registry** - Recognized oracles
7. **account_limits** - Account-specific limits
8. **reconciliation_pairs** - Expected pairs

See `docs/bigquery_table_schemas.sql` for full SQL definitions.

## Usage Examples

### Python API

```python
from app.services.anomaly_service import AnomalyService

service = AnomalyService()

# Initialize (loads anomaly master)
await service.orchestrator.initialize()

# Analyze transaction
transaction = {
    "tx_hash": "0xabc123...",
    "from_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "to_address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "value": 9500.0,
    "timestamp": "2026-07-23T23:30:00Z"
}

result = await service.analyze_transaction(transaction)

print(f"Anomaly: {result['is_anomaly']}")
print(f"Risk Score: {result['risk_score']}")
print(f"Codes: {result['anomaly_codes']}")
print(f"Client: {result['client_registry']['clientName']}")
```

### REST API

```bash
# Analyze transaction
curl -X POST http://localhost:8000/api/anomaly/detect \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0xabc123...",
    "from_address": "0x742d35...",
    "value": 9500
  }'
```

## Installation

```bash
# Install dependencies
pip install pycaret scikit-learn pandas numpy google-cloud-bigquery

# Or use requirements.txt
pip install -r backend/requirements.txt
```

## Configuration

```bash
# Environment variables
export GCP_PROJECT_ID="your-project-id"
export BIGQUERY_DATASET="blockchain_anomaly_detection"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Model Retraining

Models should be retrained periodically with new data:

```bash
# Weekly retraining (cron job)
0 2 * * 0 cd /app && python scripts/train_models.py
```

## Monitoring

Key metrics to track:
- Detection rate (anomalies / total transactions)
- False positive rate
- Average risk score
- Processing time per transaction
- Model drift (accuracy over time)

## Next Steps

1. ✅ Deploy BigQuery tables
2. ✅ Load client registry data
3. ✅ Train initial models
4. ⏳ Tune detection thresholds
5. ⏳ Implement feedback loop
6. ⏳ Add alerting for critical anomalies
7. ⏳ Create dashboard for review team
