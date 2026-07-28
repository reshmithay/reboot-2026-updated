---
name: solidity-blockchain
description: "Use when working on Solidity smart contracts, Hardhat scripts, deployment, or blockchain integration in blockchain/ or backend/clients/blockchain/"
user-invocable: true
---

# Solidity & Blockchain Development Skill

You are an expert in Solidity, Hardhat, and Web3 integration for on-chain anomaly audit trails.

## Project Context

- **Blockchain**: Polygon (MATIC) — EVM-compatible, low gas fees
- **Solidity Version**: 0.8.20
- **Framework**: Hardhat
- **Web3 Library**: Ethers.js v6 (backend), web3.py (alternative)
- **Network**: Polygon mainnet (137) / Mumbai testnet (80001)

## Smart Contracts

### 1. AnomalyRegistry.sol
**Purpose**: Immutable registry of detected anomalies

```solidity
struct AnomalyRecord {
    string anomalyId;
    bytes32 txHash;
    uint8 score;        // 0-100
    uint8 severity;     // 0=low, 1=medium, 2=high, 3=critical
    uint256 timestamp;
    address reportedBy;
}

function recordAnomaly(
    string calldata anomalyId,
    bytes32 txHash,
    uint8 score,
    uint8 severity
) external onlyOwner;
```

### 2. AuditTrail.sol
**Purpose**: Append-only log of all system events

```solidity
struct AuditEntry {
    uint256 id;
    string transactionId;
    string eventType;    // "ANOMALY_DETECTED", "STATUS_CHANGED", etc.
    string metadata;
    address author;
    uint256 timestamp;
}

function logEvent(
    string calldata transactionId,
    string calldata eventType,
    string calldata metadata
) external onlyOwner returns (uint256);
```

### 3. RiskScoreRegistry.sol
**Purpose**: Live wallet risk scores

```solidity
struct RiskEntry {
    address wallet;
    uint8 score;        // 0-100
    uint256 updatedAt;
    uint256 txCount;
    bool flagged;       // auto-flagged if score >= 75
}

function updateScore(address wallet, uint8 score) external onlyOwner;
function isFlagged(address wallet) external view returns (bool);
```

## Directory Structure

```
blockchain/
├── contracts/              # Solidity source
│   ├── AnomalyRegistry.sol
│   ├── AuditTrail.sol
│   └── RiskScoreRegistry.sol
├── scripts/
│   ├── deploy.js          # Deployment script
│   └── verify.js          # Contract verification
├── test/                  # Hardhat tests
├── artifacts/             # Compiled ABIs (gitignored)
├── cache/                 # Hardhat cache
└── hardhat.config.js      # Network config
```

## Code Patterns

### Contract Pattern
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MyContract {
    address public owner;
    
    event SomethingHappened(address indexed user, uint256 value);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "MyContract: not owner");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    function doSomething(uint256 value) external onlyOwner {
        // logic
        emit SomethingHappened(msg.sender, value);
    }
}
```

### Deployment Script
```javascript
// scripts/deploy.js
const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const Contract = await ethers.getContractFactory("AnomalyRegistry");
  const contract = await Contract.deploy();
  await contract.waitForDeployment();
  
  console.log("Deployed to:", await contract.getAddress());
}
```

### Web3 Integration (Backend)
```python
# backend/app/clients/blockchain/web3_client.py
from web3 import Web3
from app.config.settings import settings

class Web3Client:
    def __init__(self):
        self._w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
    
    @property
    def w3(self) -> Web3:
        if not self._w3.is_connected():
            raise ConnectionError("Cannot connect to RPC")
        return self._w3
```

```python
# backend/app/clients/blockchain/contract_client.py
import json

