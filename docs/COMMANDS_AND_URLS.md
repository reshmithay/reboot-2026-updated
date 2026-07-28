# 🚀 Useful Commands & URLs - Blockchain Anomaly AI

## � Table of Contents

1. [Application URLs](#-application-urls) - All service endpoints and dashboards
2. [Development Commands](#-development-commands) - Setup and running services
3. [Docker Commands](#-docker-commands) - Container management
4. [Database Commands](#-database-commands) - PostgreSQL operations
5. [Testing Commands](#-testing-commands) - Running tests
6. [Blockchain Commands](#-blockchain-commands) - Smart contracts & EOS Jungle Testnet
7. [ML Model Training](#-ml-model-training) - Machine learning operations
8. [Data Management](#-data-management) - Seeding and sample data
9. [Maintenance Commands](#-maintenance-commands) - Cleanup and linting
10. [Health Check & Debugging](#-health-check--debugging) - Troubleshooting
11. [API Testing](#-api-testing-with-curl) - cURL examples
12. [Package Management](#-package-management) - Dependencies
13. [Environment Variables](#-environment-variables) - Configuration
14. [Quick Start Workflows](#-quick-start-workflows) - Getting started guides
15. [SHAP + Cortex AI](#-shap--cortex-ai-narrative-generation) - AI narrative generation
16. [Documentation](#-documentation-files) - Available docs
17. [Useful Links](#-useful-links) - External resources

---
## 🎯 **Quick Reference - Key URLs**

| Service | URL | Purpose |
|---------|-----|---------|
| **Main Frontend** | http://localhost:5173 | React app (Vite dev) |
| **Main Backend** | http://localhost:8000 | FastAPI server |
| **Backend Docs** | http://localhost:8000/docs | Swagger UI |
| **Jungle API** | http://localhost:3000/api | EOS Jungle testnet API |
| **PostgreSQL** | localhost:5432 | Database |
| **Jungle Monitor** | https://monitor.jungletestnet.io/ | EOS account & faucet |
| **Jungle Explorer** | https://jungle4.eosq.eosnation.io/ | Block explorer |

---
## �📍 **Application URLs**

### **Core Services**
```
Backend API:          http://localhost:8000
Backend Docs:         http://localhost:8000/docs          # Swagger UI
Backend ReDoc:        http://localhost:8000/redoc         # Alternative docs
Backend Health:       http://localhost:8000/health

Frontend App:         http://localhost:5173               # Vite dev server
Frontend Prod:        http://localhost:3000               # Docker/nginx

LLM Narrative (deprecated): http://localhost:8001         # No longer needed
```

### **Database**
```
PostgreSQL:           localhost:5432
  - Database:         anomaly_db
  - User:             postgres
  - Password:         postgres
```

### **Key API Endpoints**

#### **Anomalies**
```bash
GET    /api/v1/anomalies                    # List anomalies
GET    /api/v1/anomalies/{id}               # Get anomaly details
GET    /api/v1/anomalies/shap/{anomaly_id}  # Get SHAP features
POST   /api/v1/anomalies/narrative/generate # Generate AI narrative
```

#### **Transactions**
```bash
GET    /api/v1/transactions                 # List transactions
GET    /api/v1/transactions/{hash}          # Get transaction by hash
```

#### **Blockchain**
```bash
GET    /api/v1/blockchain/contracts         # Contract addresses
POST   /api/v1/blockchain/register-anomaly  # Register on-chain
```

#### **Narratives (Legacy)**
```bash
POST   /api/v1/narratives/generate          # Generate narrative
GET    /api/v1/narratives/{anomaly_id}      # Get saved narrative
```

---

## 🔧 **Development Commands**

### **Setup & Installation**
```powershell
# Complete project setup (Windows PowerShell)
npm run bootstrap

# Individual service installs
npm run install:backend          # Install Python backend deps
npm run install:frontend         # Install React/Vite frontend deps
npm run install:blockchain       # Install Hardhat blockchain deps

# Alternative: Use Makefile (if supported)
make bootstrap
```

### **Running Services (Development)**

#### **All Services at Once**
```powershell
npm run dev                      # Runs backend + frontend concurrently
```

#### **Individual Services**
```powershell
# Backend (FastAPI on port 8000)
npm run backend
# OR
cd backend; uvicorn app.main:app --reload --port 8000
# OR
make backend

# Frontend (Vite on port 5173)
npm run frontend
# OR
cd frontend; npm run dev
# OR
make frontend

# LLM Server (DEPRECATED - no longer needed)
# npm run llm-server
```

### **Backend Specific**
```powershell
cd backend

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run with specific host (for network access)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Install dependencies
pip install -r requirements.txt

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### **Frontend Specific**
```powershell
cd frontend

# Development server with hot reload
npm run dev

# Type checking (no compilation)
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview

# Lint TypeScript/React code
npm run lint
```

---

## 🐳 **Docker Commands**

### **Full Stack**
```powershell
# Start all services (backend, frontend, postgres, redis, monitoring)
docker-compose up -d --build

# Stop all services
docker-compose down

# View logs (follow mode)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Restart a specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend
```

### **Container Management**
```powershell
# List running containers
docker ps

# Exec into backend container
docker exec -it blockchain-anomaly-ai-backend-1 bash

# Exec into postgres container
docker exec -it blockchain-anomaly-ai-postgres-1 psql -U postgres -d anomaly_db

# View container logs
docker logs -f <container_id>

# Remove all stopped containers
docker container prune
```

---

## 🗄️ **Database Commands**

### **PostgreSQL Access**
```powershell
# Connect to local PostgreSQL
psql -h localhost -U postgres -d anomaly_db

# From Docker container
docker exec -it blockchain-anomaly-ai-postgres-1 psql -U postgres -d anomaly_db
```

### **SQL Commands**
```sql
-- List all tables
\dt

-- Describe table structure
\d transactions
\d anomaly_results
\d client_registry

-- View recent anomalies
SELECT * FROM anomaly_results ORDER BY detected_at DESC LIMIT 10;

-- View transactions with high anomaly scores
SELECT t.*, a.anomaly_score 
FROM transactions t
JOIN anomaly_results a ON t.transaction_hash = a.transaction_hash
WHERE a.anomaly_score > 0.7
ORDER BY a.anomaly_score DESC;

-- Count anomalies by category
SELECT anomaly_category, COUNT(*) 
FROM anomaly_results 
GROUP BY anomaly_category;
```

### **Database Setup/Reset**
```powershell
cd backend

# Initialize database schema
python init_db.py

# Run schema setup
python sql/run_schema.py
```

---

## 🧪 **Testing Commands**

### **Backend Tests**
```powershell
cd backend

# Run all tests with coverage
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/test_detectors.py -v

# Run with verbose output
pytest -vv

# Run standalone tests
python test_pg_connection.py
python test_anomaly_storage.py
python test_csv_detection.py
python test_detection_standalone.py

# Using Make
make test-backend
```

### **Blockchain Tests**
```powershell
cd blockchain

# Run Hardhat tests
npx hardhat test

# Using npm
npm run test

# Using Make
make blockchain-test
```

---

## ⛓️ **Blockchain Commands**

### **Polygon/Hardhat (Smart Contracts)**

#### **Compile & Deploy**
```powershell
cd blockchain

# Compile smart contracts
npx hardhat compile
# OR
make blockchain-compile

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost
# OR
make blockchain-deploy-local

# Deploy to testnet (Mumbai/Polygon)
npx hardhat run scripts/deploy.js --network mumbai
# OR
make blockchain-deploy-testnet

# Start local Hardhat node
npx hardhat node
```

#### **Contract Interaction**
```powershell
# Hardhat console
npx hardhat console --network localhost

# Verify contract on Etherscan
npx hardhat verify --network mumbai <CONTRACT_ADDRESS>
```

### **EOS Jungle Testnet (Optional Alternative)**

#### **Setup & Configuration**
```powershell
cd ../jungletestnet

# Install dependencies
npm install

# Generate EOS key pair
npm run generate-keys

# Configure environment (copy and edit)
Copy-Item .env.example .env
notepad .env

# Run diagnostics (verify setup)
npm run diagnose
```

#### **Jungle Testnet Endpoints**
```
RPC Endpoint:       https://jungle4.greymass.com
Chain ID:           
Block Explorer:     https://jungle4.eosq.eosnation.io/
Network Monitor:    https://monitor.jungletestnet.io/
Faucet (Get Tokens): https://monitor.jungletestnet.io/
Account Creator:    https://jungletestnet.io/
```

#### **Account & Transaction Management**
```powershell
# Create test accounts on Jungle4
npm run create-accounts

# Generate transactions
npm run run-transactions

# Detect anomalies
npm run detect-anomalies

# Full workflow (accounts → transactions → detection)
npm run workflow

# View statistics
npm run stats
```

#### **REST API Server (Jungle Testnet)**
```powershell
# Start API server on port 3000
npm run server

# Development mode with auto-reload
npm run dev

# API Base URL
http://localhost:3000/api
```

#### **Jungle Testnet API Endpoints**
```bash
# Account Management
POST   http://localhost:3000/api/accounts/batch           # Create multiple accounts
POST   http://localhost:3000/api/accounts/single          # Create single account
GET    http://localhost:3000/api/accounts                 # List all accounts

# Transaction Operations
POST   http://localhost:3000/api/transactions/mixed       # Generate mixed pattern transactions
POST   http://localhost:3000/api/transactions/pattern     # Generate specific pattern
GET    http://localhost:3000/api/transactions             # List transactions

# Anomaly Detection
POST   http://localhost:3000/api/anomalies/detect         # Run anomaly detection
GET    http://localhost:3000/api/anomalies                # List detected anomalies

# Statistics
GET    http://localhost:3000/api/stats                    # Get system statistics
```

#### **Example API Calls (Jungle Testnet)**
```bash
# Create 5 test accounts
curl -X POST http://localhost:3000/api/accounts/batch \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'

# Generate 100 mixed transactions
curl -X POST http://localhost:3000/api/transactions/mixed \
  -H "Content-Type: application/json" \
  -d '{"count": 100}'

# Detect anomalies in last 60 minutes
curl -X POST http://localhost:3000/api/anomalies/detect \
  -H "Content-Type: application/json" \
  -d '{"windowMinutes": 60}'

# Get statistics
curl http://localhost:3000/api/stats
```

#### **Database Setup (Jungle Testnet)**
```powershell
# Setup database structure
npm run setup-db

# Test with sample data
npm run test-sample-data
```

#### **Key Files & Logs**
```
jungletestnet/
  ├── data/                    # JSON storage
  │   ├── accounts.json        # Created accounts
  │   ├── transactions.json    # Transaction records
  │   └── anomalies.json       # Detected anomalies
  ├── logs/                    # Transaction logs
  │   └── transactions_YYYYMMDD.log
  └── .env                     # Configuration
```

---

## 🤖 **ML Model Training**

```powershell
cd ml-engine

# Train anomaly detection models
python training/train.py
# OR
make ml-train

# Evaluate models
python training/evaluate.py
# OR
make ml-evaluate

# Run Jupyter notebooks
jupyter notebook
```

---

## 🌱 **Data Management**

```powershell
# Seed database with sample data
python scripts/seed_data.py
# OR
make seed

# Load sample transactions
cd backend
python -c "import pandas as pd; df = pd.read_csv('sample_transactions.csv'); print(df.head())"
```

---

## 🧹 **Maintenance Commands**

### **Cleanup**
```powershell
# Clean Python cache files
make clean

# Manual cleanup
Get-ChildItem -Recurse -Directory __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Clean frontend build artifacts
cd frontend
Remove-Item -Recurse -Force dist, node_modules\.cache
```

### **Linting & Formatting**
```powershell
# Lint all code
make lint

# Backend only (Black + Flake8)
cd backend
black app/
flake8 app/
# OR
make lint-backend

# Frontend only (ESLint)
cd frontend
npm run lint
# OR
make lint-frontend
```

---

## 🔍 **Health Check & Debugging**

```powershell
# Run health check script
bash scripts/healthcheck.sh
# OR
make healthcheck

# Check if services are running
curl http://localhost:8000/health
curl http://localhost:5173

# View Python package versions
cd backend
pip list | grep -E "(fastapi|uvicorn|pydantic|pandas)"

# Check Node versions
node --version
npm --version

# View backend logs in real-time
cd backend
uvicorn app.main:app --reload --log-level debug
```

---

## 🔑 **API Testing with cURL**

### **Main Application API**

#### **Get Anomalies**
```bash
curl http://localhost:8000/api/v1/anomalies
```

#### **Get SHAP Features**
```bash
curl "http://localhost:8000/api/v1/anomalies/shap/ANO-123?top_k=5"
```

#### **Generate AI Narrative**
```bash
curl -X POST http://localhost:8000/api/v1/anomalies/narrative/generate \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_id": "ANO-123",
    "top_k": 5,
    "persona": "fraud-analyst"
  }'
```

#### **Get Transaction**
```bash
curl http://localhost:8000/api/v1/transactions/0xabc123...
```

### **Jungle Testnet API**

#### **Create Accounts**
```bash
curl -X POST http://localhost:3000/api/accounts/batch \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'
```

#### **Generate Transactions**
```bash
curl -X POST http://localhost:3000/api/transactions/mixed \
  -H "Content-Type: application/json" \
  -d '{"count": 100, "patterns": ["normal", "suspicious", "anomalous"]}'
```

#### **Detect Anomalies**
```bash
curl -X POST http://localhost:3000/api/anomalies/detect \
  -H "Content-Type: application/json" \
  -d '{"windowMinutes": 60, "threshold": 0.7}'
```

#### **Get Statistics**
```bash
curl http://localhost:3000/api/stats
```

---

## 🐛 **Troubleshooting**

### **Common Issues - Main Application**

#### **Port Already in Use**
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Stop-Process -Id <PROCESS_ID> -Force

# Or change port in backend
cd backend
uvicorn app.main:app --reload --port 8001
```

#### **Database Connection Failed**
```powershell
# Check if PostgreSQL is running
docker ps | findstr postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check connection manually
docker exec -it blockchain-anomaly-ai-postgres-1 psql -U postgres -d anomaly_db
```

#### **Module Not Found**
```powershell
# Reinstall Python dependencies
cd backend
pip install -r requirements.txt

# Or reinstall frontend dependencies
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
```

### **Common Issues - Jungle Testnet**

#### **Key Mismatch Error**
```powershell
# Run diagnostics to verify configuration
npm run diagnose

# Common causes:
# 1. Wrong private key in .env
# 2. Private key doesn't match account
# 3. Account doesn't exist on Jungle4

# Solution: Create new account at https://monitor.jungletestnet.io/
```

#### **Insufficient Balance**
```
Error: Account has insufficient balance

Solution:
1. Visit https://monitor.jungletestnet.io/
2. Enter your account name
3. Click "Get Tokens" from faucet
4. Wait 1-2 minutes and try again
```

#### **Account Creation Failed**
```powershell
# Check if master account exists
npm run diagnose

# Verify account name format:
# - Exactly 12 characters
# - Only lowercase a-z and numbers 1-5
# - Example: testacnt1234 (✓)  TestAccount12 (✗)
```

#### **RPC Connection Failed**
```powershell
# Try alternative RPC endpoints
# Edit .env and change JUNGLE_ENDPOINT to:

JUNGLE_ENDPOINT=https://jungle4.api.eosnation.io
# OR
JUNGLE_ENDPOINT=https://jungle.eosusa.io
# OR
JUNGLE_ENDPOINT=https://jungle4.greymass.com
```

#### **Transaction Timeout**
```javascript
// Increase timeout in your code or .env
TRANSACTION_TIMEOUT=30000  // 30 seconds

// Or retry the transaction
npm run workflow
```

### **Log Files**

#### **Main Application**
```powershell
# Backend logs (if running via Docker)
docker-compose logs -f backend

# Frontend logs (Vite)
# Check terminal where you ran: npm run dev

# Database logs
docker-compose logs -f postgres
```

#### **Jungle Testnet**
```powershell
# Check transaction logs
Get-Content jungletestnet\logs\transactions_*.log -Tail 50

# View all logs
Get-ChildItem jungletestnet\logs\

# API server logs (if running)
# Check terminal where you ran: npm run server
```

---

## 🔑 **API Testing with cURL**

## 📦 **Package Management**

### **Python (Backend)**
```powershell
cd backend

# Install new package
pip install requests

# Update requirements.txt
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

### **Node.js (Frontend)**
```powershell
cd frontend

# Install new package
npm install axios

# Install dev dependency
npm install --save-dev @types/node

# Update packages
npm update
```

---

## 🌐 **Environment Variables**

### **Main Application (.env)**
```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit environment variables
notepad .env
```

**Key Variables:**
```bash
# Database
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=anomaly_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=

# Cortex AI (Internal Lloyds Gemini API)
CORTEX_API_KEY=
CORTEX_BASE_URL=https://cortex.lloydsbanking.cloud/api
CORTEX_MODEL=gemini-2.5-flash-lite

# BigQuery (if using)
BIGQUERY_PROJECT_ID=ltc-hack2026-team35
BIGQUERY_DATASET=ltchack2026team35

# Blockchain (Polygon)
BLOCKCHAIN_RPC_URL=https://polygon-rpc.com
BLOCKCHAIN_CHAIN_ID=137s**

### **Main Application (Blockchain Anomaly AI)**

```powershell
# 1. Install dependencies
npm run bootstrap

# 2. Setup environment
Copy-Item .env.example .env
# Edit .env with your credentials

# 3. Start database (Docker)
docker-compose up -d postgres redis

# 4. Initialize database
cd backend
python init_db.py
cd ..

# 5. Start development servers
npm run dev
# This starts both backend (port 8000) and frontend (port 5173)

# 6. Open in browser
start http://localhost:5173
start http://localhost:8000/docs
```

### **Jungle Testnet (EOS Blockchain)**

```powershell
# 1. Navigate to Jungle Testnet project
cd ../jungletestnet

# 2. Install dependencies
npm install

# 3. Generate EOS keys
npm run generate-keys
# Save the generated keys!

# 4. Create account on Jungle Testnet
# Visit: https://monitor.jungletestnet.io/
# Create account and get free tokens

# 5. Configure environment
Copy-Item .env.example .env
notepad .env
# Add your account name and private key

# 6. Run diagnostics
npm run diagnose
# Verify everything is configured correctly

# 7. Run the full workflow
npm run workflow
# Creates accounts → Generates transactions → Detects anomalies

# 8. Or start the API server
npm run server
# API available at http://localhost:3000/api
```

### **Combined Setup (Both Systems)**

```powershell
# Setup main application
npm run bootstrap
docker-compose up -d postgres redis
cd backend && python init_db.py && cd ..

# Setup Jungle Testnet
cd ../jungletestnet
npm install
Copy-Item .env.example .env
# Configure .env with Jungle credentials
npm run diagnose

# Run both systems
# Terminal 1: Main app
cd ../blockchain-anomaly-ai
npm run dev

# Terminal 2: Jungle API
cd ../jungletestnet
npm run server

# Access points:
# Main Frontend:  http://localhost:5173
# Main Backend:   http://localhost:8000/docs
# Jungle API:     http://localhost:3000/apiestnet.io/
2. Create an account (12 characters: lowercase a-z and numbers 1-5)
3. Get free test tokens from the faucet
4. Export your private key from wallet
5. Add credentials to `.env` file

---

## 💡 **Quick Start Workflow**

```powershell
# 1. Install dependencies
npm run bootstrap

# 2. Setup environment
Copy-Item .env.example .env
# Edit .env with your credentials

# 3. Start database (Docker)
docker-compose up -d postgres redis

# 4. Initialize database
cd backend
python init_db.py
cd ..

# 5. Start development servers
npm run dev
# This starts both backend (port 8000) and frontend (port 5173)
### **Main Application Resources**
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Ant Design:** https://ant.design/
- **Vite:** https://vitejs.dev/
- **Hardhat:** https://hardhat.org/
- **SHAP Documentation:** https://shap.readthedocs.io/
- **Polygon Network:** https://polygon.technology/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

### **Jungle Testnet Resources**
- **Jungle4 Testnet Monitor:** https://monitor.jungletestnet.io/
- **Jungle4 Block Explorer:** https://jungle4.eosq.eosnation.io/
- **Create Account & Faucet:** https://jungletestnet.io/
- **WharfKit Documentation:** https://wharfkit.com/
- **EOS/Antelope Docs:** https://docs.eosnetwork.com/
- **Greymass RPC:** https://jungle4.greymass.com
- **EOS Network Foundation:** https://eosnetwork.com/

### **API Documentation**
- **Main App Swagger UI:** http://localhost:8000/docs
- **Main App ReDoc:** http://localhost:8000/redoc
- **Jungle API Docs:** See `jungletestnet/API.md`

### **Blockchain Explorers**
- **Polygon Mainnet:** https://polygonscan.com/
- **Polygon Mumbai (Testnet):** https://mumbai.polygonscan.com/
- **Jungle4 Explorer:** https://jungle4.eosq.eosnation.io/

### **Development Tools**
- **Cortex AI (Lloyds Internal):** https://cortex.lloydsbanking.cloud/api
- **BigQuery Console:** https://console.cloud.google.com/bigquery
- **GitHub Repository:** (Your repo URL)

---

## 📝 **Project Structure**

```
reboot-2026/
├── blockchain-anomaly-ai/          # Main application
│   ├── backend/                    # FastAPI backend (port 8000)
│   ├── frontend/                   # React frontend (port 5173)
│   ├── blockchain/                 # Hardhat smart contracts
│   ├── ml-engine/                  # ML models & training
│   ├── docs/                       # Documentation
│   └── docker-compose.yml          # Full stack deployment
│
└── jungletestnet/                  # EOS Jungle4 testnet project
    ├── src/
    │   ├── api/                    # REST API (port 3000)
    │   ├── modules/                # Core modules
    │   └── scripts/                # CLI scripts
    ├── data/                       # JSON storage
    ├── logs/                       # Transaction logs
    └── package.json                # Node.js configuration
```

---

**Last Updated:** July 27, 2026  
**Project:** Blockchain Anomaly AI - Reboot 2026  
**Jungle Testnet Integration:** EOS/Antelope Blockchainenerate
2. Backend → Fetches anomaly + transaction from PostgreSQL
3. SHAP Service → Computes feature importance (top K contributors)
4. Narrative Service → Builds persona-specific prompt
5. Cortex AI (Gemini) → Generates natural language explanation
6. Response → AI narrative + SHAP contributors + metadata
```

### **Example API Call**
```bash
curl -X POST http://localhost:8000/api/v1/anomalies/narrative/generate \
  -H "Content-Type: application/json" \
  -d '{
    "anomaly_id": "ANO-123",
    "top_k": 5,
    "persona": "fraud-analyst"
  }'
```

### **Available Personas**
- `fraud-analyst` - Analytical, detailed, pattern-focused (default)
- `compliance-officer` - Internal alert with regulatory terminology
- `relationship-manager` - Customer-friendly, neutral tone
- `auditor` - Technical, transparent with full traceability
- `regulator` - Formal, evidence-based for regulatory submission

### **SHAP Features Analyzed**
- `amount` - Transaction amount
- `transaction_hour` - Time of day (0-23)
- `transaction_type` - DEPOSIT (0), TRANSFER (1), WITHDRAWAL (2)
- `daily_transaction_count` - Number of daily transactions
- `account_balance` - Account balance after transaction
- `withdrawal_percentage` - Percentage of withdrawals
- `time_since_last_transaction` - Minutes since last activity

---

## 📚 **Documentation Files**

```
docs/
  ├── COMMANDS_AND_URLS.md           # This file
  ├── DEVELOPMENT_SETUP.md           # Development environment setup
  ├── api-contract.md                # API specifications
  ├── architecture.md                # System architecture
  ├── ANOMALY_CODE_REFERENCE.md      # Anomaly detection code reference
  ├── ANOMALY_RESULTS_STORAGE.md     # Storage and database schema
  ├── ENHANCED_SYSTEM_GUIDE.md       # Enhanced features guide
  ├── smart-contract.md              # Blockchain smart contracts
  └── BEST_PRACTICES.md              # Coding best practices
```

---

## 🔗 **Useful Links**

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Ant Design:** https://ant.design/
- **Vite:** https://vitejs.dev/
- **Hardhat:** https://hardhat.org/
- **SHAP Documentation:** https://shap.readthedocs.io/
- **Polygon Network:** https://polygon.technology/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Last Updated:** July 27, 2026  
**Project:** Blockchain Anomaly AI - Reboot 2026
