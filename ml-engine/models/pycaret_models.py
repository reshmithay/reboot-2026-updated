"""
PyCaret-based anomaly detection models for behavioral patterns.
Uses unsupervised learning for anomaly detection with auto-tuning.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import pickle
import joblib

try:
    from pycaret.anomaly import setup, create_model, save_model, load_model, predict_model
    PYCARET_AVAILABLE = True
except ImportError:
    PYCARET_AVAILABLE = False
    print("PyCaret not available. Install with: pip install pycaret")

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


class PyCaretAnomalyDetector:
    """PyCaret-based anomaly detector with multiple algorithms."""
    
    def __init__(self, model_type: str = "iforest"):
        """
        Initialize PyCaret anomaly detector.
        
        Args:
            model_type: 'iforest' (Isolation Forest), 'knn', 'lof', 'svm', 'pca'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.setup_complete = False
        self.model_dir = Path("ml-engine/models/pycaret")
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def train(self, data: pd.DataFrame, fraction: float = 0.05) -> Dict[str, Any]:
        """
        Train anomaly detection model using PyCaret.
        
        Args:
            data: Training data with features
            fraction: Expected fraction of outliers (default 5%)
        
        Returns:
            Training metrics
        """
        if not PYCARET_AVAILABLE:
            logger.warning("PyCaret not available, using sklearn fallback")
            return self._train_sklearn_fallback(data, fraction)
        
        try:
            logger.info(f"Training {self.model_type} model with {len(data)} samples")
            
            # Initialize PyCaret setup
            anomaly_setup = setup(
                data=data,
                session_id=123,
                silent=True,
                verbose=False
            )
            self.setup_complete = True
            
            # Create model
            self.model = create_model(self.model_type, fraction=fraction)
            
            # Save model
            model_path = self.model_dir / f"{self.model_type}_model"
            save_model(self.model, str(model_path))
            
            logger.info(f"Model saved to {model_path}")
            
            return {
                "model_type": self.model_type,
                "samples": len(data),
                "features": list(data.columns),
                "fraction": fraction,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"PyCaret training failed: {e}, falling back to sklearn")
            return self._train_sklearn_fallback(data, fraction)
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomalies.
        
        Returns:
            DataFrame with 'Anomaly' column (1=anomaly, 0=normal) and 'Anomaly_Score'
        """
        if not PYCARET_AVAILABLE or self.model is None:
            return self._predict_sklearn_fallback(data)
        
        try:
            predictions = predict_model(self.model, data=data)
            return predictions
        except Exception as e:
            logger.error(f"PyCaret prediction failed: {e}")
            return self._predict_sklearn_fallback(data)
    
    def load(self, model_name: str):
        """Load a saved model."""
        if PYCARET_AVAILABLE:
            try:
                model_path = self.model_dir / model_name
                self.model = load_model(str(model_path))
                logger.info(f"Loaded model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load PyCaret model: {e}")
        else:
            # Load sklearn model
            model_path = self.model_dir / f"{model_name}.pkl"
            if model_path.exists():
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded sklearn model from {model_path}")
    
    def _train_sklearn_fallback(self, data: pd.DataFrame, fraction: float) -> Dict[str, Any]:
        """Fallback to sklearn Isolation Forest."""
        logger.info("Using sklearn Isolation Forest fallback")
        
        # Scale data
        X = self.scaler.fit_transform(data)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=fraction,
            random_state=42,
            n_estimators=100
        )
        self.model.fit(X)
        
        # Save model
        model_path = self.model_dir / f"{self.model_type}_sklearn.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump((self.model, self.scaler), f)
        
        return {
            "model_type": "sklearn_iforest",
            "samples": len(data),
            "features": list(data.columns),
            "status": "success_fallback"
        }
    
    def _predict_sklearn_fallback(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fallback prediction using sklearn."""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        X = self.scaler.transform(data)
        predictions = self.model.predict(X)
        scores = self.model.score_samples(X)
        
        # Convert to PyCaret-like format
        result = data.copy()
        result['Anomaly'] = (predictions == -1).astype(int)
        result['Anomaly_Score'] = -scores  # Invert so higher = more anomalous
        
        return result


