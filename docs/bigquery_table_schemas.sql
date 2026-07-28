# BigQuery SQL Schema Definitions

## Create Tables

### 1. Client Registry Table

```sql
CREATE TABLE `blockchain_anomaly_detection.client_registry` (
  clientId STRING NOT NULL,
  clientName STRING,
  clientType STRING,  -- INDIVIDUAL, CORPORATE, INSTITUTIONAL
  lei STRING,
  industrySector STRING,
  countryOfIncorporation STRING,
  riskTier STRING,  -- LOW, MEDIUM, HIGH, CRITICAL
  relationshipManager STRING,
  walletAddress STRING NOT NULL,
  walletType STRING,  -- EOA, CONTRACT, MULTISIG
  facilityType STRING,
  creditLimit NUMERIC,
  dailyDepositLimit NUMERIC,
  dailyWithdrawalLimit NUMERIC,
  expectedActivityWindow STRING,  -- "09:00-17:00"
  authorizedSignatories ARRAY<STRING>,
  kycStatus STRING,  -- PENDING, APPROVED, REJECTED
  amlStatus STRING,  -- PENDING, CLEARED, FLAGGED
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(updated_at)
CLUSTER BY walletAddress, clientId, riskTier;
```

### 2. Anomaly Master Table

```sql
CREATE TABLE `blockchain_anomaly_detection.anomaly_master` (
  anomaly_code STRING NOT NULL,
  category STRING,  -- TRANSACTION, BLOCKCHAIN, RECONCILIATION, BEHAVIORAL, etc.
  severity STRING,  -- INFO, LOW, MEDIUM, HIGH, CRITICAL
  risk_score INT64,  -- 0-100
  description STRING,
  remediation_guidance STRING,
  sla_hours INT64,  -- Response time SLA
  requires_manual_review BOOL DEFAULT FALSE,
  auto_block_threshold FLOAT64,  -- Auto-block if confidence > this
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY anomaly_code, category, severity;
```

### 3. Enhanced Anomaly Detections Table

```sql
CREATE TABLE `blockchain_anomaly_detection.anomaly_detections` (
  detection_id STRING NOT NULL,
  tx_hash STRING,
  client_id STRING,
  wallet_address STRING,
  is_anomaly BOOL,
  overall_score FLOAT64,
  overall_severity STRING,
  risk_score INT64,
  anomaly_count INT64,
  anomaly_codes ARRAY<STRING>,
  detections STRING,  -- JSON string of detector results
  all_reasons ARRAY<STRING>,
  narrative STRING,
  client_registry STRING,  -- JSON string
  detected_at TIMESTAMP,
  reviewed BOOL DEFAULT FALSE,
  reviewed_by STRING,
  reviewed_at TIMESTAMP,
  resolution STRING,  -- FALSE_POSITIVE, CONFIRMED, EXPLAINED
  resolution_notes STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(detected_at)
CLUSTER BY tx_hash, client_id, overall_severity, reviewed;
```

## Sample Data

### Insert Sample Client Registry

```sql
INSERT INTO `blockchain_anomaly_detection.client_registry`
(clientId, clientName, clientType, lei, industrySector, countryOfIncorporation, 
 riskTier, relationshipManager, walletAddress, walletType, facilityType, 
 creditLimit, dailyDepositLimit, dailyWithdrawalLimit, expectedActivityWindow,
 authorizedSignatories, kycStatus, amlStatus)
VALUES
-- High-value corporate client
('CLI-001', 'Acme Trading Corp', 'CORPORATE', '549300ABC123DEF45678', 
 'COMMODITIES_TRADING', 'US', 'LOW', 'john.doe@bank.com',
 '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb', 'MULTISIG', 'PREMIUM',
 5000000, 1000000, 500000, '08:00-18:00',
 ['0xsigner1', '0xsigner2', '0xsigner3'], 'APPROVED', 'CLEARED'),

-- Medium-risk individual
('CLI-002', 'Jane Smith', 'INDIVIDUAL', '', 
 'TECHNOLOGY', 'GB', 'MEDIUM', 'jane.manager@bank.com',
 '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', 'EOA', 'STANDARD',
 100000, 50000, 50000, '09:00-17:00',
 [], 'APPROVED', 'CLEARED'),

-- High-risk startup
('CLI-003', 'CryptoStart Ltd', 'CORPORATE', '549300XYZ789GHI01234',
 'CRYPTOCURRENCY', 'SG', 'HIGH', 'risk.team@bank.com',
 '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419', 'CONTRACT', 'ENHANCED_MONITORING',
 250000, 100000, 75000, '00:00-23:59',
 ['0xfounder', '0xcfo'], 'APPROVED', 'FLAGGED');
```

