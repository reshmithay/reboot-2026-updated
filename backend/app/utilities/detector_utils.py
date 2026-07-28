"""
Utilities for detector implementations.
"""
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime, timedelta
from functools import wraps
import asyncio

from app.core.exceptions import DetectorError, TimeoutError as CustomTimeoutError
from app.utilities.logger.logger import get_logger

logger = get_logger(__name__)


def with_timeout(seconds: int):
    """Decorator to add timeout to async detector methods."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                detector_name = args[0].__class__.__name__ if args else "Unknown"
                raise CustomTimeoutError(
                    f"{detector_name} timed out after {seconds}s",
                    details={"timeout_seconds": seconds, "detector": detector_name}
                )
        return wrapper
    return decorator


def with_error_handling(detector_name: str):
    """Decorator to standardize error handling for detectors."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except CustomTimeoutError:
                raise  # Re-raise timeout errors
            except Exception as e:
                logger.error(f"{detector_name} failed: {e}", exc_info=True)
                raise DetectorError(
                    f"{detector_name} execution failed",
                    details={"error_type": type(e).__name__},
                    original_error=e
                )
        return wrapper
    return decorator


def calculate_feature_hash(features: Dict[str, Any]) -> str:
    """Calculate hash of features for similarity detection."""
    # Sort keys for consistent hashing
    sorted_items = sorted(features.items())
    feature_str = str(sorted_items)
    return hashlib.sha256(feature_str.encode()).hexdigest()


def normalize_address(address: str) -> str:
    """Normalize Ethereum address to lowercase with 0x prefix."""
    if not address:
        return ""
    address = address.lower()
    if not address.startswith('0x'):
        address = '0x' + address
    return address


def parse_time_window(window: str) -> tuple[int, int]:
    """
    Parse time window string like '09:00-17:00' to (start_hour, end_hour).
    
    Args:
        window: Time window string
        
    Returns:
        Tuple of (start_hour, end_hour)
        
    Raises:
        ValueError: If window format is invalid
    """
    try:
        start, end = window.split('-')
        start_hour = int(start.split(':')[0])
        end_hour = int(end.split(':')[0])
        
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            raise ValueError("Hours must be between 0 and 23")
        
        return start_hour, end_hour
    except Exception as e:
        raise ValueError(f"Invalid time window format: {window}") from e


def is_within_time_window(
    timestamp: datetime,
    start_hour: int,
    end_hour: int,
    include_weekends: bool = False
) -> bool:
    """
    Check if timestamp is within specified time window.
    
    Args:
        timestamp: Timestamp to check
        start_hour: Start hour (0-23)
        end_hour: End hour (0-23)
        include_weekends: Whether to include weekends
        
    Returns:
        True if within window, False otherwise
    """
    if not include_weekends and timestamp.weekday() >= 5:
        return False
    
    hour = timestamp.hour
    
    if start_hour <= end_hour:
        return start_hour <= hour <= end_hour
    else:
        # Handle overnight windows like 22:00-06:00
        return hour >= start_hour or hour <= end_hour


def calculate_time_difference_minutes(ts1: str, ts2: str) -> float:
    """
    Calculate time difference in minutes between two ISO timestamps.
    
    Args:
        ts1: First timestamp (ISO format)
        ts2: Second timestamp (ISO format)
        
    Returns:
        Difference in minutes
    """
    dt1 = datetime.fromisoformat(ts1.replace('Z', '+00:00'))
    dt2 = datetime.fromisoformat(ts2.replace('Z', '+00:00'))
    return abs((dt2 - dt1).total_seconds() / 60)


def safe_float_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two floats, returning default if denominator is zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def extract_transaction_features(transaction: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract numerical features from transaction for ML models.
    
    Args:
        transaction: Transaction dictionary
        
    Returns:
        Dictionary of numerical features
    """
    import numpy as np
    
    timestamp = datetime.fromisoformat(transaction.get("transaction_timestamp", datetime.utcnow().isoformat()))
    
    return {
        "value_log": np.log10(float(transaction.get("amount", 1)) + 1),
        "gas_ratio": float(transaction.get("gas_ratio", 0.5)),
        "hour": timestamp.hour,
        "hour_sin": np.sin(2 * np.pi * timestamp.hour / 24),
        "hour_cos": np.cos(2 * np.pi * timestamp.hour / 24),
        "day_of_week": timestamp.weekday(),
        "is_weekend": float(timestamp.weekday() >= 5),
        "is_contract": float(transaction.get("is_contract_interaction", False)),
        "from_hash": hash(transaction.get("from_wallet_address", "")) % 1000 / 1000,
        "to_hash": hash(transaction.get("to_wallet_address", "")) % 1000 / 1000
    }


def batch_transactions(
    transactions: List[Dict[str, Any]],
    batch_size: int = 100
) -> List[List[Dict[str, Any]]]:
    """
    Batch transactions into chunks.
    
    Args:
        transactions: List of transactions
        batch_size: Size of each batch
        
    Returns:
        List of transaction batches
    """
    return [
        transactions[i:i + batch_size]
        for i in range(0, len(transactions), batch_size)
    ]


def merge_detection_metadata(
    metadata_list: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Merge metadata from multiple detections.
    
    Args:
        metadata_list: List of metadata dictionaries
        
    Returns:
        Merged metadata dictionary
    """
    merged = {}
    for metadata in metadata_list:
        for key, value in metadata.items():
            if key in merged:
                # Handle lists
                if isinstance(merged[key], list):
                    if isinstance(value, list):
                        merged[key].extend(value)
                    else:
                        merged[key].append(value)
                # Handle numbers (take max)
                elif isinstance(merged[key], (int, float)) and isinstance(value, (int, float)):
                    merged[key] = max(merged[key], value)
                # Handle strings (concatenate with separator)
                elif isinstance(merged[key], str) and isinstance(value, str):
                    merged[key] = f"{merged[key]}; {value}"
            else:
                merged[key] = value
    return merged


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int, time_window_seconds: int):
        self.max_calls = max_calls
        self.time_window = time_window_seconds
        self.calls: List[datetime] = []
    
    async def acquire(self):
        """Acquire rate limit token, waiting if necessary."""
        now = datetime.utcnow()
        # Remove old calls outside time window
        self.calls = [
            call_time for call_time in self.calls
            if (now - call_time).total_seconds() < self.time_window
        ]
        
        if len(self.calls) >= self.max_calls:
            # Wait until oldest call expires
            wait_time = self.time_window - (now - self.calls[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                return await self.acquire()
        
        self.calls.append(now)


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise DetectorError("Circuit breaker is OPEN", details={"state": self.state})
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return (datetime.utcnow() - self.last_failure_time).total_seconds() >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
