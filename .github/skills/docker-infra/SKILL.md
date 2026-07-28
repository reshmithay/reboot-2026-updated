---
name: docker-infra
description: "Use when working on Docker, docker-compose, Kubernetes, CI/CD, Nginx, Terraform, or deployment configuration in infra/ or .github/workflows/"
user-invocable: true
---

# Docker & Infrastructure Skill

You are an expert in containerization, orchestration, and deployment for this microservices architecture.

## Project Context

- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes
- **Web Server**: Nginx (reverse proxy, rate limiting)
- **IaC**: Terraform (planned)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana + Loki

## Architecture

```
┌─────────────────────────────────────────┐
│ Nginx (reverse proxy + rate limiting)  │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼──────────┬────────────┐
    │         │          │            │
┌───▼────┐ ┌─▼────┐ ┌──▼─────┐  ┌───▼────┐
│Backend │ │LLM   │ │Frontend│  │Postgres│
│(8000)  │ │(8001)│ │(80)    │  │(5432)  │
└────────┘ └──────┘ └────────┘  └────────┘
```

## Docker Services

### Backend
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY infra/nginx/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Docker Compose Pattern

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=${APP_ENV}
    env_file:
      - .env
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app  # dev hot-reload
    networks:
      - anomaly-net

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - anomaly-net

volumes:
  postgres_data:

networks:
  anomaly-net:
    driver: bridge
```

## Nginx Configuration

### Reverse Proxy + Rate Limiting
```nginx
http {
    upstream backend {
        server backend:8000;
    }
    
    # Rate limiting: 30 requests/min per IP
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
    
    server {
        listen 80;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
        }
        
        # Backend API
        location /api/v1/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 60s;
        }
        
        # LLM Server (longer timeout)
        location /api/v1/narratives/ {
            proxy_pass http://llm-narrative-server:8001;
            proxy_read_timeout 120s;
        }
    }
}
```

## Kubernetes Deployment

### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/your-org/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_HOST
          value: postgres-service
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

## CI/CD Pipeline

### Backend CI
```yaml
# .github/workflows/backend-ci.yml
name: Backend CI
on:
  push:
    branches: [main, develop]
    paths:
      - "backend/**"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      
      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt
      
      - name: Run tests
        working-directory: backend
        run: pytest tests/ -v --cov=app
```

### Production Deployment
```yaml
# .github/workflows/deploy-prod.yml
name: Deploy to Production
on:
  push:
    tags:
      - "v*"

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:latest
      
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f infra/kubernetes/
          kubectl rollout restart deployment/backend
```

## Common Tasks

### Local Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Build Individual Service
```bash
# Backend
docker build -t anomaly-backend:latest -f backend/Dockerfile backend/

# Frontend
docker build -t anomaly-frontend:latest -f infra/docker/frontend.Dockerfile frontend/
```

### Health Checks
```bash
# Check all services
bash scripts/healthcheck.sh

# Individual service
curl http://localhost:8000/health
```

### Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f infra/kubernetes/

# Check deployment status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/backend

# Scale replicas
kubectl scale deployment/backend --replicas=5
```

## Monitoring Stack

### Prometheus (metrics)
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

### Grafana (dashboards)
- Pre-configured dashboards in `monitoring/grafana/`
- Metrics: request rate, latency, error rate, anomaly detection stats

### Loki (logs)
- Aggregates logs from all services
- Query via Grafana or CLI

## Operating Rules

1. **Environment Variables**: Never hardcode secrets, use `.env` files
2. **Health Checks**: All services must expose `/health` endpoint
3. **Multi-stage Builds**: Minimize final image size (frontend builder pattern)
4. **Layer Caching**: Order Dockerfile commands by change frequency
5. **Resource Limits**: Always set memory/CPU limits in K8s
6. **Zero-downtime Deploys**: Use rolling updates in K8s
7. **Logging**: JSON-structured logs to stdout (12-factor app)

## Anti-patterns

- ❌ Don't run as root in containers — use non-root user
- ❌ Don't use `latest` tag in production — pin versions
- ❌ Don't store secrets in images — use env vars or K8s secrets
- ❌ Don't expose unnecessary ports
- ❌ Don't skip health checks — K8s needs them for restarts
- ❌ Don't use `docker-compose` in production — use K8s

## Security Best Practices

```dockerfile
# Use specific base image version
FROM python:3.12.4-slim

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Copy only what's needed
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser app/ ./app/

# Scan for vulnerabilities
RUN pip install --no-cache-dir safety && safety check
```

## Validation

After changes:
1. **Local**: `docker-compose up` and test endpoints
2. **Lint**: `docker-compose config` (validate YAML)
3. **Build**: `docker build` for each service
4. **Security**: Scan images with `docker scan <image>`
5. **K8s**: `kubectl apply --dry-run=client -f infra/kubernetes/`
