---
name: ml-engine
description: "Use when working on machine learning models, training, evaluation, feature engineering, or inference for anomaly detection in ml-engine/"
user-invocable: true
---

# ML Engine Development Skill

You are an expert in machine learning for financial transaction anomaly detection.

## Project Context

- **ML Libraries**: Scikit-learn, PyTorch, NumPy, Pandas
- **Models**: Isolation Forest + Autoencoder ensemble
- **Task**: Unsupervised anomaly detection on transaction features
- **Deployment**: Pickle (sklearn) + PyTorch state dict

## Directory Structure

```
ml-engine/
├── training/
│   ├── train.py              # Model training script
│   ├── evaluate.py           # Model evaluation metrics
│   └── feature_engineering.py # Feature extraction
├── inference/
│   ├── predictor.py          # Ensemble predictor
│   └── risk_scorer.py        # Risk classification
├── models/                   # Serialized models (.pkl, .pt)
├── datasets/                 # Training/test data (CSV)
└── notebooks/                # Jupyter exploration
```

## Feature Engineering

### Transaction Features
```python
def extract_features(transaction: dict) -> np.ndarray:
    """
    Returns: [value_log, tx_count_1h, time_since_last, 
              unique_counterparties, gas_ratio, is_contract]
    """
    features = np.array([
        np.log10(transaction["value"] + 1),
        transaction["tx_count_1h"],
        np.log10(transaction["time_since_last_tx"] + 1),
        transaction["unique_counterparties"],
        transaction["gas_ratio"],
        float(transaction["is_contract_interaction"]),
    ])
    return features.reshape(1, -1)
```

### Feature Set
| Feature | Description | Transform |
|---------|-------------|-----------|
| `value_log` | Transaction amount | log10(value + 1) |
| `tx_count_1h` | Address activity in last hour | raw count |
| `time_since_last` | Seconds since last tx from address | log10(seconds + 1) |
| `unique_counterparties` | Distinct addresses interacted with | raw count |
| `gas_ratio` | gas_used / gas_limit | 0-1 ratio |
| `is_contract` | Contract interaction flag | 0 or 1 |

## Model Architecture

### Isolation Forest
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(
    n_estimators=200,
    contamination=0.05,  # Expected fraud rate
    max_samples="auto",
    random_state=42,
)
model.fit(X_train)

# Score: -1 = anomaly, 1 = normal
raw_scores = model.decision_function(X_test)
normalized = 1 - (raw_scores - min) / (max - min)  # 0-1 range
```

### Autoencoder (PyTorch)
```python
import torch.nn as nn

class TransactionAutoencoder(nn.Module):
    def __init__(self, input_dim=6):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 12),
            nn.ReLU(),
            nn.Linear(12, 6),
            nn.ReLU(),
            nn.Linear(6, 3),
        )
        self.decoder = nn.Sequential(
            nn.Linear(3, 6),
            nn.ReLU(),
            nn.Linear(6, 12),
            nn.ReLU(),
            nn.Linear(12, input_dim),
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# Anomaly score = reconstruction error
with torch.no_grad():
    reconstructed = model(X)
    mse = torch.mean((X - reconstructed) ** 2, dim=1)
```

### Ensemble Scoring
```python
# Weighted combination
WEIGHTS = {
    "isolation_forest": 0.6,
    "autoencoder": 0.4,
}

final_score = (
    WEIGHTS["isolation_forest"] * if_score +
    WEIGHTS["autoencoder"] * ae_score
)
```

## Training Pipeline

### 1. Data Preparation
```python
df = pd.read_csv("datasets/transactions.csv")
X, feature_names = build_feature_matrix(df)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### 2. Train Models
```python
# Isolation Forest
iso_forest = train_isolation_forest(X_scaled, contamination=0.05)
with open("models/isolation_forest.pkl", "wb") as f:
    pickle.dump(iso_forest, f)

# Autoencoder
autoencoder = train_autoencoder(X_scaled, epochs=100)
torch.save(autoencoder.state_dict(), "models/autoencoder.pt")
```

### 3. Evaluate
```python
from sklearn.metrics import roc_auc_score, average_precision_score

y_pred = ensemble_predict(X_test)
roc_auc = roc_auc_score(y_true, y_pred)
avg_precision = average_precision_score(y_true, y_pred)
```

## Inference Pattern

```python
# predictor.py
class AnomalyPredictor:
    def __init__(self):
        with open("models/isolation_forest.pkl", "rb") as f:
            self.if_model = pickle.load(f)
        with open("models/scaler.pkl", "rb") as f:
            self.scaler = pickle.load(f)
        self.ae_model = torch.load("models/autoencoder.pt")
    
    def predict(self, features: np.ndarray) -> dict:
        X = self.scaler.transform(features)
        
        if_score = self.if_model.decision_function(X)[0]
        if_score = normalize_score(if_score)
        
        tensor = torch.tensor(X, dtype=torch.float32)
        with torch.no_grad():
            recon = self.ae_model(tensor)
            ae_score = float(torch.mean((recon - tensor) ** 2))
        
        ensemble = 0.6 * if_score + 0.4 * ae_score
        
        return {
            "ensemble_score": ensemble,
            "is_anomaly": ensemble >= 0.5,
            "isolation_forest_score": if_score,
            "autoencoder_score": ae_score,
        }
```

## Risk Classification

```python
def classify_severity(score: float) -> str:
    if score >= 0.90: return "critical"
    if score >= 0.75: return "high"
    if score >= 0.50: return "medium"
    return "low"
```

## Operating Rules

1. **Normalize Features**: Always log-transform skewed features (value, time)
2. **Scale Before Inference**: Use the same scaler as training
3. **Contamination Rate**: Set based on domain knowledge (fraud rate ~5%)
4. **Ensemble Weights**: Tune based on validation performance
5. **Threshold Tuning**: Balance precision/recall for production use
6. **Model Versioning**: Save metadata.json with model artifacts

## Common Tasks

### Retrain Models
```bash
# Generate synthetic data
python scripts/seed_data.py

# Train
python ml-engine/training/train.py datasets/transactions.csv

# Evaluate
python ml-engine/training/evaluate.py datasets/labeled_transactions.csv
```

### Add New Features
1. Add feature extraction logic in `feature_engineering.py`
2. Update feature count in model initialization
3. Retrain both Isolation Forest and Autoencoder
4. Update scaler with new feature dimensionality

### Tune Hyperparameters
- Isolation Forest: `n_estimators`, `contamination`, `max_samples`
- Autoencoder: learning rate, hidden layer sizes, epochs
- Ensemble: adjust weights based on cross-validation

## Anti-patterns

- ❌ Don't train on unscaled features
- ❌ Don't use different scalers for train/test
- ❌ Don't ignore class imbalance (anomalies are rare)
- ❌ Don't use accuracy — use ROC-AUC, precision, recall
- ❌ Don't forget to save scaler alongside model

## Validation

After changes:
1. Check model file exists: `ls ml-engine/models/*.pkl`
2. Run evaluation: `python ml-engine/training/evaluate.py`
3. Verify metrics: ROC-AUC > 0.85, Average Precision > 0.70
4. Test inference: load model and score sample transaction