class BehavioralAnomalyDetector:
    """Specialized detector for behavioral anomalies using PyCaret."""
    
    def __init__(self):
        self.velocity_model = PyCaretAnomalyDetector("iforest")
        self.pattern_model = PyCaretAnomalyDetector("knn")
        self.clustering_model = DBSCAN(eps=0.5, min_samples=5)
    
    def extract_features(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract behavioral features from transactions."""
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        features = {
            'tx_count_1h': [],
            'tx_count_24h': [],
            'total_value_1h': [],
            'total_value_24h': [],
            'avg_tx_value': [],
            'std_tx_value': [],
            'unique_counterparties': [],
            'avg_time_between_tx': [],
            'night_tx_ratio': [],
            'weekend_tx_ratio': [],
            'value_velocity': [],
        }
        
        # Calculate features per wallet
        for address, group in df.groupby('from_address'):
            group = group.sort_values('timestamp')
            
            features['tx_count_1h'].append(len(group.tail(10)))
            features['tx_count_24h'].append(len(group))
            features['total_value_1h'].append(group.tail(10)['value'].sum())
            features['total_value_24h'].append(group['value'].sum())
            features['avg_tx_value'].append(group['value'].mean())
            features['std_tx_value'].append(group['value'].std())
            features['unique_counterparties'].append(group['to_address'].nunique())
            
            # Time features
            time_diffs = pd.to_datetime(group['timestamp']).diff().dt.total_seconds()
            features['avg_time_between_tx'].append(time_diffs.mean())
            
            # Night and weekend ratios
            timestamps = pd.to_datetime(group['timestamp'])
            night_mask = (timestamps.dt.hour < 6) | (timestamps.dt.hour > 22)
            weekend_mask = timestamps.dt.dayofweek >= 5
            features['night_tx_ratio'].append(night_mask.sum() / len(group))
            features['weekend_tx_ratio'].append(weekend_mask.sum() / len(group))
            
            # Value velocity (value / time)
            if len(group) > 1:
                time_span = (timestamps.max() - timestamps.min()).total_seconds() / 3600
                features['value_velocity'].append(group['value'].sum() / max(time_span, 1))
            else:
                features['value_velocity'].append(0)
        
        return pd.DataFrame(features)
    
    def detect_velocity_anomaly(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Detect abnormal transaction velocity."""
        features = self.extract_features(transactions)
        
        if features.empty:
            return {"is_anomaly": False, "score": 0.0}
        
        # Use velocity-specific features
        velocity_features = features[['tx_count_1h', 'value_velocity', 'avg_time_between_tx']]
        
        try:
            predictions = self.velocity_model.predict(velocity_features)
            
            anomaly_count = predictions['Anomaly'].sum()
            avg_score = predictions['Anomaly_Score'].mean()
            
            return {
                "is_anomaly": anomaly_count > 0,
                "anomaly_count": int(anomaly_count),
                "score": float(avg_score),
                "anomaly_ratio": anomaly_count / len(features)
            }
        except Exception as e:
            logger.error(f"Velocity detection failed: {e}")
            return {"is_anomaly": False, "score": 0.0, "error": str(e)}


def train_all_models(historical_data: pd.DataFrame):
    """Train all PyCaret models for different anomaly types."""
    logger.info("Training all anomaly detection models")
    
    models = {
        "velocity": PyCaretAnomalyDetector("iforest"),
        "pattern": PyCaretAnomalyDetector("knn"),
        "clustering": PyCaretAnomalyDetector("lof"),
        "time": PyCaretAnomalyDetector("pca")
    }
    
    results = {}
    for name, model in models.items():
        logger.info(f"Training {name} model...")
        results[name] = model.train(historical_data, fraction=0.05)
    
    return results
