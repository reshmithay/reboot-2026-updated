"""
Example usage of the anomaly detection orchestrator.
"""
import asyncio
from app.services.anomaly.orchestrator import AnomalyOrchestrator


async def example_detection():
    """Example: Detect anomalies in a sample transaction."""
    
    # Initialize orchestrator
    orchestrator = AnomalyOrchestrator()
    
    # Sample transaction
    transaction = {
        "tx_hash": "0xabc123def456...",
        "from_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "to_address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "value": 9500.0,  # Just below $10k threshold
        "timestamp": "2026-07-21T23:30:00Z",  # Late night
        "gas_ratio": 0.85,
        "is_contract_interaction": False,
        "token_symbol": "USDC"
    }
    
    # Run detection
    result = await orchestrator.detect_all(transaction)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"ANOMALY DETECTION REPORT")
    print(f"{'='*60}")
    print(f"Transaction: {result['transaction_id']}")
    print(f"Is Anomaly: {result['is_anomaly']}")
    print(f"Overall Score: {result['overall_score']:.2f}")
    print(f"Severity: {result['overall_severity']}")
    print(f"Anomalies Detected: {result['anomaly_count']}")
    print(f"\nDetections:")
    for detection in result['detections']:
        print(f"  - {detection['detector']}: {detection['confidence']:.2f} ({detection['severity']})")
        for reason in detection['reasons']:
            print(f"      • {reason}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(example_detection())