class ContractClient:
    def __init__(self, web3_client):
        self.web3 = web3_client
        abi = self._load_abi("AnomalyRegistry")
        self.contract = self.web3.w3.eth.contract(
            address=settings.ANOMALY_REGISTRY_ADDRESS,
            abi=abi,
        )
    
    async def record_anomaly(self, anomaly_id, score, tx_hash):
        account = self.web3.get_account()
        tx = self.contract.functions.recordAnomaly(
            anomaly_id,
            bytes.fromhex(tx_hash[2:]),
            int(score),
            self._classify_severity(score),
        ).build_transaction({
            "from": account.address,
            "nonce": self.web3.w3.eth.get_transaction_count(account.address),
        })
        signed = account.sign_transaction(tx)
        tx_hash = self.web3.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.web3.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
```

## Operating Rules

1. **Gas Efficiency**: Minimize storage writes, use events for logging
2. **Immutability**: Once written, audit entries should never be deleted
3. **Access Control**: Use `onlyOwner` or role-based modifiers
4. **Event Emission**: Emit events for all state changes (indexing, monitoring)
5. **Input Validation**: Always validate bounds (scores, addresses, lengths)
6. **Reentrancy Safety**: Use checks-effects-interactions pattern
7. **Upgradeability**: These contracts are NOT upgradeable (immutability by design)

## Common Tasks

### Deploy Contracts
```bash
# Compile
npx hardhat compile

# Deploy to local
npx hardhat run scripts/deploy.js --network localhost

# Deploy to Mumbai testnet
npx hardhat run scripts/deploy.js --network mumbai

# Verify on Polygonscan
npx hardhat verify --network mumbai <ADDRESS>
```

### Test Contracts
```bash
npx hardhat test
npx hardhat test --grep "AnomalyRegistry"
```

### Interact with Deployed Contract
```bash
npx hardhat console --network mumbai
> const Contract = await ethers.getContractAt("AnomalyRegistry", "0x...");
> await Contract.getTotalAnomalies();
```

### Update Backend with New Contract Address
After deployment:
1. Copy addresses from `blockchain/artifacts/deployed_addresses.json`
2. Update `.env`:
   ```
   ANOMALY_REGISTRY_ADDRESS=0x...
   AUDIT_TRAIL_ADDRESS=0x...
   RISK_SCORE_REGISTRY_ADDRESS=0x...
   ```

### Add New Contract Function
1. Add function to `.sol` file
2. Recompile: `npx hardhat compile`
3. Update ABI in backend client (auto-loaded from `artifacts/`)
4. Add Python wrapper method in `contract_client.py`

## Gas Optimization Patterns

```solidity
// ✅ Good: Pack structs efficiently
struct Entry {
    uint8 score;      // 1 byte
    uint8 severity;   // 1 byte
    uint240 value;    // 30 bytes → fits in 1 slot (32 bytes)
}

// ✅ Good: Use events instead of storage for logs
emit AuditLogged(txId, eventType);  // cheap
// vs storing in array (expensive)

// ✅ Good: Batch operations
function recordMultiple(string[] calldata ids) external;

// ❌ Bad: Multiple external calls
for (uint i; i < ids.length; i++) {
    recordSingle(ids[i]);  // expensive
}
```

## Security Patterns

```solidity
// ✅ Checks-Effects-Interactions
function withdraw() external {
    uint256 amount = balances[msg.sender];
    require(amount > 0, "No balance");
    
    balances[msg.sender] = 0;  // effect BEFORE interaction
    payable(msg.sender).transfer(amount);  // interaction last
}

// ✅ Input validation
require(score <= 100, "Score out of range");
require(wallet != address(0), "Invalid address");

// ✅ Owner-only critical functions
modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}
```

## Anti-patterns

- ❌ Don't use `tx.origin` — use `msg.sender`
- ❌ Don't use `transfer()` for ETH — use `call{value: ...}()`
- ❌ Don't store large strings on-chain — use IPFS hash
- ❌ Don't delete from arrays — mark as inactive instead
- ❌ Don't use floating point — use fixed-point or basis points

## Validation

After changes:
1. Compile: `npx hardhat compile` (no errors)
2. Test: `npx hardhat test` (all passing)
3. Gas report: `REPORT_GAS=true npx hardhat test`
4. Deploy to testnet and verify function calls
5. Update backend client and test integration
