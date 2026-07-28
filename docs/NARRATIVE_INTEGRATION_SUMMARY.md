# Narrative Generation Integration - Implementation Summary

## Overview
Successfully integrated SHAP-based explainability with Cortex AI (Gemini) for generating human-readable narratives explaining anomaly detections in the blockchain transaction monitoring system. **All functionality consolidated into the backend - no separate LLM server required.**

## Architecture

### Consolidated Backend Architecture
**Location:** `backend/` (Port 8000 only)

**Components:**
- **Cortex Client:** `app/clients/cortex_client.py`
  - Direct integration with Lloyds Cortex API
  - Chat completion interface
  - Error handling and SSL verification bypass for internal API

- **SHAP Narrative Service:** `app/services/narrative_service.py`
  - Generates narratives from SHAP contributors
  - Builds prompts for explainable AI
  - Integrates with Cortex client
  - Fallback narrative generation when Cortex unavailable

- **SHAP Explainer Service:** `app/services/shap_explainer_service.py`
  - Computes SHAP values using ML models
  - Rule-based approximation when SHAP unavailable
  - Feature impact calculations based on business rules

- **Configuration:** `app/config/settings.py`
  - Cortex API credentials and settings
  - Model configuration (gemini-2.5-flash-lite)
  - Temperature and timeout settings

### API Endpoints (Port 8000)
**Location:** `backend/app/api/anomaly_routes.py`

#### GET /api/v1/anomalies/shap/{anomaly_id}
- Computes SHAP feature contributions for an anomaly
- Returns top K features with impact scores
- Response includes:
  - Feature names and values
  - SHAP contributions (positive = increased risk, negative = decreased risk)
  - Direction indicators
  - Prediction probability and label

#### POST /api/v1/anomalies/narrative/generate
- Orchestrates the narrative generation pipeline
- Fetches anomaly and transaction data
- Computes SHAP features
- **Calls local narrative service (ShapNarrativeService)**
- Returns complete narrative with SHAP analysis

**Supporting Services:**
  - Computes SHAP values using ML models
  - Rule-based approximation when SHAP unavailable
  - Feature impact calculations based on business rules
  - Handles 7 key features:
    - Transaction amount
    - Transaction hour
    - Transaction type
    - Daily transaction count
    - Account balance
    - Withdrawal percentage
    - Time since last transaction

- **Schemas:** `backend/app/schemas/narrative_schemas.py`
  - Request/response models for SHAP and narrative endpoints

### 3. Frontend Integration
**Location:** `frontend/src/`

**Components Updated:**

#### Narrative Service
**File:** `services/narrative/narrativeService.ts`
- `getShapFeatures()`: Fetch SHAP contributors for anomaly
- `generateShapNarrative()`: Request AI narrative generation

#### Custom Hook
**File:** `pages/Narrative/hooks/useShapNarrative.ts`
- Manages narrative fetching and state
- Auto-generation on page load
- Error handling and retry logic
- Loading states

#### Anomaly Narrative Page
**File:** `pages/Narrative/AnomalyNarrativePage.tsx`
- Integrated SHAP narrative hook
- Loading and error states with visual feedback
- Retry mechanism with button
- Passes narrative to AI component

#### AI Generated Narrative Component
**File:** `pages/Narrative/components/AIGeneratedNarrative.tsx`
- **New Props:**
  - `shapContributors`: Array of SHAP feature impacts
  - `predictionLabel`: Risk classification
  - `modelUsed`: LLM model identifier
- **Visual Enhancements:**
  - SHAP contributors table with color coding
  - Direction indicators (↑ Risk / ↓ Risk)
  - Impact scores with positive/negative coloring
  - Model and prediction label tags in header

## Data Flow

```
1. User opens Anomaly Narrative Page
   ↓
2. Frontend fetches anomaly data
   ↓
3. useShapNarrative hook triggers
   ↓
4. POST /anomalies/narrative/generate
   ↓
5. Backend fetches anomaly + transaction
   ↓
6. ShapExplainerService computes features
   ↓
7. Backend calls LLM Narrative Server
   ShapNarrativeService generates narrative
   ↓
8. CortexClient calls Gemini API
   ↓
9. Narrative returned to frontend
   ↓
10  - AI-generated explanation
    - SHAP contributors table
    - Risk indicators
```

## SHAP Feature Analysis

### Features Analyzed
1. **Transaction Amount** - Large amounts increase risk
2. **Transaction Hour** - Off-hours (night) increase risk
3. **Transaction Type** - Withdrawals higher risk than deposits
4. **Daily Transaction Count** - High frequency flags suspicious activity
5. **Account Balance** - Low balance after transaction is risky
6. **Withdrawal Percentage** - >90% of balance is critical
7. **Time Since Last Transaction** - Very short gaps indicate velocity risk

### Impact Scoring
- Positive SHAP values → Increased risk
- Negative SHAP values → Decreased risk
- Magnitude indicates strength of contribution

## Prompt Engineering

