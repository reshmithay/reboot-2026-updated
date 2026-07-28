# BigQuery Table Schemas

This document defines the BigQuery tables and schemas used for anomaly detection reference data.

## Dataset Configuration

- **Project ID**: `your-gcp-project-id`
- **Dataset**: `blockchain_anomaly_detection`
- **Region**: `us-central1`

## Tables

### 1. `transactions`

Stores blockchain transaction history.

```sql
CREATE TABLE `blockchain_anomaly_detection.transactions` (
  tx_hash STRING NOT NULL,
  block_number INT64,
  timestamp TIMESTAMP,
  from_address STRING,
  to_address STRING,
  value NUMERIC,
  gas_price NUMERIC,
  gas_used INT64,
  gas_ratio FLOAT64,
  is_contract_interaction BOOL,
  function_signature STRING,
  token_symbol STRING,
  tx_type STRING,
  status STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(timestamp)
CLUSTER BY from_address, to_address;
```

**Usage**: Cycling detector, off-hours detector, daily limit detector

---

### 2. `account_limits`

Account-specific transaction limits and configurations.

```sql
CREATE TABLE `blockchain_anomaly_detection.account_limits` (
  address STRING NOT NULL,
  daily_value_limit NUMERIC,
  daily_count_limit INT64,
  per_address_value_limit NUMERIC,
  is_high_risk BOOL DEFAULT FALSE,
  limit_type STRING,  -- 'default', 'custom', 'elevated'
  effective_from TIMESTAMP,
  effective_to TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(updated_at)
CLUSTER BY address;
```

**Usage**: Daily limit detector

---

### 3. `oracle_registry`

Recognized oracle addresses and configurations.

```sql
CREATE TABLE `blockchain_anomaly_detection.oracle_registry` (
  oracle_address STRING NOT NULL,
  oracle_name STRING,
  oracle_provider STRING,  -- 'Chainlink', 'Band', etc.
  data_feed STRING,  -- 'ETH/USD', 'BTC/USD', etc.
  chain_id INT64,
  is_active BOOL DEFAULT TRUE,
  function_signatures ARRAY<STRING>,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY oracle_address, chain_id;
```

**Usage**: Oracle detector

---

### 4. `account_balances`

Current and historical account balances.

```sql
CREATE TABLE `blockchain_anomaly_detection.account_balances` (
  address STRING NOT NULL,
  balance NUMERIC,
  token_symbol STRING,
  chain_id INT64,
  snapshot_time TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(snapshot_time)
CLUSTER BY address, token_symbol;
```

**Usage**: Full withdrawal detector, off-hours detector

---

### 5. `address_tags`

Address labels and risk categorization.

```sql
CREATE TABLE `blockchain_anomaly_detection.address_tags` (
  address STRING NOT NULL,
  tag STRING,  -- 'exchange', 'dex', 'oracle', 'escrow', 'high_risk', etc.
  risk_score FLOAT64,  -- 0.0 to 1.0
  source STRING,  -- 'manual', 'chainalysis', 'elliptic', etc.
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY address;
```

**Usage**: All detectors for context enrichment

---

### 6. `reconciliation_pairs`

Expected transaction pairs for reconciliation.

```sql
CREATE TABLE `blockchain_anomaly_detection.reconciliation_pairs` (
  pair_id STRING NOT NULL,
  tx_hash_1 STRING,
  tx_hash_2 STRING,
  expected_value NUMERIC,
  actual_difference NUMERIC,
  pair_type STRING,  -- 'escrow', 'deposit_withdrawal', etc.
  is_reconciled BOOL DEFAULT FALSE,
  reconciled_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY tx_hash_1, tx_hash_2;
```

**Usage**: Reconciliation detector

---

### 7. `anomaly_detections`

Stores anomaly detection results.

```sql
CREATE TABLE `blockchain_anomaly_detection.anomaly_detections` (
  detection_id STRING NOT NULL,
  tx_hash STRING,
  is_anomaly BOOL,
  overall_score FLOAT64,
  overall_severity STRING,  -- 'low', 'medium', 'high', 'critical'
  anomaly_count INT64,
  detections JSON,  -- Array of detector results
  all_reasons ARRAY<STRING>,
  narrative STRING,
  detected_at TIMESTAMP,
  reviewed BOOL DEFAULT FALSE,
  reviewed_by STRING,
  reviewed_at TIMESTAMP,
  resolution STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(detected_at)
CLUSTER BY tx_hash, overall_severity;
```

**Usage**: Historical analysis, model training

---

### 8. `user_behavior_profiles`

Behavioral profiles for legitimate explanation validation.

```sql
CREATE TABLE `blockchain_anomaly_detection.user_behavior_profiles` (
  address STRING NOT NULL,
  avg_transaction_value NUMERIC,
  avg_transaction_hour FLOAT64,
  typical_counterparties ARRAY<STRING>,
  common_transaction_types ARRAY<STRING>,
  typical_days_of_week ARRAY<INT64>,
  profile_computed_at TIMESTAMP,
  transaction_count INT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY address;
```

**Usage**: Time window detector, behavioral analysis

---

## Sample Queries

### Get recent transactions for an address

```sql
SELECT *
FROM `blockchain_anomaly_detection.transactions`
WHERE from_address = @address
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC
LIMIT 100;
```

### Get account limits

```sql
SELECT *
FROM `blockchain_anomaly_detection.account_limits`
WHERE address = @address
  AND (effective_to IS NULL OR effective_to > CURRENT_TIMESTAMP())
ORDER BY updated_at DESC
LIMIT 1;
```

### Get active oracles

```sql
SELECT oracle_address, oracle_name, data_feed
FROM `blockchain_anomaly_detection.oracle_registry`
WHERE is_active = TRUE
  AND chain_id = @chain_id;
```

### Get current balance

```sql
SELECT balance, token_symbol
FROM `blockchain_anomaly_detection.account_balances`
WHERE address = @address
  AND token_symbol = @token_symbol
ORDER BY snapshot_time DESC
LIMIT 1;
```

---

## Setup Instructions

### 1. Create dataset

```bash
bq mk --dataset \
  --location=us-central1 \
  --description="Blockchain anomaly detection reference data" \
  your-gcp-project-id:blockchain_anomaly_detection
```

### 2. Create tables

Run each CREATE TABLE statement above using:

```bash
bq query --use_legacy_sql=false < create_table.sql
```

### 3. Load initial data

```bash
# Load oracle registry
bq load --source_format=CSV \
  blockchain_anomaly_detection.oracle_registry \
  oracle_registry.csv \
  oracle_address:STRING,oracle_name:STRING,oracle_provider:STRING,data_feed:STRING,chain_id:INTEGER

# Load address tags
bq load --source_format=NEWLINE_DELIMITED_JSON \
  blockchain_anomaly_detection.address_tags \
  address_tags.jsonl
```

### 4. Configure service account

Grant BigQuery permissions to the service account:

```bash
gcloud projects add-iam-policy-binding your-gcp-project-id \
  --member="serviceAccount:anomaly-detector@your-gcp-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"
```

### 5. Set environment variables

```bash
export GCP_PROJECT_ID="your-gcp-project-id"
export BIGQUERY_DATASET="blockchain_anomaly_detection"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```
