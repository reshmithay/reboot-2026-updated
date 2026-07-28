"""
Duplicate escrow funding detector using similarity matching and nearest neighbor search.
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

from app.services.anomaly.detectors.base_detector import BaseDetector, AnomalyResult


class DuplicateEscrowDetector(BaseDetector):
    """Detects duplicate or highly similar escrow funding transactions."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.95)
        self.lookback_hours = self.config.get("lookback_hours", 72)
        self.value_tolerance = self.config.get("value_tolerance", 0.01)  # 1%
        self.time_window_minutes = self.config.get("time_window_minutes", 60)
    
    async def detect(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> AnomalyResult:
        """
        Detect duplicate escrow funding using similarity matching.
        """
        # Get recent escrow transactions
        recent_txs = context.get("recent_escrow_transactions", [])
        if not recent_txs:
            recent_txs = await self._fetch_recent_escrow_txs(transaction, context)
        
        # Find similar transactions
        similar_txs = self._find_similar_transactions(transaction, recent_txs)
        
        if similar_txs:
            # Analyze duplicates
            duplicate_info = self._analyze_duplicates(transaction, similar_txs)
            
            confidence = min(0.95, 0.7 + duplicate_info["max_similarity"] * 0.25)
            
            return self._create_result(
                is_anomaly=True,
                confidence=confidence,
                reasons=[
                    f"Found {len(similar_txs)} highly similar escrow transaction(s)",
                    f"Maximum similarity score: {duplicate_info['max_similarity']:.3f}",
                    f"Total duplicate value: ${duplicate_info['total_duplicate_value']:.2f}",
                    f"Shortest time gap: {duplicate_info['min_time_gap_minutes']:.0f} minutes"
                ],
                metadata={
                    "duplicate_count": len(similar_txs),
                    "similar_tx_hashes": [tx.get("tx_hash") for tx in similar_txs],
                    "max_similarity": duplicate_info["max_similarity"],
                    "avg_similarity": duplicate_info["avg_similarity"],
                    "total_duplicate_value": duplicate_info["total_duplicate_value"],
                    "min_time_gap_minutes": duplicate_info["min_time_gap_minutes"]
                }
            )
        
        return self._create_result(
            is_anomaly=False,
            confidence=0.1,
            reasons=["No duplicate escrow funding detected"],
            metadata={}
        )
    
    def _find_similar_transactions(
        self, target_tx: Dict[str, Any], candidates: List[Dict]
    ) -> List[Dict]:
        """Find similar transactions using feature-based similarity."""
        if not candidates:
            return []
        
        # Extract features from target
        target_features = self._extract_features(target_tx)
        
        # Extract features from candidates
        candidate_features = np.array([self._extract_features(tx) for tx in candidates])
        target_features_array = target_features.reshape(1, -1)
        
        # Compute cosine similarity
        similarities = cosine_similarity(target_features_array, candidate_features)[0]
        
        # Also check exact value matches
        target_value = float(target_tx.get("amount", 0))
        
        similar_txs = []
        for i, (tx, sim) in enumerate(zip(candidates, similarities)):
            tx_value = float(tx.get("amount", 0))
            value_diff = abs(tx_value - target_value) / target_value if target_value > 0 else 1
            
            # Check if similar AND within time window
            if sim >= self.similarity_threshold and value_diff <= self.value_tolerance:
                tx_time = datetime.fromisoformat(tx.get("transaction_timestamp", datetime.utcnow().isoformat()))
                target_time = datetime.fromisoformat(target_tx.get("transaction_timestamp", datetime.utcnow().isoformat()))
                time_diff_minutes = abs((tx_time - target_time).total_seconds() / 60)
                
                if time_diff_minutes <= self.time_window_minutes:
                    tx_with_sim = tx.copy()
                    tx_with_sim["_similarity"] = sim
                    tx_with_sim["_time_diff_minutes"] = time_diff_minutes
                    similar_txs.append(tx_with_sim)
        
        return similar_txs
    
    def _extract_features(self, tx: Dict[str, Any]) -> np.ndarray:
        """
        Extract numerical features for similarity comparison.
        Features: [log_value, gas_ratio, is_contract, hour_of_day, from_hash, to_hash]
        """
        value = float(tx.get("amount", 0))
        gas_ratio = float(tx.get("gas_ratio", 0.5))
        is_contract = 1.0 if tx.get("is_contract_interaction", False) else 0.0
        
        # Time features
        tx_time = datetime.fromisoformat(tx.get("transaction_timestamp", datetime.utcnow().isoformat()))
        hour_normalized = tx_time.hour / 24.0
        
        # Address hashing (simple hash for similarity)
        from_addr = tx.get("from_wallet_address", "")
        to_addr = tx.get("to_wallet_address", "")
        from_hash = hash(from_addr) % 1000 / 1000.0
        to_hash = hash(to_addr) % 1000 / 1000.0
        
        features = np.array([
            np.log10(value + 1),
            gas_ratio,
            is_contract,
            hour_normalized,
            from_hash,
            to_hash
        ])
        
        return features
    
    def _analyze_duplicates(self, target_tx: Dict, similar_txs: List[Dict]) -> Dict[str, Any]:
        """Analyze duplicate transaction patterns."""
        similarities = [tx["_similarity"] for tx in similar_txs]
        time_gaps = [tx["_time_diff_minutes"] for tx in similar_txs]
        values = [float(tx.get("amount", 0)) for tx in similar_txs]
        
        return {
            "max_similarity": max(similarities),
            "avg_similarity": np.mean(similarities),
            "min_time_gap_minutes": min(time_gaps),
            "avg_time_gap_minutes": np.mean(time_gaps),
            "total_duplicate_value": sum(values),
            "unique_addresses": len(set(
                tx.get("from_wallet_address") for tx in similar_txs
            ))
        }
    
    async def _fetch_recent_escrow_txs(self, transaction: Dict, context: Dict) -> List[Dict]:
        """Fetch recent escrow-related transactions from BigQuery."""
        # Placeholder - implement with BigQueryClient
        # Filter for escrow contract interactions
        return []
