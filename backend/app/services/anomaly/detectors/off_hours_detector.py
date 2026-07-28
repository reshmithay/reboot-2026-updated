"""
Off-hours full-balance withdrawal detector.
Combines rule-based (time window) + ML (Isolation Forest for behavior).
Uses client-specific activity windows from client_registry when available.
"""
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, time
import pickle
from pathlib import Path

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class OffHoursWithdrawalDetector(BaseDetector):
    """Detects full-balance withdrawals during off-hours."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Default business hours (fallback)
        self.default_hours_start = time(9, 0)  # 9 AM
        self.default_hours_end = time(17, 0)   # 5 PM
        self.full_balance_threshold = self.config.get("full_balance_threshold", 0.90)  # 90%
        self.model_path = Path(self.config.get("model_path", "ml-engine/models/time_anomaly.pkl"))
        self._model = None
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Detect off-hours + full-balance withdrawal pattern.
        Uses client-specific expected_activity_window from client_registry if available.
        """
        tx_time = datetime.fromisoformat(transaction.get("transaction_timestamp", datetime.utcnow().isoformat()))
        tx_value = float(transaction.get("amount", 0))
        from_address = transaction.get("from_wallet_address")
        client_id = transaction.get("client_id")
        
        # Get client-specific activity window or use default
        activity_window = self._get_activity_window(context, client_id)
        hours_start, hours_end, window_source = activity_window
        
        # Rule 1: Check if off-hours (using client-specific or default window)
        is_off_hours, off_hours_reason = self._is_off_hours(tx_time, hours_start, hours_end)
        
        # Rule 2: Check if full/near-full balance withdrawal
        account_balance = context.get("account_balance", {}).get(from_address, tx_value)
        withdrawal_ratio = tx_value / account_balance if account_balance > 0 else 0
        is_full_withdrawal = withdrawal_ratio >= self.full_balance_threshold
        
        # ML: Time-based anomaly score
        time_anomaly_score = await self._get_time_anomaly_score(tx_time, from_address, context)
        
        # Combined detection
        if is_off_hours and is_full_withdrawal:
            confidence = 0.85 + (time_anomaly_score * 0.15)
            reasons = [
                f"Transaction at {tx_time.strftime('%H:%M')} ({off_hours_reason})",
                f"Expected activity window: {hours_start.strftime('%H:%M')}-{hours_end.strftime('%H:%M')} ({window_source})",
                f"Withdrawal of {withdrawal_ratio*100:.1f}% of account balance",
                f"Time anomaly score: {time_anomaly_score:.2f}"
            ]
            return self._create_result(
                is_anomaly=True,
                confidence=min(confidence, 1.0),
                anomaly_code="OFF_HOURS_ACTIVITY",
                reasons=reasons,
                metadata={
                    "transaction_hour": tx_time.hour,
                    "withdrawal_ratio": withdrawal_ratio,
                    "account_balance": account_balance,
                    "time_anomaly_score": time_anomaly_score,
                    "is_weekend": tx_time.weekday() >= 5,
                    "expected_window_start": hours_start.strftime('%H:%M'),
                    "expected_window_end": hours_end.strftime('%H:%M'),
                    "window_source": window_source
                }
            )
        elif is_off_hours or (is_full_withdrawal and time_anomaly_score > 0.7):
            confidence = 0.5 + (time_anomaly_score * 0.3)
            return self._create_result(
                is_anomaly=True,
                confidence=confidence,
                anomaly_code="OFF_HOURS_ACTIVITY",
                reasons=[
                    "Suspicious timing or withdrawal pattern",
                    f"Off-hours: {is_off_hours}, Full withdrawal: {is_full_withdrawal}",
                    f"Expected window: {hours_start.strftime('%H:%M')}-{hours_end.strftime('%H:%M')} ({window_source})"
                ],
                metadata={
                    "transaction_hour": tx_time.hour,
                    "withdrawal_ratio": withdrawal_ratio,
                    "time_anomaly_score": time_anomaly_score,
                    "window_source": window_source
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=[f"Transaction within expected activity window ({window_source})"],
            metadata={"window_source": window_source}
        )
    
    def _get_activity_window(self, context: Dict[str, Any], client_id: Optional[str]) -> Tuple[time, time, str]:
        """
        Get client-specific activity window from context or use default.
        
        Returns:
            Tuple of (start_time, end_time, source_description)
        """
        # Try to get client-specific window from client_registry
        client_registry_data = context.get("client_registry", {})
        
        # Handle both dictionary formats:
        # 1. Old format: {"clientId": "...", "expectedActivityWindow": "..."}
        # 2. New format: {client_id: {"clientId": "...", "expectedActivityWindow": "..."}}
        client_info = {}
        
        if isinstance(client_registry_data, dict):
            if client_id and client_id in client_registry_data:
                # New format with nested dictionary
                client_info = client_registry_data[client_id]
            elif "clientId" in client_registry_data:
                # Old flat format
                client_info = client_registry_data
            elif client_id:
                # Try to find by any key in the dictionary
                for key, value in client_registry_data.items():
                    if isinstance(value, dict) and value.get("clientId") == client_id:
                        client_info = value
                        break
        
        expected_window = client_info.get("expectedActivityWindow")
        
        if expected_window:
            parsed_window = self._parse_activity_window(expected_window)
            if parsed_window:
                return (*parsed_window, "client-specific")
        
        # Fallback to default business hours
        return (self.default_hours_start, self.default_hours_end, "default")
    
    def _parse_activity_window(self, window_str: str) -> Optional[Tuple[time, time]]:
        """
        Parse activity window string in format "HH:MM-HH:MM" or "HH:MM - HH:MM".
        
        Examples:
            "08:00-20:00" → (time(8, 0), time(20, 0))
            "09:30 - 18:30" → (time(9, 30), time(18, 30))
        
        Returns:
            Tuple of (start_time, end_time) or None if invalid format
        """
        try:
            # Remove spaces and split by dash
            parts = window_str.replace(" ", "").split("-")
            if len(parts) != 2:
                return None
            
            # Parse start and end times
            start_parts = parts[0].split(":")
            end_parts = parts[1].split(":")
            
            if len(start_parts) != 2 or len(end_parts) != 2:
                return None
            
            start_time = time(int(start_parts[0]), int(start_parts[1]))
            end_time = time(int(end_parts[0]), int(end_parts[1]))
            
            return (start_time, end_time)
        except (ValueError, IndexError):
            return None
    
    def _is_off_hours(self, tx_time: datetime, hours_start: time, hours_end: time) -> Tuple[bool, str]:
        """
        Check if transaction is outside expected activity hours.
        
        Returns:
            Tuple of (is_off_hours, reason_description)
        """
        tx_time_only = tx_time.time()
        is_weekend = tx_time.weekday() >= 5
        
        if is_weekend:
            return (True, "weekend transaction")
        
        is_outside_window = not (hours_start <= tx_time_only <= hours_end)
        if is_outside_window:
            if tx_time_only < hours_start:
                return (True, f"before activity window starts at {hours_start.strftime('%H:%M')}")
            else:
                return (True, f"after activity window ends at {hours_end.strftime('%H:%M')}")
        
        return (False, "within activity window")
    
    async def _get_time_anomaly_score(self, tx_time: datetime, address: str, context: Dict) -> float:
        """Use Isolation Forest to score time-based anomaly."""
        if self._model is None:
            self._load_model()
        
        # Extract temporal features
        features = np.array([[
            tx_time.hour,
            tx_time.minute / 60.0,
            tx_time.weekday(),
            1 if tx_time.weekday() >= 5 else 0,  # is_weekend
            tx_time.day,
        ]])
        
        if self._model is None:
            # Fallback: simple heuristic
            if tx_time.hour < 6 or tx_time.hour > 22:
                return 0.9
            elif tx_time.weekday() >= 5:
                return 0.7
            return 0.3
        
        # Use model
        try:
            raw_score = self._model.decision_function(features)[0]
            # Normalize to 0-1
            normalized = 1 - (raw_score + 0.5)
            return max(0.0, min(1.0, normalized))
        except Exception:
            return 0.5
    
    def _load_model(self):
        """Load Isolation Forest model for time anomalies."""
        try:
            if self.model_path.exists():
                with open(self.model_path, "rb") as f:
                    self._model = pickle.load(f)
        except Exception:
            self._model = None
