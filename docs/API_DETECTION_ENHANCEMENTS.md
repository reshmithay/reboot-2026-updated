# API-Based Anomaly Detection Enhancements

## Overview
Enhanced API-based anomaly detection to match CSV file-based detection flow with the following improvements:

## Changes Implemented

### 1. API Request Schema Update
**File**: `backend/app/schemas/anomaly_schema.py`

- Changed `AnomalyDetectRequest` to accept `transaction_hash` instead of `transaction_id`
- Enhanced `AnomalyReason` model to include `score` field (confidence score 0-1)

```python
class AnomalyReason(BaseModel):
    reasonCode: str
    description: str
    score: Optional[float] = Field(None, description="Confidence score for this reason (0-1)")

class AnomalyDetectRequest(BaseModel):
    transaction_hash: str = Field(..., description="Transaction hash to detect anomalies")
    force: bool = Field(False, description="Force re-analysis even if cached")
```

### 2. Detector Configuration
**File**: `backend/app/services/anomaly/orchestrator.py`

The orchestrator now maintains two sets of detectors:

**API Detectors (6 detectors)** - Used for API-based detection:
1. **OffHoursWithdrawalDetector** - Detects after-hours suspicious activity
2. **ThresholdDepositDetector** - Detects threshold avoidance (structuring)
3. **DailyLimitDetector** - Detects daily limit violations
4. **ReconciliationDetector** - Detects reconciliation mismatches
5. **FullWithdrawalDetector** - Detects full account draining
6. **TimeWindowDetector** - Detects time-based anomalies

**CSV Upload Detectors (8 detectors)** - Used for CSV file-based detection:
1. OffHoursWithdrawalDetector
2. ThresholdDepositDetector
3. **DuplicateEscrowDetector** - Detects duplicate escrow patterns
4. **OracleDetector** - Detects oracle manipulation
5. DailyLimitDetector
6. ReconciliationDetector
7. FullWithdrawalDetector
8. TimeWindowDetector

```python
# All detectors for CSV upload
self.all_detectors: List[BaseDetector] = [
    OffHoursWithdrawalDetector(...),
    ThresholdDepositDetector(...),
    DuplicateEscrowDetector(...),
    OracleDetector(...),
    DailyLimitDetector(...),
    ReconciliationDetector(...),
    FullWithdrawalDetector(...),
    TimeWindowDetector(...),
]

# API detectors (6 specialized detectors)
self.api_detectors: List[BaseDetector] = [
    OffHoursWithdrawalDetector(...),
    ThresholdDepositDetector(...),
    DailyLimitDetector(...),
    ReconciliationDetector(...),
    FullWithdrawalDetector(...),
    TimeWindowDetector(...),
]
```

### 3. New Detection Method
**File**: `backend/app/services/anomaly/orchestrator.py`

Added `detect_by_transaction_hash()` method that:
- Fetches transaction from database using transaction hash
- Runs all 6 detectors on the transaction
- Aggregates results with enhanced anomaly reasons
- Stores results in PostgreSQL and BigQuery
- Returns data in `anomaly_results` table format

```python
async def detect_by_transaction_hash(
    self,
    transaction_hash: str,
    transaction_repo=None
) -> Dict[str, Any]:
    """
    Detect anomalies for a transaction identified by hash.
    Similar to CSV-based detection flow.
    """
```

### 4. Enhanced Anomaly Reasons Storage
**File**: `backend/app/services/anomaly/orchestrator.py`

The `_aggregate_results()` method now creates `detailed_reasons` with:
- `reasonCode`: Anomaly code from detector
- `description`: Human-readable description of the anomaly
- `score`: Confidence score from detector (0-1)

```python
detailed_reasons = []
for result in anomalies:
    for reason in result.reasons:
        detailed_reasons.append({
            "reasonCode": result.anomaly_code or "ANOMALY",
            "description": reason,
            "score": result.confidence
        })
```

### 5. Result Format Conversion
**File**: `backend/app/services/anomaly/orchestrator.py`

Added `_convert_to_anomaly_result_format()` method to convert detection results to match the `anomaly_results` table schema:

```python
{
    "anomalyId": "detection_id",
    "transactionId": "transaction_id",
    "transactionHash": "transaction_hash",
    "clientId": "client_id",
    "amount": 1000.0,
    "currency": "INR",
    "anomalyScore": 0.85,
    "severity": "HIGH",
    "anomalyCategory": "FRAUD",
    "anomalyTypes": ["OFF_HOURS", "FULL_WITHDRAWAL"],
    "anomalyReasons": [
        {
            "reasonCode": "OFF_HOURS",
            "description": "Transaction occurred outside business hours (02:30 AM)",
            "score": 0.85
        },
        {
            "reasonCode": "FULL_WITHDRAWAL",
            "description": "Withdrawal of 95.0% of account balance",
            "score": 0.85
        }
    ],
    "confidence": 0.85,
    "modelName": "Ensemble",
    "modelVersion": "v1.0",
    "reviewStatus": "PENDING",
    "detectedAt": "2026-07-26T10:30:00",
    "createdAt": "2026-07-26T10:30:00",
    "updatedAt": "2026-07-26T10:30:00"
}
```

### 6. API Endpoint Update
**File**: `backend/app/api/anomaly_routes.py`

Updated `/detect` endpoint to:
- Accept `transaction_hash` in request payload
- Use transaction repository to fetch transaction
- Initialize AnomalyOrchestrator with AnomalyResultService
- Call `detect_by_transaction_hash()` method
- Return results in `AnomalyResultResponse` format

