# Architecture Decision Log

## ADR-001: FastAPI for Backend API
**Date:** 2026-07-21  
**Status:** Accepted  
**Decision:** Use FastAPI (Python) for the backend API layer.  
**Rationale:** FastAPI's async-first design, auto-generated OpenAPI docs, Pydantic validation, and native Python ML library integration make it ideal for this ML-heavy system.

---

## ADR-002: Isolation Forest + Autoencoder Ensemble
**Date:** 2026-07-21  
**Status:** Accepted  
**Decision:** Use an ensemble of Isolation Forest (60% weight) and Autoencoder (40% weight) for anomaly scoring.  
**Rationale:** Isolation Forest excels at detecting global outliers in tabular data. Autoencoders capture complex non-linear patterns via reconstruction error. The ensemble reduces false positives.

---

## ADR-003: Polygon for Smart Contracts
**Date:** 2026-07-21  
**Status:** Accepted  
**Decision:** Deploy smart contracts on Polygon (MATIC) rather than Ethereum mainnet.  
**Rationale:** Lower gas fees for frequent writes (anomaly events, audit logs). High throughput. EVM-compatible so contracts are identical to Ethereum.

---

## ADR-004: Gemini 1.5 Pro for Narrative Generation
**Date:** 2026-07-21  
**Status:** Accepted  
**Decision:** Use Google Gemini 1.5 Pro for LLM-powered fraud narrative generation.  
**Rationale:** Large context window (1M tokens) allows passing full transaction history. Native Google Cloud integration with BigQuery/Firebase. Strong performance on structured financial text.

---

## ADR-005: Microservice for LLM Narrative Server
**Date:** 2026-07-21  
**Status:** Accepted  
**Decision:** Separate the LLM narrative generation into its own FastAPI microservice.  
**Rationale:** LLM calls are slow (3-10s). Isolating them prevents blocking the main backend. Independent scaling and rate-limit management. Can be swapped for a different LLM provider without affecting core services.

---

## ADR-006: BigQuery for Analytics
**Date:** 2026-07-21  
**Status:** Accepted  
**Decision:** Use BigQuery for transaction analytics and historical ML feature computation.  
**Rationale:** Serverless SQL analytics at petabyte scale. Native GCP integration. Cost-effective for batch analytical queries over large transaction datasets.
