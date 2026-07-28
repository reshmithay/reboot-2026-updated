# BigQuery Migration Summary

## ✅ Changes Made

Successfully migrated the backend from PostgreSQL to BigQuery for all three tables:
- `transactions`
- `anomaly_results`
- `client_registry`

---

## 📁 Files Created/Modified

### **1. Configuration**
**File:** `backend/app/config/settings.py`
- ✅ Changed `DB_TYPE` from "postgresql" to "bigquery"
- ✅ Added BigQuery project and dataset settings:
  - `BIGQUERY_PROJECT_ID`: `ltc-hack2026-team35`
  - `BIGQUERY_DATASET`: `ltchack2026team35`
  - `BIGQUERY_TABLE`: `transactions`
  - `BIGQUERY_ANOMALY_TABLE`: `anomaly_results`
  - `BIGQUERY_CLIENT_TABLE`: `client_registry`

**File:** `backend/.env` (Created)
- ✅ BigQuery configuration
- ✅ Database type set to `bigquery`
- ✅ Project ID and dataset configured

---

### **2. New BigQuery Repositories**

**File:** `backend/app/repositories/bigquery_anomaly_repository.py` (Created)
- ✅ `BigQueryAnomalyRepository` class
- ✅ Methods: `create()`, `get_by_id()`, `get_by_transaction_id()`, `get_by_transaction_hash()`, `list()`, `update()`
- ✅ Supports filtering by: severity, review_status, anomaly_category, client_id, date range
- ✅ Pagination support

**File:** `backend/app/repositories/bigquery_client_repository.py` (Created)
- ✅ `BigQueryClientRepository` class
- ✅ Methods: `create()`, `get_by_id()`, `get_by_wallet()`, `list()`, `update()`, `update_risk_score()`
- ✅ Supports filtering by: risk_tier, kyc_status, aml_status, client_type
- ✅ Search functionality across client_name, client_id, wallet_address
- ✅ Pagination support

---

### **3. Repository Factory Updates**

**File:** `backend/app/repositories/factory.py`
- ✅ Added `get_anomaly_repository()` method
- ✅ Added `get_client_repository()` method
- ✅ Existing `get_transaction_repository()` already supported BigQuery
- ✅ Factory automatically switches between PostgreSQL and BigQuery based on `DB_TYPE` setting

---

### **4. API Routes Updates**

**File:** `backend/app/api/anomaly_routes.py`
- ✅ Updated to use `RepositoryFactory` instead of direct PostgreSQL repository
- ✅ Works with both PostgreSQL and BigQuery transparently

**File:** `backend/app/api/client_registry_routes.py`
- ✅ Updated to use `RepositoryFactory` instead of direct PostgreSQL repository
- ✅ Works with both PostgreSQL and BigQuery transparently

**File:** `backend/app/api/transaction_routes.py`
- ✅ Updated to use `RepositoryFactory` (already supported BigQuery)
- ✅ Enhanced to handle optional db_session for BigQuery

---

## 🚀 How to Use

### **1. Start the Backend**

```bash
cd blockchain-anomaly-ai/backend
uvicorn app.main:app --reload --port 8000
```

### **2. API Endpoints**

All existing API endpoints work the same way:

**Transactions:**
- `POST /api/v1/transactions/ingest` - Ingest new transaction
- `GET /api/v1/transactions/` - List transactions
- `GET /api/v1/transactions/{tx_hash}` - Get transaction by hash

**Anomaly Results:**
- `POST /api/v1/anomalies/detect` - Detect anomaly
- `GET /api/v1/anomalies/results/` - List anomaly results (with filters)
- `GET /api/v1/anomalies/results/{anomaly_id}` - Get anomaly by ID
- `GET /api/v1/anomalies/results/transaction/{transaction_id}` - Get anomaly by transaction

**Client Registry:**
- `POST /api/v1/clients/` - Create client
- `GET /api/v1/clients/` - List clients (with filters)
- `GET /api/v1/clients/{client_id}` - Get client by ID
- `GET /api/v1/clients/wallet/{wallet_address}` - Get client by wallet
- `PUT /api/v1/clients/{client_id}` - Update client

---

## 🔧 Configuration

### **BigQuery Tables Required**

Make sure your BigQuery dataset `ltchack2026team35` has these tables:

1. **`transactions`** - Transaction records
2. **`anomaly_results`** - Detected anomalies
3. **`client_registry`** - Client information

### **Authentication**

The backend uses Application Default Credentials:
- Already configured via `gcloud auth application-default login`
- Certificate: `C:\Users\7316575\wssproxy.crt`

### **Environment Variable (Optional)**

Set the SSL certificate path:
```bash
$env:GRPC_DEFAULT_SSL_ROOTS_FILE_PATH = "C:\Users\7316575\wssproxy.crt"
```

---

## ✨ Benefits

1. **Scalability** - BigQuery handles large datasets efficiently
2. **Cost-effective** - Pay only for what you query
3. **No DB maintenance** - Fully managed by Google Cloud
4. **Same API** - No frontend changes needed
5. **Easy switch** - Change `DB_TYPE` to switch between PostgreSQL and BigQuery

---

## 🎯 Testing

Test the BigQuery integration:

```bash
# Test transaction ingestion
curl -X POST http://localhost:8000/api/v1/transactions/ingest \
  -H "Content-Type: application/json" \
  -d '{...transaction data...}'

# Test client list
curl http://localhost:8000/api/v1/clients/?page=1&page_size=10

# Test anomaly results
curl http://localhost:8000/api/v1/anomalies/results/?severity=high
```

---

## 📝 Notes

- BigQuery operations are asynchronous internally but wrapped in async Python methods
- Updates in BigQuery use DELETE + INSERT pattern (standard for BigQuery)
- All datetime fields are stored as ISO 8601 strings in BigQuery
- Pagination works the same as PostgreSQL
- Filtering supports all the same parameters

---

**Migration Complete! ✅**
Your backend now reads and writes from BigQuery tables instead of PostgreSQL.
