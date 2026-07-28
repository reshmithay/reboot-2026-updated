---
name: python-backend
description: "Use when working on Python FastAPI backend, services, schemas, repositories, clients, or utilities in backend/ or llm-narrative-server/"
user-invocable: true
---

# Python Backend Development Skill

You are an expert in Python 3.12, FastAPI, and async web services for this anomaly detection system.

## Project Context

- **Framework**: FastAPI + Uvicorn
- **Python Version**: 3.12
- **Validation**: Pydantic v2
- **HTTP Client**: httpx (async)
- **Web3**: web3.py
- **LLM**: Google Gemini API
- **Database**: PostgreSQL + SQLAlchemy (planned)
- **Cache**: Redis

## Architecture

```
backend/app/
├── api/            # Route handlers (anomaly_routes, transaction_routes, etc.)
├── services/       # Business logic (anomaly, blockchain, narrative, transaction)
├── clients/        # External API clients (Gemini, Web3, BigQuery, Firebase)
├── repositories/   # Database access layer
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response models
├── utilities/      # Logger, constants, validators, helpers, exceptions
└── config/         # Settings (environment variables)
```

## Code Patterns

### Route Handler Pattern
```python
# api/anomaly_routes.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.anomaly_schema import AnomalyResponse
from app.services.anomaly.anomaly_service import AnomalyService

router = APIRouter()

@router.post("/detect", response_model=AnomalyResponse)
async def detect_anomaly(
    payload: AnomalyDetectRequest,
    service: AnomalyService = Depends(),
):
    try:
        return await service.detect_and_record(payload.transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### Service Pattern
```python
# services/anomaly/anomaly_service.py
class AnomalyService:
    def __init__(self):
        self._model = None
    
    async def detect_and_record(self, tx_id: str) -> dict:
        # 1. Load features
        # 2. Score with ML model
        # 3. Persist to DB
        # 4. Write to blockchain if anomaly
        # 5. Send notification
        return result
```

### Schema Pattern
```python
# schemas/anomaly_schema.py
from pydantic import BaseModel, Field
from datetime import datetime

class AnomalyResponse(BaseModel):
    id: str
    score: float = Field(..., ge=0.0, le=1.0)
    severity: str
    detected_at: datetime
    
    class Config:
        from_attributes = True
```

### Client Pattern
```python
# clients/gemini/gemini_client.py
import google.generativeai as genai
from app.config.settings import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def generate(self, prompt: str) -> str:
        response = self._model.generate_content(prompt)
        return response.text
```

## Operating Rules

1. **Async First**: Use `async def` for all I/O operations (DB, HTTP, file)
2. **Type Hints**: Always include type annotations for function signatures
3. **Pydantic for Validation**: Use Pydantic models for all request/response data
4. **Dependency Injection**: Use FastAPI's `Depends()` for services
5. **Error Handling**: Raise `HTTPException` with proper status codes
6. **Logging**: Use `get_logger(__name__)` from utilities
7. **Settings**: Access config via `settings` from `config/settings.py`
8. **Never Block**: No synchronous I/O in async functions

## Common Tasks

### Adding a New Endpoint
1. Define Pydantic schemas in `schemas/`
2. Create route handler in `api/`
3. Implement business logic in `services/`
4. Register router in `main.py`: `app.include_router(router, prefix="/api/v1/...")`

### Adding External API Client
1. Create client class in `clients/<service>/`
2. Initialize in `__init__` with settings
3. Implement async methods
4. Add required settings to `config/settings.py`

### Database Operations
1. Define SQLAlchemy model in `models/`
2. Create repository in `repositories/`
3. Use repository methods in services
4. Return Pydantic schemas from routes, not ORM models

### ML Model Integration
1. Load model in service `__init__` or lazily
2. Store models in `ml-engine/models/`
3. Use numpy/pandas for feature engineering
4. Return normalized scores (0-1 range)

## Project-Specific Details

### Anomaly Detection Pipeline
```python
# 1. Extract features from transaction
features = extract_features(transaction)

# 2. Score with ensemble (Isolation Forest + Autoencoder)
if_score = isolation_forest.predict(features)
ae_score = autoencoder_reconstruction_error(features)
final_score = 0.6 * if_score + 0.4 * ae_score

# 3. Classify severity
severity = classify_severity(final_score)  # low/medium/high/critical

# 4. Write to blockchain
await blockchain_service.record_anomaly(anomaly_id, final_score, tx_hash)

# 5. Send notification if high/critical
if severity in ["high", "critical"]:
    await notification_service.send_alert(anomaly)
```

### LLM Narrative Generation
```python
# Build prompt from template
prompt = build_anomaly_narration_prompt(anomaly, transaction)

# Call Gemini
gemini = GeminiClient()
narrative = await gemini.generate(prompt, temperature=0.7)

# Parse and structure response
return NarrativeResponse(
    id=uuid4(),
    anomaly_id=anomaly_id,
    title=extract_title(narrative),
    summary=extract_summary(narrative),
    detailed_explanation=narrative,
    ...
)
```

## Anti-patterns

- ❌ Don't use `requests` — use `httpx` for async HTTP
- ❌ Don't use blocking file I/O — use `aiofiles`
- ❌ Don't access `request.json()` directly — use Pydantic models
- ❌ Don't return SQLAlchemy models from routes — convert to Pydantic
- ❌ Don't hardcode secrets — use environment variables via `settings`
- ❌ Don't use `print()` — use `logger.info/error/warning`

## Validation

After changes:
1. Run `black app/` to format code
2. Run `flake8 app/` to check style
3. Run `pytest tests/ -v` to run tests
4. Start server: `uvicorn app.main:app --reload`
5. Check `/docs` for auto-generated API documentation
