"""
README - Best Practices Implementation

This document explains the best practices applied to the codebase.

## Architecture Patterns

### 1. Dependency Injection (DI)
- **Container Pattern**: `app/core/container.py`
  - Centralized dependency management
  - Singleton instances
  - Easy testing with mock dependencies
  - Clear dependency graph

### 2. Configuration Management
- **Pydantic Settings**: `app/config/settings.py`
  - Type-safe configuration
  - Environment variable support
  - Validation at startup
  - Centralized settings

### 3. Data Validation
- **Pydantic Models**: `app/models/detection_models.py`
  - Request/response validation
  - Type safety
  - Automatic documentation
  - Custom validators

### 4. Error Handling
- **Custom Exceptions**: `app/core/exceptions.py`
  - Hierarchical exception structure
  - Rich error context
  - Structured error details
  - Proper error propagation

### 5. Utilities
- **Detector Utils**: `app/utilities/detector_utils.py`
  - Reusable helper functions
  - Decorators for common patterns
  - Circuit breaker pattern
  - Rate limiting

## Code Organization

```
backend/app/
├── api/                    # API routes
│   └── anomaly_routes.py  # REST endpoints
├── core/                   # Core application logic
│   ├── container.py       # DI container
│   └── exceptions.py      # Custom exceptions
├── models/                 # Data models
│   └── detection_models.py # Pydantic models
├── services/               # Business logic
│   └── anomaly/           # Anomaly detection
├── clients/                # External clients
│   └── bigquery/          # BigQuery integration
├── utilities/              # Helper functions
│   └── detector_utils.py  # Shared utilities
├── config/                 # Configuration
│   └── settings.py        # App settings
└── main.py                # Application factory
```

## Best Practices Applied

### 1. Type Hints
```python
from typing import Dict, Any, List, Optional

async def detect_all(
    self,
    transaction: Dict[str, Any]
) -> Dict[str, Any]:
    """Fully typed function signature."""
    pass
```

### 2. Async/Await
```python
# Parallel execution
results = await asyncio.gather(*tasks)

# Timeout handling
result = await asyncio.wait_for(func(), timeout=30)
```

### 3. Error Handling
```python
try:
    result = await detector.detect(tx, context)
except TimeoutError as e:
    logger.error(f"Timeout: {e}")
    # Graceful degradation
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    # Continue with other detectors
```

### 4. Logging
```python
logger.info("Operation started", extra={"tx_hash": tx_hash})
logger.error("Operation failed", exc_info=True)
```

### 5. Configuration
```python
# Environment-based config
class Settings(BaseSettings):
    DEBUG: bool = False
    BIGQUERY_PROJECT_ID: str
    
    class Config:
        env_file = ".env"
```

### 6. Validation
```python
class TransactionModel(BaseModel):
    tx_hash: str
    value: float = Field(ge=0)
    
    @field_validator('tx_hash')
    @classmethod
    def validate_hash(cls, v: str) -> str:
        if not v.startswith('0x'):
            raise ValueError("Invalid hash")
        return v
```

### 7. Decorators
```python
@with_timeout(seconds=30)
@with_error_handling("DetectorName")
async def detect(self, tx, ctx):
    """Decorated with timeout and error handling."""
    pass
```

### 8. Circuit Breaker
```python
breaker = CircuitBreaker(failure_threshold=5)
result = await breaker.call(external_api_call)
```

### 9. Rate Limiting
```python
limiter = RateLimiter(max_calls=100, time_window_seconds=60)
await limiter.acquire()
await api_call()
```

### 10. Dependency Injection
```python
# In FastAPI
@router.post("/detect")
async def detect(
    transaction: TransactionModel,
    service = Depends(get_anomaly_service)
):
    return await service.analyze(transaction)
```

## Design Patterns Used

### 1. **Factory Pattern**
- `create_app()` in main.py
- Creates configured FastAPI instance

### 2. **Strategy Pattern**
- Multiple detector implementations
- Common `BaseDetector` interface

### 3. **Observer Pattern**
- Event logging throughout
- Metrics collection

### 4. **Circuit Breaker**
- Protects external service calls
- Prevents cascade failures

### 5. **Singleton**
- Settings instance
- Container instance

### 6. **Repository Pattern**
- BigQueryReferenceClient
- Abstracts data access

## Code Quality Standards

### 1. **Function Length**
- Max 50 lines per function
- Extract complex logic to helpers

### 2. **Class Responsibility**
- Single Responsibility Principle
- Each class has one clear purpose

### 3. **DRY (Don't Repeat Yourself)**
- Shared utilities in detector_utils
- Reusable decorators

### 4. **SOLID Principles**
- S: Single Responsibility
- O: Open/Closed (extend via subclassing)
- L: Liskov Substitution (all detectors interchangeable)
- I: Interface Segregation (focused interfaces)
- D: Dependency Inversion (depend on abstractions)

### 5. **Documentation**
- Docstrings for all public methods
- Type hints everywhere
- README files

## Testing Strategy

### 1. **Unit Tests**
```python
import pytest
from app.services.anomaly.detectors.threshold_deposit_detector import ThresholdDepositDetector

@pytest.fixture
def detector():
    return ThresholdDepositDetector(config={})

async def test_detect_threshold(detector):
    result = await detector.detect(transaction, context)
    assert isinstance(result.is_anomaly, bool)
```

### 2. **Integration Tests**
```python
async def test_orchestrator_integration():
    orchestrator = AnomalyOrchestrator()
    await orchestrator.initialize()
    result = await orchestrator.detect_all(transaction)
    assert "detection_id" in result
```

### 3. **Mock Dependencies**
```python
from unittest.mock import AsyncMock

bq_client = AsyncMock()
bq_client.get_client_registry.return_value = mock_client
```

## Performance Optimizations

### 1. **Parallel Execution**
- All detectors run concurrently
- `asyncio.gather()` for parallelism

### 2. **Caching**
- Anomaly master cached in memory
- Settings cached with `@lru_cache`

### 3. **Connection Pooling**
- BigQuery client reused
- HTTP client pooling

### 4. **Lazy Loading**
- ML models loaded on demand
- Container lazy initialization

## Security Best Practices

### 1. **Input Validation**
- Pydantic models validate all inputs
- SQL injection prevention (parameterized queries)

### 2. **Error Messages**
- Don't expose internal details in production
- Generic error messages to users

### 3. **Logging**
- Don't log sensitive data (PII, credentials)
- Structured logging for audit

### 4. **Environment Variables**
- Secrets in env vars, not code
- `.env` file for local development

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Debug mode disabled in production
- [ ] Proper error handling tested
- [ ] Logging configured correctly
- [ ] Health check endpoint working
- [ ] CORS configured properly
- [ ] Timeouts set appropriately
- [ ] Rate limiting enabled
- [ ] Monitoring setup
- [ ] Alerts configured

## Usage Examples

### Basic Detection
```python
from app.core.container import get_container

container = get_container()
await container.initialize()

service = container.anomaly_service
result = await service.analyze_transaction(transaction)
```

### With Configuration
```python
from app.models.detection_models import AnomalyDetectionConfig
from app.models.detection_models import ThresholdDetectorConfig

config = AnomalyDetectionConfig(
    threshold_deposit=ThresholdDetectorConfig(min_pattern_count=4),
    enable_ml_models=True
)

orchestrator = AnomalyOrchestrator(config=config.model_dump())
```

### Error Handling
```python
from app.core.exceptions import AnomalyDetectionError

try:
    result = await service.analyze_transaction(tx)
except AnomalyDetectionError as e:
    logger.error(f"Detection failed: {e.message}")
    # Fallback logic
```

## Monitoring

### Metrics to Track
- Detection throughput (transactions/sec)
- Average detection time
- Error rate per detector
- BigQuery query latency
- ML model inference time
- Cache hit rate

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Correlation IDs for request tracking
- Performance metrics

## Next Steps

1. Add comprehensive unit tests
2. Set up CI/CD pipeline
3. Configure monitoring (Prometheus/Grafana)
4. Add API rate limiting
5. Implement request authentication
6. Add caching layer (Redis)
7. Set up alerting
8. Performance profiling
9. Load testing
10. Security audit
