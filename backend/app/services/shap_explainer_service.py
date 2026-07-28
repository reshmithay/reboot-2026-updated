import logging
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ShapExplainerService:
    """Service for computing SHAP values for anomaly explanations."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize SHAP explainer with the anomaly detection model."""
        self.model = None
        self.explainer = None
        self.feature_names = None
        
        # Try to load the model if path provided
        if model_path:
            self._load_model(model_path)

    def _load_model(self, model_path: str):
        """Load the trained anomaly detection model."""
        try:
            model_file = Path(model_path)
            if model_file.exists():
                with open(model_file, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded model from {model_path}")
                
                # Initialize SHAP explainer
                try:
                    import shap
                    self.explainer = shap.TreeExplainer(self.model)
                    logger.info("SHAP explainer initialized")
                except ImportError:
                    logger.warning("SHAP library not available, will use fallback method")
                except Exception as e:
                    logger.warning(f"Failed to initialize SHAP explainer: {e}")
            else:
                logger.warning(f"Model file not found: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def compute_shap_values(
        self,
        transaction_features: Dict[str, Any],
        anomaly_score: float,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Compute SHAP values for transaction features.
        
        Args:
            transaction_features: Dictionary of feature values
            anomaly_score: The anomaly score from detection
            top_k: Number of top contributors to return
            
        Returns:
            List of SHAP contributors sorted by absolute impact
        """
        # If SHAP is not available or model not loaded, use rule-based approximation
        if not self.explainer or not self.model:
            return self._approximate_shap_values(transaction_features, anomaly_score, top_k)
        
        try:
            # Prepare features in correct order
            feature_names = self._get_feature_names(transaction_features)
            feature_values = [transaction_features.get(name, 0) for name in feature_names]
            
            # Compute SHAP values
            shap_values = self.explainer.shap_values(np.array([feature_values]))
            base_value = self.explainer.expected_value
            
            # Create contributors list
            contributors = []
            for i, (name, value, shap_val) in enumerate(zip(feature_names, feature_values, shap_values[0])):
                contributors.append({
                    "feature": self._format_feature_name(name),
                    "actual_value": float(value),
                    "shap_contribution": round(float(shap_val), 4),
                    "direction": "increased" if shap_val > 0 else "decreased",
                })
            
            # Sort by absolute impact and return top k
            contributors.sort(key=lambda x: abs(x["shap_contribution"]), reverse=True)
            return contributors[:top_k]
            
        except Exception as e:
            logger.error(f"SHAP computation failed: {e}, using approximation")
            return self._approximate_shap_values(transaction_features, anomaly_score, top_k)

    def _approximate_shap_values(
        self,
        transaction_features: Dict[str, Any],
        anomaly_score: float,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Approximate SHAP values using rule-based heuristics when SHAP is unavailable.
        This provides a reasonable explanation based on feature values and anomaly reasons.
        """
        contributors = []
        
        # Map transaction features to impact scores based on business rules
        feature_impacts = {
            "amount": self._calculate_amount_impact(transaction_features),
            "transaction_hour": self._calculate_time_impact(transaction_features),
            "transaction_type": self._calculate_type_impact(transaction_features),
            "daily_transaction_count": self._calculate_frequency_impact(transaction_features),
            "account_balance": self._calculate_balance_impact(transaction_features),
            "withdrawal_percentage": self._calculate_withdrawal_impact(transaction_features),
            "time_since_last_transaction": self._calculate_velocity_impact(transaction_features),
        }
        
        # Convert to SHAP-like format
        for feature, impact in feature_impacts.items():
            if feature in transaction_features:
                contributors.append({
                    "feature": self._format_feature_name(feature),
                    "actual_value": float(transaction_features.get(feature, 0)),
                    "shap_contribution": round(impact * anomaly_score, 4),
                    "direction": "increased" if impact > 0 else "decreased",
                })
        
        # Sort by absolute impact
        contributors.sort(key=lambda x: abs(x["shap_contribution"]), reverse=True)
        return contributors[:top_k]

    def _calculate_amount_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of transaction amount."""
        amount = features.get("amount", 0)
        # Large amounts contribute more to risk
        if amount > 100000:
            return 0.3
        elif amount > 50000:
            return 0.2
        elif amount > 10000:
            return 0.1
        return 0.0

    def _calculate_time_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of transaction time."""
        hour = features.get("transaction_hour", 12)
        # Off-hours (night time) contribute to risk
        if hour < 6 or hour > 22:
            return 0.25
        elif hour < 9 or hour > 17:
            return 0.1
        return -0.05  # Normal hours reduce risk

    def _calculate_type_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of transaction type."""
        tx_type = features.get("transaction_type", 0)
        # tx_type is encoded: 0=DEPOSIT, 1=TRANSFER, 2=WITHDRAWAL
        if isinstance(tx_type, str):
            # Fallback for string type (backward compatibility)
            tx_type = tx_type.lower()
            if "withdrawal" in tx_type:
                return 0.15
            elif "transfer" in tx_type:
                return 0.1
            return 0.0
        else:
            # Numeric encoding
            if tx_type == 2:  # WITHDRAWAL
                return 0.15
            elif tx_type == 1:  # TRANSFER
                return 0.1
            return 0.0  # DEPOSIT or unknown

    def _calculate_frequency_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of transaction frequency."""
        count = features.get("daily_transaction_count", 0)
        # High frequency can indicate suspicious activity
        if count > 20:
            return 0.2
        elif count > 10:
            return 0.1
        return 0.0

    def _calculate_balance_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of account balance."""
        balance = features.get("account_balance", 0)
        amount = features.get("amount", 0)
        # Low balance after transaction is risky
        if balance < 1000:
            return 0.15
        elif amount > balance * 0.5:
            return 0.1
        return -0.05

    def _calculate_withdrawal_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of withdrawal percentage."""
        pct = features.get("withdrawal_percentage", 0)
        # High withdrawal percentage is risky
        if pct > 90:
            return 0.35
        elif pct > 70:
            return 0.2
        elif pct > 50:
            return 0.1
        return 0.0

    def _calculate_velocity_impact(self, features: Dict[str, Any]) -> float:
        """Calculate impact of transaction velocity."""
        time_gap = features.get("time_since_last_transaction", 999999)
        # Very short time gaps indicate velocity risk
        if time_gap < 60:  # Less than 1 minute
            return 0.2
        elif time_gap < 300:  # Less than 5 minutes
            return 0.1
        return 0.0

    def _get_feature_names(self, features: Dict[str, Any]) -> List[str]:
        """Get consistent feature names in model order."""
        # Standard feature order (should match model training)
        return [
            "amount",
            "transaction_hour",
            "daily_transaction_count",
            "account_balance",
            "withdrawal_percentage",
            "time_since_last_transaction",
        ]

    def _format_feature_name(self, feature: str) -> str:
        """Format feature name for display."""
        name_mapping = {
            "amount": "Transaction Amount",
            "transaction_hour": "Transaction Time (Hour)",
            "daily_transaction_count": "Daily Transaction Count",
            "account_balance": "Account Balance",
            "withdrawal_percentage": "Withdrawal Percentage",
            "time_since_last_transaction": "Time Since Last Transaction",
            "transaction_type": "Transaction Type",
        }
        return name_mapping.get(feature, feature.replace("_", " ").title())
