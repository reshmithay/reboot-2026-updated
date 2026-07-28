# API Contract

Base URL: `http://localhost:8000/api/v1`

## Transactions

### POST /transactions/ingest
Ingest a new transaction and trigger anomaly detection.

**Request:**
```json
{
  "tx_hash": "0xabc123...",
  "from_address": "0xSender...",
  "to_address": "0xReceiver...",
  "value": 1500.00,
  "token_symbol": "USDC",
  "chain_id": 137
}
```
**Response:** `201 Created` — `TransactionResponse`

### GET /transactions/
List transactions with pagination.

**Query params:** `page`, `page_size`, `is_anomaly`, `chain_id`

---

## Anomalies

### POST /anomalies/detect
Run anomaly detection on a transaction.

**Request:** `{ "transaction_id": "0xabc...", "force": false }`  
**Response:** `201 Created` — `AnomalyResponse`

### GET /anomalies/
List anomalies. Query params: `page`, `page_size`, `severity`

### GET /anomalies/stats/summary
Get aggregated anomaly statistics.

---

## Narratives

### POST /narratives/generate
Generate Gemini-powered narrative for an anomaly.

**Request:**
```json
{
  "anomaly_id": "anom-abc123",
  "narrative_type": "anomaly_explanation",
  "include_recommendations": true,
  "audience": "analyst"
}
```
**Response:** `201 Created` — `NarrativeResponse`

### GET /narratives/{anomaly_id}
Get existing narrative for an anomaly.

---

## Blockchain

### GET /blockchain/audit/{transaction_id}
Fetch on-chain audit trail entries.

### GET /blockchain/risk-score/{address}
Get wallet risk score from smart contract.

---

## Error Format
All errors return:
```json
{
  "detail": "Human-readable error message"
}
```