### Insert Anomaly Master Data

```sql
INSERT INTO `blockchain_anomaly_detection.anomaly_master`
(anomaly_code, category, severity, risk_score, description, remediation_guidance, 
 sla_hours, requires_manual_review, auto_block_threshold)
VALUES
('OFF_HOURS_FULL_BALANCE_WITHDRAWAL', 'TRANSACTION', 'HIGH', 95, 
 '100% position withdrawn outside business hours',
 'Contact client immediately. Verify authorization. Consider temporary block.',
 2, TRUE, 0.90),

('UNKNOWN_ORACLE_ADDRESS', 'BLOCKCHAIN', 'HIGH', 90,
 'Unregistered oracle used in transaction',
 'Verify oracle legitimacy. Update whitelist if valid.',
 4, TRUE, NULL),

('DUPLICATE_ESCROW_FUNDING', 'FINANCING', 'MEDIUM', 75,
 'Same purchase order or invoice funded multiple times',
 'Check invoice/PO uniqueness. Verify legitimate business reason.',
 12, TRUE, NULL),

('THRESHOLD_AVOIDANCE_PATTERN', 'BEHAVIORAL', 'MEDIUM', 65,
 'Transaction amount intentionally structured below monitoring threshold',
 'Review transaction history. File SAR if pattern confirmed.',
 24, TRUE, NULL),

('DAILY_LIMIT_BREACH', 'LIMIT', 'MEDIUM', 65,
 'Client exceeds configured daily transaction or withdrawal limits',
 'Verify if limit increase was approved. Block if unauthorized.',
 4, FALSE, NULL),

('LEGITIMATE_ACTIVITY_PATTERN', 'EXCEPTION', 'INFO', 10,
 'Flagged activity subsequently explained by documented business rationale',
 'Document explanation. Update client profile if needed.',
 NULL, FALSE, NULL);
```

## Queries for Detectors

### Get High-Risk Clients

```sql
SELECT *
FROM `blockchain_anomaly_detection.client_registry`
WHERE riskTier IN ('HIGH', 'CRITICAL')
  AND kycStatus = 'APPROVED';
```

### Get Unreviewed Critical Anomalies

```sql
SELECT 
  d.detection_id,
  d.tx_hash,
  d.client_id,
  c.clientName,
  c.riskTier,
  d.overall_score,
  d.overall_severity,
  d.risk_score,
  d.anomaly_codes,
  d.detected_at
FROM `blockchain_anomaly_detection.anomaly_detections` d
LEFT JOIN `blockchain_anomaly_detection.client_registry` c
  ON d.client_id = c.clientId
WHERE d.overall_severity IN ('HIGH', 'CRITICAL')
  AND d.reviewed = FALSE
ORDER BY d.risk_score DESC, d.detected_at DESC
LIMIT 100;
```

### Anomaly Statistics by Client

```sql
SELECT 
  client_id,
  COUNT(*) as anomaly_count,
  AVG(overall_score) as avg_score,
  AVG(risk_score) as avg_risk,
  STRING_AGG(DISTINCT overall_severity) as severities,
  MAX(detected_at) as last_anomaly
FROM `blockchain_anomaly_detection.anomaly_detections`
WHERE is_anomaly = TRUE
  AND detected_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY client_id
HAVING anomaly_count > 5
ORDER BY avg_risk DESC;
```

### Anomaly Trend by Code

```sql
SELECT 
  UNNEST(anomaly_codes) as anomaly_code,
  DATE(detected_at) as detection_date,
  COUNT(*) as occurrence_count,
  AVG(overall_score) as avg_confidence
FROM `blockchain_anomaly_detection.anomaly_detections`
WHERE is_anomaly = TRUE
  AND detected_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY anomaly_code, detection_date
ORDER BY detection_date DESC, occurrence_count DESC;
```

## Views

### Create Client Risk Summary View

```sql
CREATE VIEW `blockchain_anomaly_detection.client_risk_summary` AS
SELECT 
  c.clientId,
  c.clientName,
  c.riskTier,
  c.dailyWithdrawalLimit,
  COUNT(DISTINCT d.detection_id) as total_anomalies,
  SUM(CASE WHEN d.overall_severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_count,
  SUM(CASE WHEN d.overall_severity = 'HIGH' THEN 1 ELSE 0 END) as high_count,
  AVG(d.risk_score) as avg_risk_score,
  MAX(d.detected_at) as last_anomaly_date
FROM `blockchain_anomaly_detection.client_registry` c
LEFT JOIN `blockchain_anomaly_detection.anomaly_detections` d
  ON c.clientId = d.client_id
  AND d.detected_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY c.clientId, c.clientName, c.riskTier, c.dailyWithdrawalLimit;
```
