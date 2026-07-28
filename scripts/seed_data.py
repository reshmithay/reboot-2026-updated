"""
Seed script — generates synthetic transaction data for development and ML training.
Run: python scripts/seed_data.py
"""
import random
import json
import uuid
from datetime import datetime, timedelta


def generate_address() -> str:
    return "0x" + "".join(random.choices("0123456789abcdef", k=40))


def generate_tx_hash() -> str:
    return "0x" + "".join(random.choices("0123456789abcdef", k=64))


def generate_transaction(is_anomalous: bool = False) -> dict:
    base_value = random.uniform(0.001, 1000)
    if is_anomalous:
        # Anomalous patterns: large transfers, many counterparties, unusual timing
        base_value = random.uniform(100000, 5000000)

    return {
        "id": str(uuid.uuid4()),
        "tx_hash": generate_tx_hash(),
        "from_address": generate_address(),
        "to_address": generate_address(),
        "value": round(base_value, 6),
        "token_symbol": random.choice(["ETH", "USDC", "USDT", "WBTC", "MATIC"]),
        "chain_id": 137,
        "block_number": random.randint(50000000, 60000000),
        "timestamp": (
            datetime.utcnow() - timedelta(seconds=random.randint(0, 86400 * 30))
        ).isoformat() + "Z",
        "is_fraud": int(is_anomalous),
        "tx_count_1h": random.randint(1, 200) if is_anomalous else random.randint(1, 10),
        "unique_counterparties": random.randint(10, 100) if is_anomalous else random.randint(1, 5),
        "gas_ratio": round(random.uniform(0.3, 1.0), 3),
        "is_contract": random.choice([0, 1]),
        "time_since_last_tx": random.uniform(1, 60) if is_anomalous else random.uniform(300, 86400),
    }


def main(n_normal: int = 1000, n_anomalous: int = 50, output: str = "ml-engine/datasets/transactions.csv"):
    import csv
    import os

    os.makedirs(os.path.dirname(output), exist_ok=True)

    transactions = (
        [generate_transaction(False) for _ in range(n_normal)]
        + [generate_transaction(True) for _ in range(n_anomalous)]
    )
    random.shuffle(transactions)

    if transactions:
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)

    print(f"Generated {n_normal + n_anomalous} transactions → {output}")
    print(f"  Normal: {n_normal}, Anomalous: {n_anomalous}")


if __name__ == "__main__":
    main()