```python
@router.post("/detect", response_model=AnomalyResultResponse)
async def detect_anomaly(
    payload: AnomalyDetectRequest,
    transaction_repo = Depends(get_transaction_repository),
    anomaly_result_repo = Depends(get_anomaly_result_repository),
):
    anomaly_result_service = AnomalyResultService(anomaly_result_repo)
    orchestrator = AnomalyOrchestrator(
        config={"store_results": True},
        anomaly_result_service=anomaly_result_service
    )
    result = await orchestrator.detect_by_transaction_hash(
        transaction_hash=payload.transaction_hash,
        transaction_repo=transaction_repo
    )
    return result
```

### 7. Storage in PostgreSQL/BigQuery
**File**: `backend/app/services/anomaly/orchestrator.py`

The `_store_results()` method now:
- Stores enhanced `detailed_reasons` (with scores) in `anomaly_reasons` column
- Saves to both BigQuery `anomaly_detections` table and PostgreSQL `anomaly_results` table
- Uses AnomalyResultService for PostgreSQL storage

## API Usage

### Request
```bash
POST /api/v1/anomalies/detect
Content-Type: application/json

{
  "transaction_hash": "0xabc123...",
  "force": false
}
```

### Response
```json
{
  "anomalyId": "ANM12345678",
  "transactionId": "TXN001",
  "transactionHash": "0xabc123...",
  "clientId": "CLIENT001",
  "amount": 50000.0,
  "currency": "INR",
  "fromWalletAddress": "0x123...",
  "toWalletAddress": "0x456...",
  "transactionType": "WITHDRAWAL",
  "anomalyScore": 0.85,
  "severity": "HIGH",
  "anomalyCategory": "FRAUD",
  "anomalyTypes": ["OFF_HOURS", "FULL_WITHDRAWAL"],
  "anomalyReasons": [
    {
      "reasonCode": "OFF_HOURS",
      "description": "Transaction at 02:30 (outside business hours)",
      "score": 0.85
    },
    {
      "reasonCode": "FULL_WITHDRAWAL",
      "description": "Withdrawal of 95.0% of account balance",
      "score": 0.85
    }
  ],
  "confidence": 0.85,
  "modelName": "Ensemble",
  "modelVersion": "v1.0",
  "reviewStatus": "PENDING",
  "assignedTo": null,
  "caseId": null,
  "detectedAt": "2026-07-26T10:30:00",
  "createdAt": "2026-07-26T10:30:00",
  "updatedAt": "2026-07-26T10:30:00"
}
```

## Detection Flow

### API-Based Detection (6 Detectors)
```
1. API Request with transaction_hash
   ↓
2. Fetch transaction from PostgreSQL/BigQuery by hash
   ↓
3. Prepare context (client registry, limits, recent transactions, balance)
   ↓
4. Run 6 specialized detectors:
   - OffHoursWithdrawalDetector
   - ThresholdDepositDetector
   - DailyLimitDetector
   - ReconciliationDetector
   - FullWithdrawalDetector
   - TimeWindowDetector
   ↓
5. Aggregate results with scores in anomaly_reasons
   ↓
6. Store in BigQuery (anomaly_detections) and PostgreSQL (anomaly_results)
   ↓
7. Return formatted response in anomaly_results table format
```

### CSV-Based Detection (8 Detectors)
```
1. Load transactions from CSV file
   ↓
2. For each transaction:
   ↓
3. Prepare context (client registry, limits, recent transactions, balance)
   ↓
4. Run all 8 detectors:
   - OffHoursWithdrawalDetector
   - ThresholdDepositDetector
   - DuplicateEscrowDetector
   - OracleDetector
   - DailyLimitDetector
   - ReconciliationDetector
   - FullWithdrawalDetector
   - TimeWindowDetector
   ↓
5. Aggregate results with scores in anomaly_reasons
   ↓
6. Store in BigQuery (anomaly_detections) and PostgreSQL (anomaly_results)
   ↓
7. Return aggregated detection results
```

## Key Features

1. **Transaction Hash Lookup**: Uses transaction hash instead of ID for detection
2. **Dual Detector Configuration**: 
   - **6 specialized detectors** for API-based real-time detection
   - **8 comprehensive detectors** for CSV file-based batch detection
3. **Enhanced Reason Storage**: Each anomaly reason includes its confidence score
4. **Dual Storage**: Results saved in both BigQuery and PostgreSQL
5. **Standardized Format**: Response matches anomaly_results table schema
6. **Proper Context**: Uses client registry, limits, and historical data for detection

## Benefits

- **Flexible Detection**: Different detector sets optimized for API (6 detectors) vs CSV upload (8 detectors)
- **API Performance**: Focused 6-detector set for faster real-time API detection
- **CSV Completeness**: Full 8-detector suite for comprehensive batch analysis
- **Traceability**: Score included with each reason for transparency
- **Flexibility**: Works with both PostgreSQL and BigQuery
- **Scalability**: Can process transactions in real-time via API or batch via CSV
- **Auditability**: Complete detection details stored in database

## Database Schema

### PostgreSQL: `anomaly_results` table
- `anomaly_id`: Primary key
- `transaction_hash`: Transaction hash (indexed)
- `anomaly_score`: Overall confidence score
- `anomaly_reasons`: JSONB array with {reasonCode, description, score}
- `severity`: CRITICAL, HIGH, MEDIUM, LOW
- `review_status`: PENDING, APPROVED, REJECTED, etc.

### BigQuery: `anomaly_detections` table  
- Similar schema with nested/repeated fields
- Stores aggregated detection results
- Used for analytics and reporting

## Next Steps

To test the enhanced detection:

1. Ensure a transaction exists in the database
2. Call POST `/api/v1/anomalies/detect` with transaction_hash
3. Check the response for detailed anomaly reasons with scores
4. Verify storage in PostgreSQL `anomaly_results` table
5. Verify storage in BigQuery `anomaly_detections` table (if configured)