The narrative prompt includes:
- Prediction label and probability
- Top 5 SHAP contributors with values
- Clear tasks:
  1. Explain model prediction
  2. Rank important drivers
  3. Identify risk-increasing factors
  4. Identify risk-decreasing factors
  5. Business interpretation
  6. Numerical SHAP mentions

**Guidelines:**
- No SHAP theory explanations
- Business-focused language
- Regulatory-suitable format
- Actionable insights
- Clear sections

## Configuration

### Environment Variables

**Backend (.env):**
```
LLM_SERVER_URL=http://localhost:8001
```

**LLM Narrative Server (.env):**
# Cortex API Configuration (Lloyds Internal Gemini)
CORTEX_API_KEY=ck_dev_PjgvIybRQB_cc9Y-IbpBy6u2DieHqksA382pOeyc2K0
CORTEX_BASE_URL=https://cortex.lloydsbanking.cloud/api
CORTEX_MODEL=gemini-2.5-flash-lite
CORTEX_TEMPERATURE=0.2
CORTEX_TIMEOUT=12
### Backend
- httpx>=0.27.0 (already present)
- No new packages required

### LLM Narrative Server
- fastapi>=0.111.0
- **requests>=2.31.0** - For Cortex API HTTP calls
- httpx>=0.27.0 (already present)

✅ **Explainability:** SHAP values provide transparent, quantifiable feature impacts
✅ **AI Narratives:** Cortex/Gemini generates human-readable explanations
✅ **Visual Clarity:** Color-coded table shows risk factors with directional indicators
✅ **Error Handling:** Graceful fallbacks, retry mechanisms, loading states
✅ **Scalability:** Separate microservice for LLM operations
✅ **Flexibility:** Rule-based SHAP approximation when model unavailable
✅ **Business Focus:** Prompts designed for compliance and fraud analysts

## Testing Checklist
Single Server Architecture:** All functionality in backend - no microservice complexity
✅ **Explainabackend server on port 8000
- [ ] Verify Cortex API connectivity
- [ ] Navigate to anomaly narrative page
- [ ] Verify SHAP features endpoint returns data
- [ ] Verify narrative generation completes (without separate LLM server)
- [ ] Check SHAP contributors table renders
- [ ] Verify risk direction indicators (↑/↓)
- [ ] Test retry mechanism on error
- [ ] Validate loading states
- [ ] Check model and prediction label tags
- [ ] Test fallback narrative when Cortex unavailable
- [ ] Check model and prediction label tags

## Next Steps

1. **Start Services:** (includes narrative generation)
   cd backend
   uvicorn app.main:app --reload --port 8000
   
   # Terminal 2main:app --reload --port 8001
   
   # Terminal 3: Frontend
   cd frontend
   npm run dev
   ```

2. **Test Integration:**
   - Detect an anomaly using compliance dashboard
   - Navigate to narrative page via "View Full Report"
   - Observe SHAP narrative generation
   - Review feature contributions table

3. **Production Considerations:**
   - Add SHAP model persistence
   - Implement narrative caching
   - Add rate limiting for Cortex API
   - Monitor LLM costs and latency
   - Add narrative quality metrics

## Files Modified/Created

### Created (13 files):
1. `llm-narrative-server/app/config/settings.py`
2. `llm-narrative-server/app/clients/cortex_client.py`
3. `llm-narra6 files):
1. `backend/app/clients/cortex_client.py` - Cortex API client
2. `backend/app/services/narrative_service.py` - SHAP narrative generation
3. `backend/app/services/shap_explainer_service.py` - SHAP computation
4. `backend/app/schemas/narrative_schemas.py` - Request/response models
5. `frontend/src/pages/Narrative/hooks/useShapNarrative.ts` - React hook
6. `docs/NARRATIVE_INTEGRATION_SUMMARY.md` - This file

### Modified (6 files):
1. `backend/app/config/settings.py` - Added Cortex configuration
2. `backend/app/api/anomaly_routes.py` - Added SHAP and narrative endpoints (consolidated)
3. `backend/requirements.txt` - Added requests library
4. `frontend/src/services/narrative/narrativeService.ts` - Added SHAP methods
5. `frontend/src/pages/Narrative/hooks/index.ts` - Exported new hook
6. `frontend/src/pages/Narrative/AnomalyNarrativePage.tsx` - Integrated SHAP narrative
7. `frontend/src/pages/Narrative/components/AIGeneratedNarrative.tsx` - Added SHAP table

### Deprecated (LLM Narrative Server - No Longer Needed):
~~llm-narrative-server/~~ - Functionality moved to backend
The narrative generation system is now fully integrated with SHAP explainability and Cortex AI, providing transparent, AI-powered explanations for anomaly detections.
 **All functionality is consolidated in the backend - no separate LLM server needed!**

## Advantages of Consolidated Architecture

✅ **Simpler Deployment:** Only one backend server to run and maintain
✅ **Reduced Dependencies:** No need to install and manage separate LLM server packages
✅ **Better Performance:** No network overhead between services
✅ **Easier Debugging:** All logs in one place
✅ **Lower Complexity:** Fewer moving parts, simpler architecture
✅ **Cost Effective:** One server to monitor and scale