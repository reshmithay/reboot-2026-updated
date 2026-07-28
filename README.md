# Blockchain Anomaly AI

> **Reboot 2026 Hackathon** — Real-time anomaly detection in financial transactions using blockchain, ML, and LLM-powered narratives.

## Overview

This system monitors on-chain and off-chain financial transactions, detects anomalies using ML models (Isolation Forest + Autoencoder), logs immutable audit trails on-chain, and generates human-readable fraud explanations via Gemini LLM.

## Architecture

```
[Blockchain / Transactions]
        │
        ▼
[Backend API (FastAPI)] ──► [ML Engine] ──► Anomaly Score
        │                                        │
        ▼                                        ▼
[BigQuery Analytics]              [LLM Narrative Server]
        │                                        │
        ▼                                        ▼
[Firebase Notifications]         [Smart Contract Audit Trail]
        │
        ▼
[React Frontend Dashboard]
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python / FastAPI |
| ML Engine | Scikit-learn, PyTorch (Isolation Forest + Autoencoder) |
| LLM Narrative | Google Gemini API (integrated in backend) |
| Blockchain | EOS Jungle Testnet |
| Frontend | React + TypeScript + Vite |
| Database | PostgreSQL |
| Analytics | Google BigQuery |
| Infra | Docker, Nginx |

## Quick Start

```bash
# Clone and bootstrap
git clone <repo>
cd blockchain-anomaly-ai
make bootstrap

# Start all services
docker-compose up -d

# Or run individually
make backend
make frontend
```

## Project Structure

- `backend/` — FastAPI backend with anomaly detection, blockchain integration, and Gemini AI narratives
- `ml-engine/` — Model training, evaluation, and inference
- `frontend/` — React dashboard for real-time anomaly monitoring
- `infra/` — Docker and Nginx configs
- `scripts/` — Utility scripts for bootstrapping and health checks
- `docs/` — Architecture, API contracts, deployment guides

## Team

Built for **Reboot 2026 Hackathon** — Financial Anomaly Detection Track.
# 2026-reboot
