# Anomaly Master Reference - Quick Guide

## 19 Anomaly Codes

### 🔴 CRITICAL & HIGH SEVERITY (Risk 80-95)

| Code | Risk | Category | Description | Detector |
|------|------|----------|-------------|----------|
| **OFF_HOURS_FULL_BALANCE_WITHDRAWAL** | 95 | TRANSACTION | 100% withdrawn outside hours | OffHoursWithdrawalDetector |
| **UNKNOWN_ORACLE_ADDRESS** | 90 | BLOCKCHAIN | Unregistered oracle | OracleDetector |
| **FAILED_MINT** | 85 | BLOCKCHAIN | Token mint failed | - |
| **LEDGER_RECONCILIATION_BREAK** | 85 | RECONCILIATION | Balance mismatch | ReconciliationDetector |
| **RAPID_FUND_IN_OUT** | 85 | BEHAVIORAL | Quick withdrawal after deposit | - |
| **ABNORMAL_TRANSACTION_VELOCITY** | 80 | BEHAVIORAL | High frequency | - |

### 🟡 MEDIUM SEVERITY (Risk 60-75)

| Code | Risk | Category | Description | Detector |
|------|------|----------|-------------|----------|
| **DUPLICATE_ESCROW_FUNDING** | 75 | FINANCING | Same PO funded twice | DuplicateEscrowDetector |
| **MULTIPLE_WALLETS_SAME_CLIENT** | 70 | BEHAVIORAL | Multi-wallet usage | - |
| **UNUSUAL_COUNTERPARTY** | 70 | COUNTERPARTY | New/high-risk counterparty | - |
| **FULL_WITHDRAWAL** | 70 | TRANSACTION | 90-100% withdrawal | FullWithdrawalDetector |
| **THRESHOLD_AVOIDANCE_PATTERN** | 65 | BEHAVIORAL | Structuring | ThresholdDepositDetector |
| **DAILY_LIMIT_BREACH** | 65 | LIMIT | Limit exceeded | DailyLimitDetector |
| **FACILITY_UTILIZATION_SPIKE** | 65 | EXPOSURE | Credit spike | - |
| **OFF_HOURS_ACTIVITY** | 60 | TRANSACTION | Off-hours transaction | TimeWindowDetector |
| **STALE_PENDING_TRANSACTION** | 60 | OPERATIONS | SLA breach | - |
| **LARGE_NEAR_THRESHOLD_DEPOSIT** | 60 | TRANSACTION | Just below threshold | ThresholdDepositDetector |

### 🟢 LOW SEVERITY (Risk 45-55)

| Code | Risk | Category | Description | Detector |
|------|------|----------|-------------|----------|
| **REPEATED_FAILED_TRANSACTIONS** | 55 | OPERATIONS | Multiple failures | - |
| **CONCENTRATION_RISK** | 45 | EXPOSURE | Portfolio concentration | - |

### ℹ️ INFO SEVERITY (Risk 10)

| Code | Risk | Category | Description | Detector |
|------|------|----------|-------------|----------|
| **LEGITIMATE_ACTIVITY_PATTERN** | 10 | EXCEPTION | Explained activity | - |

---

## Categories

- **TRANSACTION**: Direct transaction anomalies (5 codes)
- **BEHAVIORAL**: Pattern-based detection (6 codes)
- **BLOCKCHAIN**: On-chain specific (2 codes)
- **FINANCING**: Trade finance related (1 code)
- **RECONCILIATION**: Balance matching (1 code)
- **LIMIT**: Threshold breaches (1 code)
- **COUNTERPARTY**: Party screening (1 code)
- **EXPOSURE**: Risk concentration (2 codes)
- **OPERATIONS**: Process issues (2 codes)
- **EXCEPTION**: Whitelisted (1 code)

---

## Response Actions by Risk Score

### Critical (90-95)
- **Immediate block** of transaction
- **Alert senior management** within 1 hour
- **Manual review required**
- **Potential SAR filing**

### High (80-89)
- **Hold transaction** pending review
- **Alert compliance team** within 2 hours
- **Investigate within 4 hours**
- **Document findings**

### Medium (60-79)
- **Flag for review** within 24 hours
- **Enhanced monitoring**
- **Batch review acceptable**
- **Update client profile**

### Low (45-59)
- **Routine monitoring**
- **Weekly review**
- **Statistical tracking**

### Info (10)
- **Log only**
- **No action required**
- **Explained/whitelisted**

---

## Common Combinations

### Money Laundering Indicators
```
ABNORMAL_TRANSACTION_VELOCITY + THRESHOLD_AVOIDANCE_PATTERN
→ Risk Score: 72.5 avg → HIGH severity
```

### Account Takeover
```
OFF_HOURS_FULL_BALANCE_WITHDRAWAL + UNUSUAL_COUNTERPARTY
→ Risk Score: 82.5 avg → HIGH severity
```

### Fraud Scheme
```
DUPLICATE_ESCROW_FUNDING + MULTIPLE_WALLETS_SAME_CLIENT
→ Risk Score: 72.5 avg → MEDIUM severity
```

---

## Client Risk Tier Adjustments

| Client Risk Tier | Threshold Multiplier | Auto-Block |
|------------------|---------------------|-----------|
| LOW | 1.0x | Risk ≥ 90 |
| MEDIUM | 0.9x | Risk ≥ 85 |
| HIGH | 0.8x | Risk ≥ 80 |
| CRITICAL | 0.7x | Risk ≥ 75 |

Example:
- LOW risk client: Block at score 90+
- HIGH risk client: Block at score 80+

---

## SLA Response Times

| Severity | Detection | Review | Resolution |
|----------|-----------|--------|------------|
| CRITICAL | Real-time | 1 hour | 4 hours |
| HIGH | Real-time | 2 hours | 8 hours |
| MEDIUM | Real-time | 4 hours | 24 hours |
| LOW | Batch | 24 hours | 7 days |
| INFO | Batch | N/A | N/A |

---

## Detector Coverage Matrix

| Pattern Type | Primary Detector | Backup Method |
|--------------|------------------|---------------|
| Transaction velocity | Rule thresholds | Historical baseline |
| Structuring | Rules + ML | Statistical z-score |
| Off-hours | Time rules + ML | Business hours |
| Duplicate | Similarity matching | Hash comparison |
| Oracle | Whitelist | Registry lookup |
| Limits | Rules | Client registry |
| Reconciliation | Pairing rules | Balance delta |
| Full withdrawal | Rules + ML | Ratio calculation |
| Time anomaly | Isolation Forest | Historical pattern |

---

## Integration Points

### Input Required
```json
{
  "walletAddress": "0x...",  // Links to client_registry
  "tx_hash": "0x...",
  "value": 9500,
  "timestamp": "2026-07-23T23:30:00Z"
}
```

### Output Provided
```json
{
  "anomaly_codes": ["CODE1", "CODE2"],
  "risk_score": 80,
  "client_registry": {...},
  "detections": [...]
}
```

### BigQuery Stored
- Full detection record in `anomaly_detections` table
- Linked to `client_registry` via `client_id`
- Enriched with `anomaly_master` metadata

---

## Quick Reference: Severity Calculation

```python
# From anomaly_codes to risk_score
total_risk = sum(master[code]['risk_score'] for code in anomaly_codes)
avg_risk_score = total_risk // len(anomaly_codes)

# Severity mapping
if avg_risk_score >= 90: severity = "CRITICAL"
elif avg_risk_score >= 75: severity = "HIGH"
elif avg_risk_score >= 50: severity = "MEDIUM"
else: severity = "LOW"
```
