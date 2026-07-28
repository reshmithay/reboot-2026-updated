import pickle
import numpy as np
from pathlib import Path
from typing import Any

MODEL_PATH = Path(__file__).parent.parent / "models"


class AnomalyPredictor:
    """
    Ensemble predictor combining Isolation Forest and Autoencoder scores.
    Loads models lazily on first prediction call.
    """

    def __init__(self):
        self._if_model = None
        self._scaler = None
        self._ae_model = None

    def _load_models(self):
        if self._if_model is None:
            with open(MODEL_PATH / "isolation_forest.pkl", "rb") as f:
                self._if_model = pickle.load(f)
            with open(MODEL_PATH / "scaler.pkl", "rb") as f:
                self._scaler = pickle.load(f)
        # Autoencoder loaded separately if available
        ae_path = MODEL_PATH / "autoencoder.pt"
        if ae_path.exists() and self._ae_model is None:
            try:
                import torch
                self._ae_model = torch.load(ae_path, map_location="cpu")
                self._ae_model.eval()
            except Exception:
                pass

    def predict(self, features: np.ndarray) -> dict:
        """
        Return anomaly score and contributing signals.
        features: shape (1, n_features)
        """
        self._load_models()
        X = self._scaler.transform(features)

        # Isolation Forest score
        if_raw = self._if_model.decision_function(X)[0]
        if_score = float(1 - (if_raw + 0.5))  # normalize to ~[0, 1]
        if_score = max(0.0, min(1.0, if_score))

        # Autoencoder reconstruction error
        ae_score = 0.0
        if self._ae_model is not None:
            import torch
            tensor = torch.tensor(X, dtype=torch.float32)
            with torch.no_grad():
                recon = self._ae_model(tensor)
                ae_score = float(torch.mean((recon - tensor) ** 2).item())
                ae_score = min(ae_score / 2.0, 1.0)  # normalize

        ensemble = 0.6 * if_score + 0.4 * ae_score

        return {
            "ensemble_score": round(ensemble, 4),
            "isolation_forest_score": round(if_score, 4),
            "autoencoder_score": round(ae_score, 4),
            "is_anomaly": ensemble >= 0.5,
        }
