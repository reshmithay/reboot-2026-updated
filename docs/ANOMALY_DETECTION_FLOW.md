# Anomaly Detection Flow - Complete Technical Guide

## Overview

This document provides a comprehensive breakdown of how anomaly detection works in the backend when:
1. **API-based detection**: Calling the `/api/v1/anomalies/detect` endpoint
2. **File-based detection**: Reading transactions from CSV files

---

## Table of Contents

1. [API-Based Detection Flow](#1-api-based-detection-flow)
2. [CSV File-Based Detection Flow](#2-csv-file-based-detection-flow)
3. [Detection Components](#3-detection-components)
4. [Complete Pipeline Diagram](#4-complete-pipeline-diagram)
5. [Code References](#5-code-references)

---

## 1. API-Based Detection Flow

### Step 1: API Endpoint Receives Request

**File:** `backend/app/api/anomaly_routes.py`

**Endpoint:**
```
POST /api/v1/anomalies/detect
```

**Request Payload:**
```json
{
  "transaction_id": "tx123",
  "force": false
}
```

**Handler Code:**
```python
@router.post("/detect", response_model=AnomalyResponse, status_code=status.HTTP_201_CREATED)
async def detect_anomaly(
    payload: AnomalyDetectRequest,
    service: AnomalyService = Depends(),
):
    """Run anomaly detection on a transaction and record result on-chain."""
    try:
        return await service.detect_and_record(payload.transaction_id, force=payload.force)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Step 2: AnomalyService Processes Transaction

**File:** `backend/app/services/anomaly/anomaly_service.py`

#### 2.1 Load ML Model

```python
def _load_model(self):
    """Load pre-trained Isolation Forest model"""
    if self._isolation_forest is None:
        model_path = Path(settings.ML_MODEL_PATH) / settings.ISOLATION_FOREST_MODEL
        if model_path.exists():
            with open(model_path, "rb") as f:
                self._isolation_forest = pickle.load(f)
            logger.info("Isolation Forest model loaded")
        else:
            logger.warning(f"Model not found at {model_path}, using mock scores")
```

#### 2.2 Fetch Transaction Features

- Retrieves transaction from database or BigQuery
- Extracts features:
  - Transaction amount
  - Gas ratio
  - Contract interaction flag
  - Timestamp
  - Wallet addresses

#### 2.3 Compute Anomaly Score

```python
def _compute_score(self, features: np.ndarray) -> float:
    """Compute anomaly score using Isolation Forest"""
    if self._isolation_forest:
        raw = self._isolation_forest.decision_function(features)[0]
        # Normalize to [0, 1] where 1 = most anomalous
        return float(1 - (raw - (-0.5)) / 1.0)
    return 0.3  # fallback mock score
```

#### 2.4 Classify Severity

```python
def _classify_severity(self, score: float) -> str:
    """Classify anomaly severity based on score"""
    if score >= 0.9:
        return "critical"
    elif score >= 0.75:
        return "high"
    elif score >= 0.5:
        return "medium"
    return "low"
```

#### 2.5 Return Result

```json
{
  "id": "anom-tx123",
  "transaction_id": "tx123",
  "score": 0.85,
  "severity": "high",
  "status": "pending",
  "features": {"raw": [0.5, 1000.0, 3, 0.2]},
  "detected_at": "2026-07-26T12:00:00Z"
}
```

---

## 2. CSV File-Based Detection Flow

### Step 1: Load Transactions from CSV

**File:** `backend/test_csv_detection.py`  
**CSV Source:** `backend/sample_transactions.csv`

**Loading Process:**
```python
async def load_transactions_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load transactions from CSV file."""
    transactions = []
    csv_file = Path(csv_path)
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transaction = {
                "transaction_hash": row["tx_hash"],
                "from_wallet_address": row["from_address"],
                "to_wallet_address": row["to_address"],
                "amount": float(row["value"]),
                "transaction_timestamp": row["timestamp"],
                "gas_ratio": float(row["gas_ratio"]),
                "is_contract_interaction": row["is_contract_interaction"].lower() == "true",
                "token_symbol": row["token_symbol"],
                "scenario": row.get("scenario", "unknown")
            }
            transactions.append(transaction)
    
    print(f"✅ Loaded {len(transactions)} transactions from CSV")
    return transactions
```

**Sample CSV Structure:**
```csv
tx_hash,from_address,to_address,value,timestamp,gas_ratio,is_contract_interaction,token_symbol,scenario
0xabc...,0x123...,0x456...,9500.0,2026-07-26T10:00:00Z,1.2,false,USDT,threshold_avoidance
```

---

### Step 2: Initialize AnomalyOrchestrator

**File:** `backend/app/services/anomaly/orchestrator.py`

#### 2.1 Initialize Detectors

```python
class AnomalyOrchestrator:
    """Orchestrates multiple anomaly detectors and aggregates results."""
    
    def __init__(self, config: Dict[str, Any] = None, anomaly_result_service=None):
        self.config = config or {}
        self.bq_client = BigQueryReferenceClient()
        self.anomaly_master: Dict[str, Dict[str, Any]] = {}
        self.anomaly_result_service = anomaly_result_service
        
        # Initialize all detectors
        self.detectors: List[BaseDetector] = [
            OffHoursWithdrawalDetector(self.config.get("off_hours", {})),
            ThresholdDepositDetector(self.config.get("threshold_deposit", {})),
            DuplicateEscrowDetector(self.config.get("duplicate_escrow", {})),
            OracleDetector(self.config.get("oracle", {})),
            DailyLimitDetector(self.config.get("daily_limit", {})),
            ReconciliationDetector(self.config.get("reconciliation", {})),
            FullWithdrawalDetector(self.config.get("full_withdrawal", {})),
            TimeWindowDetector(self.config.get("time_window", {})),
        ]
        
        logger.info(f"Initialized {len(self.detectors)} anomaly detectors")
```

**8 Specialized Detectors:**
1. **OffHoursWithdrawalDetector** - Detects after-hours suspicious activity
2. **ThresholdDepositDetector** - Detects threshold avoidance (structuring/smurfing)
3. **DuplicateEscrowDetector** - Detects duplicate escrow attempts
4. **OracleDetector** - Detects oracle price manipulation
5. **DailyLimitDetector** - Detects daily limit violations
6. **ReconciliationDetector** - Detects reconciliation mismatches
7. **FullWithdrawalDetector** - Detects full account draining
8. **TimeWindowDetector** - Detects suspicious time-based patterns

#### 2.2 Load Anomaly Master Table

```python
async def initialize(self):
    """Initialize anomaly master table from BigQuery."""
    self.anomaly_master = await self.bq_client.get_anomaly_master()
    logger.info(f"Loaded {len(self.anomaly_master)} anomaly codes")
```

**Anomaly Master Structure:**
```python
{
  "THRESHOLD_001": {
    "risk_score": 75,
    "category": "FRAUD",
    "description": "Deposit just below regulatory threshold",
    "severity": "high"
  },
  "TIME_WINDOW_003": {
    "risk_score": 60,
    "category": "SUSPICIOUS",
    "description": "Multiple transactions in short time window"
  }
}
```

---

### Step 3: Run Detection on Each Transaction

**Main Detection Pipeline:**
```python
async def detect_all(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run all detectors on a transaction and aggregate results.
    """
    # 1. PREPARE CONTEXT (fetch reference data)
    if not self.anomaly_master:
        await self.initialize()
    
    context = await self._prepare_context(transaction)
    
    # 2. RUN ALL DETECTORS IN PARALLEL
    results: List[AnomalyResult] = []
    for detector in self.detectors:
        try:
            result = await detector.detect(transaction, context)
            results.append(result)
        except Exception as e:
            logger.error(f"{detector.name} failed: {e}")
    
    # 3. AGGREGATE RESULTS
    aggregated = self._aggregate_results(transaction, results, context)
    
    # 4. STORE IN BIGQUERY & POSTGRESQL
    if self.config.get("store_results", True):
        await self._store_results(aggregated)
    
    return aggregated
```

---

### Step 4: Context Preparation (Reference Data)

**Fetch Comprehensive Context from BigQuery:**
```python
async def _prepare_context(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare context data for detectors using BigQuery."""
    from_address = transaction.get("from_wallet_address")
    
    context = {}
    
    try:
        # 1. CLIENT REGISTRY (KYC, limits, risk tier)
        client_registry = await self.bq_client.get_client_registry(from_address)
        context["client_registry"] = client_registry
        
        # 2. ACCOUNT LIMITS (from client registry)
        context["account_limits"] = {
            from_address: {
                "daily_value_limit": client_registry.get("dailyWithdrawalLimit", 50000),
                "daily_count_limit": 100,
                "per_address_value_limit": client_registry.get("dailyWithdrawalLimit", 25000)
            }
        }
        
        # 3. ORACLE REGISTRY (price feed addresses)
        context["oracle_registry"] = await self.bq_client.get_oracle_registry()
        
        # 4. RECENT TRANSACTIONS (last 24 hours)
        recent_txs = await self.bq_client.get_recent_transactions(from_address, lookback_hours=24)
        context["recent_transactions"] = recent_txs
        
        # 5. ACCOUNT BALANCE
        balance = await self.bq_client.get_account_balance(from_address)
        context["account_balance"] = {from_address: balance}
        
        # 6. DERIVED METRICS
        if recent_txs:
            context["tx_count_1h"] = len([
                tx for tx in recent_txs 
                if (datetime.utcnow() - datetime.fromisoformat(tx["timestamp"])).total_seconds() < 3600
            ])
            context["unique_counterparties"] = len(set(tx["to_address"] for tx in recent_txs))
        
    except Exception as e:
        logger.warning(f"Failed to fetch complete context: {e}")
    
    return context
```

**Context Data Structure:**
```python
{
  "client_registry": {
    "client_id": "CLT-001",
    "wallet_address": "0x123...",
    "kyc_status": "VERIFIED",
    "risk_tier": "LOW",
    "dailyWithdrawalLimit": 50000
  },
  "account_limits": {
    "0x123...": {
      "daily_value_limit": 50000,
      "daily_count_limit": 100
    }
  },
  "oracle_registry": {
    "price_feed_addresses": ["0xabc...", "0xdef..."]
  },
  "recent_transactions": [
    {"tx_hash": "0x...", "amount": 1000, "timestamp": "..."}
  ],
  "account_balance": {"0x123...": 100000},
  "tx_count_1h": 5,
  "unique_counterparties": 3
}
```

---

### Step 5: Individual Detector Logic

**Example: ThresholdDepositDetector**

**File:** `backend/app/services/anomaly/detectors/threshold_deposit_detector.py`

#### Detection Process:

**1. Extract Transaction Value**
```python
tx_value = float(transaction.get("amount", 0))
from_address = transaction.get("from_wallet_address")
to_address = transaction.get("to_wallet_address")
```

**2. Rule 1: Check Near Threshold**
```python
def _check_near_threshold(self, value: float) -> Dict[str, Any]:
    """Check if value is just below a known threshold."""
    thresholds = [10000, 5000, 3000]  # Regulatory thresholds
    threshold_margin = 0.05  # 5% below threshold
    
    for threshold in sorted(self.thresholds, reverse=True):
        lower_bound = threshold * (1 - self.threshold_margin)
        upper_bound = threshold
        
        if lower_bound <= value < upper_bound:
            amount_below = threshold - value
            percent_below = (amount_below / threshold) * 100
            return {
                "is_near_threshold": True,
                "threshold": threshold,
                "amount_below": amount_below,
                "percent_below": percent_below
            }
    
    return {"is_near_threshold": False}
```

**3. Rule 2: Pattern Detection (Structuring/Smurfing)**
```python
def _detect_structuring_pattern(
    self, current_value: float, recent_txs: List[Dict], address: str
) -> tuple[bool, Dict[str, Any]]:
    """Detect repeated near-threshold deposits (structuring/smurfing)."""
    near_threshold_txs = []
    
    # Find similar near-threshold deposits
    for tx in recent_txs:
        if tx.get("from_wallet_address") == address:
            tx_value = float(tx.get("amount", 0))
            if self._check_near_threshold(tx_value)["is_near_threshold"]:
                near_threshold_txs.append(tx_value)
    
    # Include current transaction
    if self._check_near_threshold(current_value)["is_near_threshold"]:
        near_threshold_txs.append(current_value)
    
    # Pattern detected if >= 3 similar transactions
    pattern_detected = len(near_threshold_txs) >= 3
    
    stats = {
        "count": len(near_threshold_txs),
        "total_value": sum(near_threshold_txs),
        "avg_value": np.mean(near_threshold_txs) if near_threshold_txs else 0,
        "std_value": np.std(near_threshold_txs) if len(near_threshold_txs) > 1 else 0
    }
    
    return pattern_detected, stats
```

**4. Statistical Outlier Check**
```python
def _statistical_outlier_check(self, value: float, recent_txs: List[Dict]) -> tuple[bool, float]:
    """Use z-score to detect statistical outliers."""
    if len(recent_txs) < 10:
        return False, 0.0
    
    values = [float(tx.get("amount", 0)) for tx in recent_txs]
    values.append(value)
    
    arr = np.array(values, dtype=float)
    mean, std = arr.mean(), arr.std()
    z_scores = np.abs((arr - mean) / std) if std > 0 else np.zeros_like(arr)
    current_z = z_scores[-1]
    
    # 2.5 sigma threshold (99.7% confidence)
    is_outlier = current_z > 2.5
    
    return is_outlier, float(current_z)
```

**5. ML Model Score (Isolation Forest)**
```python
async def _get_ml_anomaly_score(self, transaction: Dict, context: Dict) -> float:
    """Get ML-based anomaly score using Isolation Forest."""
    if not self._model:
        return 0.0
    
    # Extract features
    features = self._extract_features(transaction, context)
    
    # Get Isolation Forest score
    score = self._model.decision_function([features])[0]
    
    # Normalize to [0, 1]
    normalized_score = 1 - (score - (-0.5)) / 1.0
    
    return max(0.0, min(1.0, normalized_score))
```

**6. Combine Signals & Return Result**
```python
async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
    # Execute all checks
    near_threshold_info = self._check_near_threshold(tx_value)
    pattern_detected, pattern_stats = self._detect_structuring_pattern(tx_value, recent_txs, from_address)
    is_statistical_outlier, z_score = self._statistical_outlier_check(tx_value, recent_txs)
    ml_score = await self._get_ml_anomaly_score(transaction, context)
    
    # HIGH CONFIDENCE: Near threshold + Pattern
    if near_threshold_info["is_near_threshold"] and pattern_detected:
        confidence = 0.9 + (ml_score * 0.1)
        return self._create_result(
            is_anomaly=True,
            confidence=min(confidence, 1.0),
            anomaly_code="THRESHOLD_001",
            reasons=[
                f"Deposit ${tx_value:.2f} is {near_threshold_info['percent_below']:.1f}% below ${near_threshold_info['threshold']:.0f} threshold",
                f"Pattern: {pattern_stats['count']} similar deposits in {self.pattern_lookback_days} days",
                f"Total structured amount: ${pattern_stats['total_value']:.2f}",
                f"Statistical Z-score: {z_score:.2f}"
            ],
            metadata={
                "threshold": near_threshold_info["threshold"],
                "margin_below": near_threshold_info["amount_below"],
                "pattern_count": pattern_stats["count"],
                "pattern_total": pattern_stats["total_value"],
                "z_score": z_score,
                "ml_score": ml_score
            }
        )
    
    # MEDIUM CONFIDENCE: Only near threshold
    elif near_threshold_info["is_near_threshold"]:
        confidence = 0.6 + (ml_score * 0.2)
        return self._create_result(
            is_anomaly=True,
            confidence=confidence,
            anomaly_code="THRESHOLD_001",
            reasons=[
                f"Deposit just below ${near_threshold_info['threshold']:.0f} threshold",
                "Possible threshold avoidance"
            ],
            metadata={"threshold": near_threshold_info["threshold"], "ml_score": ml_score}
        )
    
    # NO ANOMALY
    return self._create_result(
        is_anomaly=False,
        confidence=0.1,
        reasons=["No threshold avoidance pattern detected"],
        metadata={"ml_score": ml_score}
    )
```

---

### Step 6: Result Aggregation

**File:** `backend/app/services/anomaly/orchestrator.py`

```python
def _aggregate_results(self, transaction: Dict, results: List[AnomalyResult], context: Dict) -> Dict[str, Any]:
    """Aggregate detection results into final report."""
    
    # Filter only anomalies
    anomalies = [r for r in results if r.is_anomaly]
    
    detection_id = str(uuid.uuid4())
    client_registry = context.get("client_registry", {})
    
    # NO ANOMALIES FOUND
    if not anomalies:
        return {
            "detection_id": detection_id,
            "transaction_id": transaction.get("tx_hash"),
            "is_anomaly": False,
            "overall_score": 0.0,
            "overall_severity": "low",
            "risk_score": 0,
            "anomaly_count": 0,
            "anomaly_codes": [],
            "detections": [],
            "all_reasons": [],
            "client_registry": client_registry,
            "detected_at": datetime.utcnow().isoformat()
        }
    
    # ANOMALIES FOUND - AGGREGATE
    
    # 1. Calculate overall score (max confidence across all detectors)
    overall_score = max(r.confidence for r in anomalies)
    
    # 2. Collect anomaly codes
    anomaly_codes = [r.anomaly_code for r in anomalies if r.anomaly_code]
    
    # 3. Calculate risk score from anomaly master
    total_risk_score = 0
    for code in anomaly_codes:
        if code in self.anomaly_master:
            total_risk_score += self.anomaly_master[code].get("risk_score", 50)
    
    avg_risk_score = total_risk_score // len(anomaly_codes) if anomaly_codes else 0
    
    # 4. Calculate overall severity (highest severity wins)
    severity_priority = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    overall_severity = max(anomalies, key=lambda r: severity_priority[r.severity]).severity
    
    # 5. Collect all reasons from all detectors
    all_reasons = []
    for result in anomalies:
        all_reasons.extend(result.reasons)
    
    # 6. Build detection summary with enrichment
    detections = []
    for r in anomalies:
        detection = {
            "detector": r.detector_name,
            "confidence": r.confidence,
            "severity": r.severity,
            "anomaly_code": r.anomaly_code,
            "reasons": r.reasons,
            "metadata": r.metadata
        }
        
        # Enrich with anomaly master data
        if r.anomaly_code and r.anomaly_code in self.anomaly_master:
            master = self.anomaly_master[r.anomaly_code]
            detection["category"] = master.get("category")
            detection["risk_score"] = master.get("risk_score")
            detection["description"] = master.get("description")
        
        detections.append(detection)
    
    # 7. Return aggregated result
    return {
        "detection_id": detection_id,
        "transaction_id": transaction.get("tx_hash"),
        "is_anomaly": True,
        "overall_score": overall_score,
        "overall_severity": overall_severity,
        "risk_score": avg_risk_score,
        "anomaly_count": len(anomalies),
        "anomaly_codes": anomaly_codes,
        "detections": detections,
        "all_reasons": all_reasons,
        "client_registry": client_registry,
        "detected_at": datetime.utcnow().isoformat(),
        "transaction_summary": {
            "from": transaction.get("from_address"),
            "to": transaction.get("to_address"),
            "value": transaction.get("value"),
            "timestamp": transaction.get("timestamp")
        }
    }
```

**Example Aggregated Result:**
```json
{
  "detection_id": "550e8400-e29b-41d4-a716-446655440000",
  "transaction_id": "0xabc123...",
  "is_anomaly": true,
  "overall_score": 0.85,
  "overall_severity": "high",
  "risk_score": 78,
  "anomaly_count": 2,
  "anomaly_codes": ["THRESHOLD_001", "TIME_WINDOW_003"],
  "detections": [
    {
      "detector": "ThresholdDepositDetector",
      "confidence": 0.9,
      "severity": "high",
      "anomaly_code": "THRESHOLD_001",
      "reasons": [
        "Deposit $9,500 is 5% below $10,000 threshold",
        "Pattern: 4 similar deposits in 7 days",
        "Total structured: $38,000"
      ],
      "category": "FRAUD",
      "risk_score": 75,
      "description": "Deposit just below regulatory threshold"
    },
    {
      "detector": "TimeWindowDetector",
      "confidence": 0.8,
      "severity": "medium",
      "anomaly_code": "TIME_WINDOW_003",
      "reasons": [
        "3 transactions in 5-minute window",
        "Unusual velocity pattern"
      ],
      "category": "SUSPICIOUS",
      "risk_score": 60
    }
  ],
  "all_reasons": [
    "Deposit $9,500 is 5% below $10,000 threshold",
    "Pattern: 4 similar deposits in 7 days",
    "Total structured: $38,000",
    "3 transactions in 5-minute window",
    "Unusual velocity pattern"
  ],
  "detected_at": "2026-07-26T12:30:00Z"
}
```

---

### Step 7: Storage

**Store Results in Multiple Databases:**

```python
async def _store_results(self, aggregated: Dict[str, Any]):
    """Store detection results in BigQuery and optionally PostgreSQL."""
    
    # 1. STORE IN BIGQUERY
    try:
        await self.bq_client.store_anomaly_detection(aggregated)
        logger.info(f"Stored detection result in BigQuery for {aggregated['transaction_id']}")
    except Exception as e:
        logger.error(f"Failed to store in BigQuery: {e}")
    
    # 2. STORE IN POSTGRESQL (if service available)
    if self.anomaly_result_service and aggregated.get("is_anomaly"):
        try:
            # Extract anomaly types and reasons
            anomaly_types = aggregated.get("anomaly_codes", [])
            anomaly_reasons = [
                {
                    "reasonCode": reason.split(":")[0].strip() if ":" in reason else "ANOMALY",
                    "description": reason
                }
                for reason in aggregated.get("all_reasons", [])
            ]
            
            # Get transaction summary
            tx_summary = aggregated.get("transaction_summary", {})
            
            # Prepare transaction data
            transaction_data = {
                "transaction_id": aggregated.get("transaction_id"),
                "transaction_hash": aggregated.get("transaction_id"),
                "client_id": aggregated.get("client_registry", {}).get("client_id"),
                "amount": tx_summary.get("value"),
                "currency": "INR",
                "from_wallet_address": tx_summary.get("from"),
                "to_wallet_address": tx_summary.get("to"),
                "transaction_type": "BLOCKCHAIN",
            }
            
            # Store in PostgreSQL anomaly_results table
            await self.anomaly_result_service.store_anomaly_result(
                transaction=transaction_data,
                anomaly_score=aggregated.get("overall_score", 0.0),
                anomaly_types=anomaly_types,
                anomaly_reasons=anomaly_reasons,
                confidence=aggregated.get("overall_score", 0.0),
                model_name="Ensemble",
                model_version="v1.0"
            )
            
            logger.info(f"Stored in PostgreSQL for {transaction_data['transaction_id']}")
        except Exception as e:
            logger.error(f"Failed to store in PostgreSQL: {e}", exc_info=True)
```

**Database Tables:**

**BigQuery: `anomaly_detections` table**
```sql
CREATE TABLE anomaly_detections (
  detection_id STRING,
  transaction_id STRING,
  is_anomaly BOOLEAN,
  overall_score FLOAT64,
  overall_severity STRING,
  risk_score INT64,
  anomaly_codes ARRAY<STRING>,
  detections JSON,
  detected_at TIMESTAMP
)
```

**PostgreSQL: `anomaly_results` table**
```sql
CREATE TABLE anomaly_results (
  anomaly_id UUID PRIMARY KEY,
  transaction_id VARCHAR(255),
  transaction_hash VARCHAR(255),
  client_id VARCHAR(255),
  anomaly_score DECIMAL(5,4),
  severity VARCHAR(50),
  anomaly_category VARCHAR(100),
  anomaly_types TEXT[],
  anomaly_reasons JSONB,
  confidence DECIMAL(5,4),
  model_name VARCHAR(100),
  model_version VARCHAR(50),
  detected_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
)
```

---

## 3. Detection Components

### A. Base Detector Interface

**File:** `backend/app/services/anomaly/detectors/base_detector.py`

```python
class AnomalyResult:
    """Standard result format for all detectors."""
    
    def __init__(
        self,
        is_anomaly: bool,
        detector_name: str,
        confidence: float,        # 0.0 to 1.0
        severity: str,            # low, medium, high, critical
        anomaly_code: str,        # Maps to anomaly_master table
        reasons: List[str],
        metadata: Dict[str, Any],
        detected_at: Optional[datetime] = None
    ):
        self.is_anomaly = is_anomaly
        self.detector_name = detector_name
        self.confidence = confidence
        self.severity = severity
        self.anomaly_code = anomaly_code
        self.reasons = reasons
        self.metadata = metadata
        self.detected_at = detected_at or datetime.utcnow()


class BaseDetector(ABC):
    """Abstract base class for all anomaly detectors."""
    
    @abstractmethod
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Detect anomalies in a transaction.
        
        Args:
            transaction: Transaction data (value, from_address, to_address, timestamp, etc.)
            context: Additional context (historical transactions, reference data, etc.)
        
        Returns:
            AnomalyResult with detection outcome
        """
        pass
```

---

### B. Detection Methods

#### 1. Rule-Based Detection
- **Threshold checks**: Amount > $10,000
- **Time-based rules**: Transaction at 3:00 AM
- **Pattern matching**: 3+ similar transactions in 7 days
- **Relationship rules**: Sender in blacklist

#### 2. Statistical Analysis
- **Z-score outlier detection**: `z = |x - μ| / σ > 2.5`
- **Moving averages**: Compare to 30-day average
- **Standard deviation**: Detect variance anomalies
- **Percentile-based**: Values in top/bottom 5%

#### 3. Machine Learning
- **Isolation Forest** (Unsupervised)
  - Trained on historical transaction data
  - Isolates anomalies by random forest partitioning
  - Returns anomaly score: -0.5 to 0.5 (normalized to 0-1)
- **Autoencoder** (Deep Learning)
  - Reconstruction error indicates anomaly
  - Trained on normal transaction patterns
- **Ensemble Methods**
  - Combines multiple model scores
  - Weighted voting or max score

#### 4. Context-Aware Analysis
- **Client history**: Compare to user's typical behavior
- **Account limits**: Check against daily/monthly limits
- **Network relationships**: Analyze wallet connections
- **Temporal patterns**: Time-of-day, day-of-week analysis
- **Geographic patterns**: Location-based risk assessment

---

## 4. Complete Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INPUT: Transaction                               │
│                   (API Request or CSV File)                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: INITIALIZE ORCHESTRATOR                                    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Load 8 Specialized Detectors:                             │    │
│  │  • OffHoursWithdrawalDetector                              │    │
│  │  • ThresholdDepositDetector                                │    │
│  │  • DuplicateEscrowDetector                                 │    │
│  │  • OracleDetector                                          │    │
│  │  • DailyLimitDetector                                      │    │
│  │  • ReconciliationDetector                                  │    │
│  │  • FullWithdrawalDetector                                  │    │
│  │  • TimeWindowDetector                                      │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Load Anomaly Master Table from BigQuery:                  │    │
│  │  {                                                          │    │
│  │    "THRESHOLD_001": {risk_score: 75, category: "FRAUD"},   │    │
│  │    "TIME_WINDOW_003": {risk_score: 60, ...}                │    │
│  │  }                                                          │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: PREPARE CONTEXT (Fetch Reference Data from BigQuery)      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. Client Registry                                        │    │
│  │     - KYC status, Risk tier, Withdrawal limits             │    │
│  │  2. Account Limits                                         │    │
│  │     - Daily value/count limits                             │    │
│  │  3. Oracle Registry                                        │    │
│  │     - Price feed addresses                                 │    │
│  │  4. Recent Transactions (24h)                              │    │
│  │     - Historical transaction data                          │    │
│  │  5. Account Balance                                        │    │
│  │     - Current wallet balance                               │    │
│  │  6. Derived Metrics                                        │    │
│  │     - tx_count_1h, unique_counterparties                   │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: RUN ALL DETECTORS IN PARALLEL                             │
│                                                                     │
│  ┌───────────────────────┐  ┌───────────────────────┐             │
│  │ ThresholdDetector     │  │ OffHoursDetector      │             │
│  │ ─────────────────     │  │ ────────────────      │             │
│  │ 1. Rule checks        │  │ 1. Time checks        │             │
│  │ 2. Pattern analysis   │  │ 2. Behavioral AI      │             │
│  │ 3. Statistical tests  │  │ 3. Context analysis   │             │
│  │ 4. ML scoring         │  │ 4. Risk scoring       │             │
│  └──────────┬────────────┘  └──────────┬────────────┘             │
│             │                           │                           │
│  ┌──────────▼────────────┐  ┌──────────▼────────────┐             │
│  │ DailyLimitDetector    │  │ OracleDetector        │             │
│  │ ──────────────────    │  │ ──────────────        │             │
│  │ Checks daily limits   │  │ Detects oracle manip  │             │
│  └───────────────────────┘  └───────────────────────┘             │
│                                                                     │
│  ┌──────────────────────────────────────────────────┐             │
│  │ Each detector returns AnomalyResult:             │             │
│  │ {                                                 │             │
│  │   is_anomaly: true/false,                        │             │
│  │   confidence: 0.0-1.0,                           │             │
│  │   severity: "critical"|"high"|"medium"|"low",    │             │
│  │   anomaly_code: "THRESHOLD_001",                 │             │
│  │   reasons: ["Deposit below threshold", ...],     │             │
│  │   metadata: {threshold: 10000, ...}              │             │
│  │ }                                                 │             │
│  └──────────────────────────────────────────────────┘             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: AGGREGATE RESULTS                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. Filter anomalies (is_anomaly = True)                   │    │
│  │  2. Calculate overall_score = max(confidence)               │    │
│  │  3. Determine overall_severity (critical > high > medium)   │    │
│  │  4. Calculate risk_score from anomaly_master                │    │
│  │  5. Collect all anomaly_codes                               │    │
│  │  6. Collect all reasons from all detectors                  │    │
│  │  7. Enrich with anomaly_master metadata                     │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Aggregated Result:                                         │    │
│  │  {                                                          │    │
│  │    detection_id: "uuid",                                    │    │
│  │    transaction_id: "0xabc...",                              │    │
│  │    is_anomaly: true,                                        │    │
│  │    overall_score: 0.85,                                     │    │
│  │    overall_severity: "high",                                │    │
│  │    risk_score: 78,                                          │    │
│  │    anomaly_count: 2,                                        │    │
│  │    anomaly_codes: ["THRESHOLD_001", "TIME_003"],           │    │
│  │    detections: [{detector, confidence, reasons}, ...],      │    │
│  │    all_reasons: ["...", "..."]                              │    │
│  │  }                                                          │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: STORE RESULTS                                              │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  1. BigQuery: anomaly_detections table                     │    │
│  │     - Full detection details with JSON                     │    │
│  │  2. PostgreSQL: anomaly_results table                      │    │
│  │     - Normalized relational structure                      │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    OUTPUT: Detection Result                         │
│  {                                                                  │
│    "is_anomaly": true,                                              │
│    "overall_score": 0.85,                                           │
│    "overall_severity": "high",                                      │
│    "risk_score": 78,                                                │
│    "anomaly_codes": ["THRESHOLD_001", "TIME_WINDOW_003"],          │
│    "detections": [                                                  │
│      {                                                              │
│        "detector": "ThresholdDepositDetector",                      │
│        "confidence": 0.9,                                           │
│        "severity": "high",                                          │
│        "reasons": [                                                 │
│          "Deposit $9,500 is 5% below $10,000 threshold",            │
│          "Pattern: 4 similar deposits in 7 days"                    │
│        ]                                                            │
│      }                                                              │
│    ]                                                                │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Code References

### Key Files

| Component | File Path | Description |
|-----------|-----------|-------------|
| **API Routes** | `backend/app/api/anomaly_routes.py` | FastAPI endpoints for anomaly detection |
| **Orchestrator** | `backend/app/services/anomaly/orchestrator.py` | Main detection orchestrator |
| **Base Detector** | `backend/app/services/anomaly/detectors/base_detector.py` | Abstract base class for detectors |
| **Threshold Detector** | `backend/app/services/anomaly/detectors/threshold_deposit_detector.py` | Detects threshold avoidance |
| **Off Hours Detector** | `backend/app/services/anomaly/detectors/off_hours_detector.py` | Detects after-hours activity |
| **CSV Test Script** | `backend/test_csv_detection.py` | Load & test from CSV files |
| **BigQuery Client** | `backend/app/clients/bigquery/reference_data_client.py` | Fetch reference data |

### Database Schemas

**BigQuery Tables:**
- `anomaly_master` - Anomaly code definitions with risk scores
- `client_registry` - Client KYC and limits
- `oracle_registry` - Price feed addresses
- `anomaly_detections` - Detection results

**PostgreSQL Tables:**
- `anomaly_results` - Normalized anomaly detection results
- `transactions` - Transaction details

---

## Summary

The anomaly detection system uses a **multi-layered approach**:

1. **Rule-Based Detection** - Fast, explainable threshold and pattern checks
2. **Statistical Analysis** - Z-score and variance-based outlier detection
3. **Machine Learning** - Isolation Forest for unsupervised anomaly detection
4. **Context-Aware** - Uses historical data, client profiles, and network analysis

Each transaction is evaluated by **8 specialized detectors**, and results are aggregated into a single comprehensive report with:
- Overall anomaly score (0.0 - 1.0)
- Severity classification (low, medium, high, critical)
- Risk score (weighted by anomaly master)
- Multiple anomaly codes with detailed reasons
- Enriched metadata for investigation

The system supports both **real-time API-based detection** and **batch CSV file processing** for testing and validation.
