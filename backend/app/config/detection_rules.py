"""
Default detection rules and thresholds configuration.
These are used as fallbacks when BigQuery reference data is unavailable.
"""

# Daily transaction limits
DEFAULT_DAILY_LIMITS = {
    "daily_value_limit": 50000.0,
    "daily_count_limit": 100,
    "per_address_value_limit": 25000.0
}

# Regulatory reporting thresholds (USD equivalent)
REGULATORY_THRESHOLDS = [
    10000,  # US CTR threshold
    5000,   # Suspicious activity threshold
    3000,   # Enhanced monitoring threshold
    1000,   # Internal review threshold
]

# Threshold margin for structuring detection
THRESHOLD_MARGIN = 0.05  # 5% below threshold triggers alert

# Full withdrawal thresholds
FULL_WITHDRAWAL_THRESHOLDS = {
    "min_threshold": 0.90,  # 90%
    "max_threshold": 1.00,  # 100%
}

# Time window rules
BUSINESS_HOURS = {
    "start": 9,   # 9 AM
    "end": 17,    # 5 PM
}

HIGH_RISK_HOURS = [0, 1, 2, 3, 4, 5, 22, 23]  # Midnight to 5 AM, 10 PM to midnight

# Oracle registry (recognized oracle addresses)
RECOGNIZED_ORACLES = {
    "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419",  # Chainlink ETH/USD
    "0xf4030086522a5beea4988f8ca5b36dbc97bee88c",  # Chainlink BTC/USD
    "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",  # Band Protocol Oracle
    "0x0567f2323251f0aab15c8dfb1967e4e8a7d42aee",  # Chainlink LINK/USD
    "0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6",  # Chainlink USDC/USD
}

# Duplicate escrow detection
DUPLICATE_ESCROW_CONFIG = {
    "similarity_threshold": 0.95,
    "lookback_hours": 72,
    "value_tolerance": 0.01,  # 1%
    "time_window_minutes": 60
}

# Reconciliation tolerance
RECONCILIATION_CONFIG = {
    "tolerance": 0.001,  # 0.1%
    "lookback_minutes": 60
}

# ML model paths
ML_MODEL_PATHS = {
    "isolation_forest": "ml-engine/models/isolation_forest.pkl",
    "autoencoder": "ml-engine/models/autoencoder.pt",
    "time_anomaly": "ml-engine/models/time_anomaly.pkl",
    "scaler": "ml-engine/models/scaler.pkl"
}

# Anomaly score thresholds
ANOMALY_SCORE_THRESHOLDS = {
    "critical": 0.90,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25
}

# Pattern detection minimums
PATTERN_DETECTION = {
    "min_pattern_count": 3,
    "lookback_days": 7
}
