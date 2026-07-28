# Development Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Google Cloud SDK (for BigQuery)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
# Required:
# - GOOGLE_APPLICATION_CREDENTIALS
# - BIGQUERY_PROJECT_ID
# - GEMINI_API_KEY (if using LLM narratives)
```

### 3. Database Setup

```bash
# Start PostgreSQL
# Windows: Start PostgreSQL service
# Linux: sudo systemctl start postgresql

# Create database
psql -U postgres -c "CREATE DATABASE anomaly_db;"

# Run migrations (if using Alembic)
alembic upgrade head
```

### 4. Redis Setup

```bash
# Windows: Start Redis service
# Linux: sudo systemctl start redis

# Verify
redis-cli ping
# Should return: PONG
```

### 5. BigQuery Setup

```bash
# Authenticate
gcloud auth application-default login

# Create dataset
bq mk --dataset --location=us-central1 blockchain_anomaly_detection

# Create tables
bq query < ../docs/bigquery_table_schemas.sql
```

### 6. Train ML Models

```bash
# Generate and train models
python scripts/train_models.py

# Models will be saved to: ml-engine/models/pycaret/
```

### 7. Run Backend

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 8. Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_detectors.py -v

# Open coverage report
# Windows: start htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```


## Docker Setup (Alternative)

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Verification

### 1. Health Check

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","app":"Blockchain Anomaly Detection","version":"1.0.0"}
```

### 2. Test Detection Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/anomaly/detect \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0xabc123def456",
    "from_address": "0x742d35cc6634c0532925a3b844bc9e7595f0beb",
    "to_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
    "value": 9500.0,
    "timestamp": "2026-07-23T23:30:00Z",
    "gas_ratio": 0.85
  }'
```

### 3. Check API Docs

Open browser: http://localhost:8000/docs

## Common Issues

### Issue: BigQuery Authentication Error

**Solution:**
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Or in .env file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Issue: Import Errors

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: PyCaret Installation Fails

**Solution:**
```bash
# Install without PyCaret (uses sklearn fallback)
pip install -r requirements.txt --no-deps pycaret

# Or remove pycaret from requirements.txt
# System will use sklearn Isolation Forest instead
```

### Issue: Port Already in Use

**Solution:**
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

## Development Workflow

### 1. Make Changes

```bash
# Edit code
# Add tests
# Update documentation
```

### 2. Format Code

```bash
# Format with Black
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/ tests/
```

### 3. Run Tests

```bash
pytest -v
```

### 4. Type Check

```bash
mypy app/
```

### 5. Commit

```bash
git add .
git commit -m "feat: add new detector"
git push
```

## Production Deployment

### 1. Build Docker Image

```bash
docker build -t anomaly-detection-backend:latest .
```

### 2. Push to Registry

```bash
docker tag anomaly-detection-backend:latest gcr.io/PROJECT-ID/anomaly-detection-backend:latest
docker push gcr.io/PROJECT-ID/anomaly-detection-backend:latest
```

### 3. Deploy to Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 4. Configure Monitoring

```bash
# Prometheus
kubectl apply -f k8s/prometheus-config.yaml

# Grafana
kubectl apply -f k8s/grafana-config.yaml
```

## Monitoring

### Metrics Endpoints

- Application: `http://localhost:8000/metrics`
- Health: `http://localhost:8000/health`

### Logs

```bash
# View application logs
docker-compose logs -f backend

# Or with kubectl
kubectl logs -f deployment/anomaly-detection-backend
```

## Troubleshooting

### Enable Debug Mode

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart application
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d anomaly_db

# Check connection string
python -c "from app.config.settings import settings; print(settings.postgres_url)"
```

### BigQuery Issues

```bash
# Test BigQuery access
python -c "from google.cloud import bigquery; client = bigquery.Client(); print('Connected')"
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PyCaret Documentation](https://pycaret.gitbook.io/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Project Architecture](../docs/architecture.md)
- [Best Practices](../docs/BEST_PRACTICES.md)
