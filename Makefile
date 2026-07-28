.PHONY: bootstrap backend frontend blockchain-deploy docker-up docker-down test lint clean

# ── Bootstrap ──────────────────────────────────────────────────────────────────
bootstrap:
	@echo "Setting up blockchain-anomaly-ai..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cp .env.example .env
	@echo "Bootstrap complete. Update .env with your credentials."

# ── Run Services ───────────────────────────────────────────────────────────────
backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

# ── Docker ─────────────────────────────────────────────────────────────────────
docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ── Blockchain ─────────────────────────────────────────────────────────────────
# Note: Using EOS Jungle Testnet via backend API
# See jungletestnet/ folder for EOS blockchain integration

# blockchain-compile:
# 	cd blockchain && npx hardhat compile

# blockchain-deploy-local:
# 	cd blockchain && npx hardhat run scripts/deploy.js --network localhost

# blockchain-deploy-testnet:
# 	cd blockchain && npx hardhat run scripts/deploy.js --network mumbai

# blockchain-test:
# 	cd blockchain && npx hardhat test

# ── ML Engine ──────────────────────────────────────────────────────────────────
ml-train:
	cd ml-engine && python training/train.py

ml-evaluate:
	cd ml-engine && python training/evaluate.py

# ── Tests ──────────────────────────────────────────────────────────────────────
test-backend:
	cd backend && pytest tests/ -v --cov=app

test-all: test-backend blockchain-test
	@echo "All tests passed."

# ── Linting ────────────────────────────────────────────────────────────────────
lint-backend:
	cd backend && black app/ && flake8 app/

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend

# ── Seed Data ──────────────────────────────────────────────────────────────────
seed:
	python scripts/seed_data.py

# ── Health Check ───────────────────────────────────────────────────────────────
healthcheck:
	bash scripts/healthcheck.sh

# ── Clean ──────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
	cd frontend && rm -rf dist node_modules/.cache
	@echo "Cleaned."
