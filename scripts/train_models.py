"""
Model training script for PyCaret anomaly detection models.
Run this to train all ML models on historical transaction data.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

from ml_engine.models.pycaret_models import PyCaretAnomalyDetector, BehavioralAnomalyDetector, train_all_models
from app.clients.bigquery.reference_data_client import BigQueryReferenceClient
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


async def fetch_training_data(lookback_days: int = 90) -> pd.DataFrame:
    """Fetch historical transaction data from BigQuery."""
    bq_client = BigQueryReferenceClient()
    
    logger.info(f"Fetching {lookback_days} days of historical data...")
    
    # In production, fetch from BigQuery
    # For now, generate synthetic data
    return generate_synthetic_data(num_samples=10000)


def generate_synthetic_data(num_samples: int = 10000) -> pd.DataFrame:
    """Generate synthetic transaction data for training."""
    np.random.seed(42)
    
    # Normal transactions
    normal_count = int(num_samples * 0.95)
    normal_data = {
        'value': np.random.lognormal(mean=8, sigma=2, size=normal_count),
        'gas_ratio': np.random.normal(0.5, 0.1, normal_count),
        'hour': np.random.choice(range(9, 18), normal_count),  # Business hours
        'day_of_week': np.random.choice(range(0, 5), normal_count),  # Weekdays
        'tx_count_1h': np.random.poisson(2, normal_count),
        'unique_counterparties': np.random.poisson(3, normal_count),
        'is_contract': np.random.choice([0, 1], normal_count, p=[0.7, 0.3])
    }
    
    # Anomalous transactions (5%)
    anomaly_count = num_samples - normal_count
    anomaly_data = {
        'value': np.random.lognormal(mean=11, sigma=1, size=anomaly_count),  # Higher values
        'gas_ratio': np.random.normal(0.8, 0.15, anomaly_count),
        'hour': np.random.choice([22, 23, 0, 1, 2, 3], anomaly_count),  # Off hours
        'day_of_week': np.random.choice([5, 6], anomaly_count),  # Weekends
        'tx_count_1h': np.random.poisson(10, anomaly_count),  # High velocity
        'unique_counterparties': np.random.poisson(1, anomaly_count),  # Low diversity
        'is_contract': np.random.choice([0, 1], anomaly_count, p=[0.3, 0.7])
    }
    
    # Combine
    normal_df = pd.DataFrame(normal_data)
    anomaly_df = pd.DataFrame(anomaly_data)
    
    df = pd.concat([normal_df, anomaly_df], ignore_index=True)
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    logger.info(f"Generated {len(df)} synthetic transactions ({anomaly_count} anomalies)")
    return df


def train_velocity_model(data: pd.DataFrame):
    """Train velocity anomaly detection model."""
    logger.info("Training velocity model...")
    
    velocity_features = data[['value', 'tx_count_1h', 'unique_counterparties']].copy()
    velocity_features['value_log'] = np.log10(velocity_features['value'] + 1)
    velocity_features = velocity_features.drop('value', axis=1)
    
    model = PyCaretAnomalyDetector(model_type="iforest")
    results = model.train(velocity_features, fraction=0.05)
    
    logger.info(f"Velocity model trained: {results}")
    return model


def train_time_anomaly_model(data: pd.DataFrame):
    """Train time-based anomaly model."""
    logger.info("Training time anomaly model...")
    
    time_features = data[['hour', 'day_of_week']].copy()
    
    # Cyclical encoding
    time_features['hour_sin'] = np.sin(2 * np.pi * time_features['hour'] / 24)
    time_features['hour_cos'] = np.cos(2 * np.pi * time_features['hour'] / 24)
    time_features['is_weekend'] = (time_features['day_of_week'] >= 5).astype(int)
    time_features = time_features.drop(['hour', 'day_of_week'], axis=1)
    
    model = PyCaretAnomalyDetector(model_type="iforest")
    results = model.train(time_features, fraction=0.05)
    
    logger.info(f"Time anomaly model trained: {results}")
    return model


def train_value_anomaly_model(data: pd.DataFrame):
    """Train value-based anomaly model (threshold detection)."""
    logger.info("Training value anomaly model...")
    
    value_features = data[['value', 'gas_ratio']].copy()
    value_features['value_log'] = np.log10(value_features['value'] + 1)
    value_features = value_features.drop('value', axis=1)
    
    model = PyCaretAnomalyDetector(model_type="iforest")
    results = model.train(value_features, fraction=0.05)
    
    logger.info(f"Value anomaly model trained: {results}")
    return model


def train_pattern_model(data: pd.DataFrame):
    """Train behavioral pattern model using KNN."""
    logger.info("Training pattern model...")
    
    pattern_features = data[['tx_count_1h', 'unique_counterparties', 'is_contract']].copy()
    
    model = PyCaretAnomalyDetector(model_type="knn")
    results = model.train(pattern_features, fraction=0.05)
    
    logger.info(f"Pattern model trained: {results}")
    return model


async def main():
    """Main training pipeline."""
    logger.info("=" * 60)
    logger.info("ANOMALY DETECTION MODEL TRAINING")
    logger.info("=" * 60)
    
    # Fetch training data
    data = await fetch_training_data(lookback_days=90)
    
    logger.info(f"Training data shape: {data.shape}")
    logger.info(f"Features: {list(data.columns)}")
    
    # Train individual models
    models = {}
    
    try:
        models['velocity'] = train_velocity_model(data)
        models['time'] = train_time_anomaly_model(data)
        models['value'] = train_value_anomaly_model(data)
        models['pattern'] = train_pattern_model(data)
        
        logger.info("=" * 60)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Trained {len(models)} models:")
        for name in models.keys():
            logger.info(f"  - {name}")
        
        logger.info("\nModels saved to: ml-engine/models/pycaret/")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise
    
    return models


if __name__ == "__main__":
    asyncio.run(main())
