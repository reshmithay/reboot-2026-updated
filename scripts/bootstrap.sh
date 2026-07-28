#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo "  Blockchain Anomaly AI — Bootstrap Script  "
echo "============================================"

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3.10+ required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js 20+ required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }

# Copy env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — update with your credentials"
fi

# Backend
echo "\n[1/4] Installing backend dependencies..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
deactivate
cd ..

# LLM Narrative Server
echo "\n[2/4] Installing LLM server dependencies..."
cd llm-narrative-server
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet -r requirements.txt
deactivate
cd ..

# Frontend
echo "\n[3/4] Installing frontend dependencies..."
cd frontend
npm install --silent
cd ..

# Blockchain
echo "\n[4/4] Installing blockchain dependencies..."
cd blockchain
npm install --silent
cd ..

echo "\n Bootstrap complete!"
echo "  Start services: make docker-up"
echo "  Or individually: make backend / make frontend / make llm-server"
