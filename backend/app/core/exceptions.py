"""
Custom exceptions for anomaly detection system.
"""
from typing import Optional, Any, Dict


class AnomalyDetectionError(Exception):
    """Base exception for anomaly detection errors."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)


class DetectorError(AnomalyDetectionError):
    """Exception raised by individual detectors."""
    pass


class ConfigurationError(AnomalyDetectionError):
    """Exception for configuration errors."""
    pass


class BigQueryError(AnomalyDetectionError):
    """Exception for BigQuery-related errors."""
    pass


class ModelLoadError(AnomalyDetectionError):
    """Exception for ML model loading errors."""
    pass


class ValidationError(AnomalyDetectionError):
    """Exception for data validation errors."""
    pass


class ClientRegistryError(AnomalyDetectionError):
    """Exception for client registry errors."""
    pass


class TimeoutError(AnomalyDetectionError):
    """Exception for operation timeout."""
    pass
