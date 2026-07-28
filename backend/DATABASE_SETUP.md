# Database Setup Guide

## Overview

This application supports two database backends:
- **PostgreSQL** (default, recommended for development)
- **BigQuery** (for production data warehousing)

You can switch between them by setting the `DB_TYPE` environment variable.

## PostgreSQL Setup (Default)

### 1. Install PostgreSQL

**Windows:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql
```

**Docker (Recommended for Development):**
```bash
docker run --name postgres-anomaly \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=anomaly_db \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```env
# Database Type
DB_TYPE=postgresql

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=anomaly_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 3. Initialize Database

```bash
cd backend
.venv\Scripts\python.exe init_db.py
```

This creates all required tables automatically.

### 4. Start the Application

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

## BigQuery Setup

### 1. Configure Environment

```env
# Database Type
DB_TYPE=bigquery

# BigQuery Configuration
BIGQUERY_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=blockchain_anomaly_detection
BIGQUERY_TABLE=transactions
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### 2. Create BigQuery Table

Run this SQL in BigQuery console:

```sql
CREATE TABLE `your-project.blockchain_anomaly_detection.transactions` (
  id STRING NOT NULL,
  tx_hash STRING NOT NULL,
  from_address STRING NOT NULL,
  to_address STRING NOT NULL,
  value FLOAT64 NOT NULL,
  token_symbol STRING,
  chain_id INT64 NOT NULL,
  block_number INT64,
  status STRING NOT NULL,
  tx_type STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  anomaly_score FLOAT64,
  is_anomaly BOOL NOT NULL DEFAULT FALSE,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Create indexes
CREATE INDEX idx_tx_hash ON `your-project.blockchain_anomaly_detection.transactions`(tx_hash);
CREATE INDEX idx_is_anomaly ON `your-project.blockchain_anomaly_detection.transactions`(is_anomaly);
CREATE INDEX idx_timestamp ON `your-project.blockchain_anomaly_detection.transactions`(timestamp);
```

### 3. Start the Application

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

## API Usage

### Ingest Transaction

```bash
curl -X POST http://localhost:8000/api/v1/transactions/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0x123...",
    "from_address": "0xabc...",
    "to_address": "0xdef...",
    "value": 1000.5,
    "token_symbol": "USDC",
    "chain_id": 137
  }'
```

### List Transactions

```bash
# All transactions
curl http://localhost:8000/api/v1/transactions/?page=1&page_size=20

# Only anomalies
curl http://localhost:8000/api/v1/transactions/?is_anomaly=true

# Filter by chain
curl http://localhost:8000/api/v1/transactions/?chain_id=137
```

### Get Transaction by Hash

```bash
curl http://localhost:8000/api/v1/transactions/0x123...
```

## Database Schema

### Transaction Table

| Column | Type | Description |
|--------|------|-------------|
| id | String | Unique UUID |
| tx_hash | String | Blockchain transaction hash (unique) |
| from_address | String | Sender address |
| to_address | String | Receiver address |
| value | Float | Transaction value |
| token_symbol | String | Token symbol (optional) |
| chain_id | Integer | Blockchain network ID |
| block_number | Integer | Block number (optional) |
| status | Enum | pending, confirmed, failed |
| tx_type | Enum | transfer, swap, mint, burn, stake, contract_call |
| timestamp | DateTime | Transaction timestamp |
| anomaly_score | Float | ML anomaly score (0-1) |
| is_anomaly | Boolean | Whether flagged as anomaly |
| metadata | JSON | Additional metadata |
| created_at | DateTime | Record creation time |
| updated_at | DateTime | Last update time |

## Switching Databases

To switch from PostgreSQL to BigQuery (or vice versa):

1. Update `.env` file:
   ```env
   DB_TYPE=bigquery  # or postgresql
   ```

2. Restart the application:
   ```bash
   # Stop current server (Ctrl+C)
   # Start again
   .venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

The application will automatically use the configured database backend.

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Test connection
.venv\Scripts\python.exe -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"
```

Common issues:
- **Port 5432 already in use**: Change `POSTGRES_PORT` in `.env`
- **Authentication failed**: Check `POSTGRES_USER` and `POSTGRES_PASSWORD`
- **Database does not exist**: Create it manually or use Docker command above

### BigQuery Issues

Common issues:
- **403 Forbidden**: Check GCP service account permissions
- **Table not found**: Verify `BIGQUERY_PROJECT_ID`, `BIGQUERY_DATASET`, and `BIGQUERY_TABLE`
- **Credentials error**: Check `GOOGLE_APPLICATION_CREDENTIALS` path

## Performance Recommendations

### PostgreSQL
- For high-volume ingestion, use connection pooling (already configured)
- Consider partitioning by timestamp for large datasets
- Regular VACUUM and ANALYZE operations

### BigQuery
- Use batch inserts for better performance
- Avoid frequent small queries (use appropriate caching)
- Monitor query costs in GCP console

## Migration Between Databases

To migrate data from PostgreSQL to BigQuery (or vice versa):

```bash
# Export from PostgreSQL
.venv\Scripts\python.exe scripts/export_transactions.py --output=transactions.json

# Import to BigQuery
.venv\Scripts\python.exe scripts/import_transactions.py --input=transactions.json
```

(Note: Migration scripts are placeholders - implement as needed)
