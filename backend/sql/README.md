# Database Schema Setup Guide

## Overview

This directory contains SQL schemas for:
1. **Transactions** - All blockchain transaction records with anomaly detection
2. **Client Registry** - Client master data with risk profiles and limits
3. **Anomaly Master** - Anomaly code definitions and classifications

## Files

- `postgresql_schema.sql` - PostgreSQL/CockroachDB compatible schema
- `bigquery_schema.sql` - Google BigQuery compatible schema

## PostgreSQL Setup

### Option 1: Using psql command line

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d anomaly_db

# Run the schema script
\i sql/postgresql_schema.sql

# Verify tables created
\dt

# Check sample data
SELECT * FROM anomaly_master;
```

### Option 2: Using pgAdmin

1. Open pgAdmin
2. Connect to your database
3. Open Query Tool
4. Load `postgresql_schema.sql`
5. Execute (F5)

### Option 3: Using Python script

```bash
cd backend
.venv\Scripts\python.exe -c "
import asyncio
import asyncpg
from app.config.settings import Settings

async def run_schema():
    settings = Settings()
    conn = await asyncpg.connect(settings.postgres_url)
    
    with open('sql/postgresql_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    await conn.execute(schema_sql)
    print('✅ Schema created successfully!')
    await conn.close()

asyncio.run(run_schema())
"
```

### Option 4: Using Docker

```bash
# Copy SQL file into container
docker cp sql/postgresql_schema.sql postgres-anomaly:/tmp/schema.sql

# Execute inside container
docker exec -i postgres-anomaly psql -U postgres -d anomaly_db < /tmp/schema.sql
```

## BigQuery Setup

### Option 1: Using bq command line

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create dataset
bq mk --dataset YOUR_PROJECT_ID:blockchain_anomaly_detection

# Run schema (replace placeholders first)
bq query --use_legacy_sql=false < sql/bigquery_schema.sql
```

### Option 2: Using BigQuery Console

1. Go to BigQuery Console (https://console.cloud.google.com/bigquery)
2. Select your project
3. Click "Compose new query"
4. Copy content from `bigquery_schema.sql`
5. Replace `your-project.your-dataset` with actual values
6. Run query

### Option 3: Using Python

```python
from google.cloud import bigquery
from app.config.settings import Settings

settings = Settings()
client = bigquery.Client(project=settings.BIGQUERY_PROJECT_ID)

with open('sql/bigquery_schema.sql', 'r') as f:
    schema_sql = f.read()
    
# Replace placeholders
schema_sql = schema_sql.replace(
    'your-project.your-dataset',
    f'{settings.BIGQUERY_PROJECT_ID}.{settings.BIGQUERY_DATASET}'
)

# Execute each statement
for statement in schema_sql.split(';'):
    if statement.strip():
        client.query(statement).result()

print('✅ BigQuery schema created!')
```

## Schema Features

### Transactions Table

**Key Fields:**
- `transaction_id` - Unique business transaction ID
- `transaction_hash` - Blockchain hash
- `amount`, `currency` - Transaction value
- `from_wallet_address`, `to_wallet_address` - Wallet addresses
- `client_id` - Links to client registry
- `is_anomaly`, `anomaly_score` - Detection results
- `anomaly_codes` - Array of detected anomaly types

**Indexes:**
- Transaction ID, hash, timestamp
- Client ID, wallet addresses
- Anomaly flag for fast filtering
- Composite indexes for common queries

**PostgreSQL Specific:**
- Partitioning ready (can add later)
- JSONB for metadata with GIN index
- Automatic `updated_at` triggers

**BigQuery Specific:**
- Partitioned by transaction_timestamp (by day)
- Clustered by client_id, is_anomaly, transaction_type
- Optimized for time-range queries

### Client Registry Table

**Key Fields:**
- `client_id` - Primary key
- `client_name`, `client_type` - Basic info
- `risk_tier` - Risk classification
- `wallet_address` - Primary wallet
- `daily_deposit_limit`, `daily_withdrawal_limit` - Transaction limits
- `kyc_status`, `aml_status` - Compliance flags

**Indexes:**
- Client name, wallet, risk tier
- KYC/AML status for compliance queries

### Anomaly Master Table

**Key Fields:**
- `anomaly_code` - Primary key (e.g., AN001)
- `category` - Anomaly category
- `severity` - CRITICAL, HIGH, MEDIUM, LOW
- `risk_score` - 0-100 numeric score
- `description` - Human-readable description

**Pre-loaded Data:**
10 common anomaly types with configurations

## Views Created

### PostgreSQL & BigQuery Views:

1. **v_recent_anomalies** - Latest anomalies with client details
2. **v_client_transaction_summary** - Transaction stats by client
3. **v_daily_anomaly_stats** - Daily aggregated statistics
4. **v_hourly_pattern** (BigQuery) - Hourly transaction patterns
5. **v_high_risk_clients** (BigQuery) - High-risk client monitoring
6. **v_daily_limit_violations** (BigQuery) - Limit breach detection
7. **v_anomaly_trends** (BigQuery) - Anomaly trends over time

## Sample Queries

### Find all anomalies for a client

```sql
-- PostgreSQL
SELECT * FROM transactions 
WHERE client_id = 'client-001' 
AND is_anomaly = TRUE
ORDER BY transaction_timestamp DESC;

-- BigQuery
SELECT * FROM `your-project.your-dataset.transactions`
WHERE client_id = 'client-001' 
AND is_anomaly = TRUE
ORDER BY transaction_timestamp DESC;
```

### Get today's anomaly count by severity

```sql
-- PostgreSQL
SELECT am.severity, COUNT(*) as count
FROM transactions t,
     UNNEST(t.anomaly_codes) AS code
JOIN anomaly_master am ON am.anomaly_code = code
WHERE DATE(t.transaction_timestamp) = CURRENT_DATE
AND t.is_anomaly = TRUE
GROUP BY am.severity;

-- BigQuery
SELECT am.severity, COUNT(*) as count
FROM `your-project.your-dataset.transactions` t,
     UNNEST(t.anomaly_codes) as code
JOIN `your-project.your-dataset.anomaly_master` am 
  ON am.anomaly_code = code
WHERE DATE(t.transaction_timestamp) = CURRENT_DATE()
AND t.is_anomaly = TRUE
GROUP BY am.severity;
```

### Check client daily limits

```sql
SELECT * FROM v_daily_limit_violations
WHERE transaction_date = CURRENT_DATE;
```

## Maintenance

### PostgreSQL

```sql
-- Vacuum and analyze
VACUUM ANALYZE transactions;
VACUUM ANALYZE client_registry;

-- Reindex if needed
REINDEX TABLE transactions;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### BigQuery

```sql
-- Check table size and costs
SELECT 
  table_name,
  ROUND(size_bytes/POW(10,9), 2) as size_gb,
  row_count
FROM `your-project.your-dataset.__TABLES__`
ORDER BY size_bytes DESC;

-- Optimize with clustering (already applied in schema)
-- No manual maintenance needed for BigQuery
```

## Migration Between Databases

See `DATABASE_SETUP.md` for instructions on migrating data between PostgreSQL and BigQuery.

## Troubleshooting

### PostgreSQL
- **Error: relation already exists** - Drop tables first or use `IF NOT EXISTS`
- **Permission denied** - Grant appropriate permissions to user
- **Cannot connect** - Check `pg_hba.conf` and firewall settings

### BigQuery
- **Table already exists** - Use `CREATE OR REPLACE TABLE` or delete first
- **Quota exceeded** - Check your GCP billing and quotas
- **Invalid table name** - Ensure proper project.dataset.table format
