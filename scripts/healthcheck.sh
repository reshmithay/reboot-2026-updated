#!/usr/bin/env bash
set -euo pipefail

# Health check script for all services

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
LLM_URL="${LLM_URL:-http://localhost:8001}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

check_service() {
  local name=$1
  local url=$2
  local status
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url/health" 2>/dev/null || echo "000")
  if [ "$status" == "200" ]; then
    echo "[OK]   $name ($url)"
  else
    echo "[FAIL] $name ($url) — HTTP $status"
  fi
}

echo "=== Service Health Check ==="
check_service "Backend API"         "$BACKEND_URL"
check_service "LLM Narrative Server" "$LLM_URL"
echo "==========================="
