# Hindsight Implementation Plan — Gram Vaani Memory

## 1. Current Architecture Summary

Gram Vaani is an agricultural voice- and text-enabled AI assistant for Indian farmers, developed with a FastAPI backend and a React/Vite frontend.

- **Backend Framework**: FastAPI (`app = FastAPI()`) running under Uvicorn.
- **Frontend Framework**: React 18 with Vite, Vanilla CSS, Lucide icons.
- **Authentication**: JWT bearer tokens (`PyJWT`), passwords hashed using `bcrypt`.
- **Database Architecture**:
  - **MongoDB Atlas** (`db = client.gramvani`): Stores regional agricultural knowledge in `hyperlocal_context`, regional farmer achievements in `success_stories`, field incident reports in `pest_outbreaks`, and environmental records in `environmental_profiles`.
  - **Amazon DynamoDB**: Stores user records (`gramvaani_users`), user queries (`gramvaani_user_querie`), sessions (`gramvaani_sessions`), village trust metrics, and community reports.
- **AI & Cloud Integrations**:
  - **Azure OpenAI**: Model `gpt-4o-mini` (or `gpt-4o`) for intent classification, multilingual question-answering, and query handling.
  - **Azure Speech Services**: High-fidelity Indian language Neural TTS and STT (`ta-IN`, `te-IN`, `kn-IN`, `ml-IN`, etc.).
  - **OpenWeather API**: Hyperlocal real-time weather and forecast data.

---

## 2. Relevant Existing Files

### Backend
- `backend/main.py`: Main FastAPI entry point containing routes for auth, text processing, audio processing, weather, crop prices, government schemes, hyperlocal context, feedback, and WhatsApp webhooks.
- `backend/advisor_endpoints.py`: APIRouter with environmental profile and advisory endpoints.
- `backend/data_aggregator.py`: Fetches and caches weather and regional crop data from MongoDB and external APIs.
- `backend/hyperlocal_data.py`: District-level soil, rainfall, crop calendar, pest alerts, and success stories.
- `backend/india_complete_data.py`: Nationwide agricultural data across 28 states and 8 union territories.
- `backend/transcribe_service.py`: Audio handling and speech recognition pipeline.
- `backend/.env` & `backend/.env.example`: Configuration and credentials.
- `backend/requirements.txt`: Python package dependencies.

### Frontend
- `frontend/src/App.jsx`: Main React application component, session management, and view routing.
- `frontend/src/Auth.jsx`: Farmer signup and login modal/page handling `phone_number` and `password`.
- `frontend/src/api/client.js` or Axios client: Communicates with FastAPI backend.

---

## 3. Existing Farmer Identity Flow

1. **Registration & Login**:
   - The farmer provides `phone_number` and `password`, along with initial preferences `language` (e.g., `"hi"`, `"te"`, `"en"`) and `location` (e.g., `"Guntur, Andhra Pradesh"`).
   - Upon successful authentication (`/api/login`), the server returns a JWT access token encoding `{"sub": user.phone_number}`.
2. **Authenticated Requests**:
   - The frontend attaches `Authorization: Bearer <token>` to all API requests.
   - The FastAPI dependency `get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security))` validates the JWT and returns the user dictionary.
   - In WhatsApp messaging (`/webhook`), the farmer's canonical identity is derived directly from the sender's normalized WhatsApp telephone number (`phone_number`).
3. **Canonical Farmer ID**:
   - The farmer's verified telephone number `phone_number` is the authoritative, unique, cross-session identifier (`farmer_id`).

---

## 4. Existing Data Model

- **Farmer Profile**:
  - `phone_number`: Unique identifier (string).
  - `language`: Preferred communication language code (e.g., `"hi"`, `"te"`, `"ta"`, `"mr"`, `"en"`).
  - `location`: Geographic location description (e.g., `"Guntur, Andhra Pradesh"`).
  - `created_at`: Registration timestamp.
- **Environmental Profile**:
  - `temperature`, `humidity`, `rainfall`, `nitrogen`, `phosphorus`, `potassium`, `soil_ph`.
- **Query History**:
  - `query_id`, `user_phone`, `query`, `query_english`, `response`, `query_type`, `timestamp`.

---

## 5. Proposed Hindsight Integration Point

To adhere strictly to modularity and prevent scattering Hindsight API calls across routes:
- Create a dedicated service package at:
  ```
  backend/services/hindsight/
  ├── __init__.py
  ├── config.py           # Configuration management, env var validation
  ├── client.py           # Low-level robust client wrapping official hindsight-client SDK
  ├── memory_types.py     # Data classes & taxonomy schemas for memory items
  └── memory_service.py   # High-level domain service with isolation, validation, & logging
  ```
- **Credit-Conscious Integration**:
  - Hindsight operations are exposed cleanly as a service layer.
  - **No automated loops or unsolicited calls** are placed in the recommendation or request pipelines during Phase 1 & Phase 2.
  - Retain is called explicitly when designated long-term facts (profile, constraints, corrections) are identified.
  - Recall is invoked only when explicitly requested by memory-aware services.
  - Recommendation generation (`process_ai_query` in `main.py`) remains **strictly unchanged** in this phase.

---

## 6. Proposed Memory Model (Phase 2 Taxonomy)

Memories are classified into eight durable categories:
1. `PROFILE`: Basic durable farm/farmer attributes (e.g., location, landholding size, soil type, language).
2. `PREFERENCE`: Farming preferences (e.g., preference for low-water crops, organic fertilizers, specific varieties).
3. `CONSTRAINT`: Critical operational limiters (e.g., lack of borewell, limited labor, seasonal budget constraints).
4. `CROP_HISTORY`: Prior season cultivation experiences, crops grown, and recorded failure or success reasons.
5. `RECOMMENDATION`: High-value historical recommendations provided to the farmer.
6. `CORRECTION`: Farmer-provided corrections that override prior beliefs or erroneous assumptions.
7. `OUTCOME`: Realized harvest or treatment results tied to prior recommendations.
8. `INCIDENT`: Significant agricultural events (e.g., pest attack, unseasonal frost, canal water shutoff).

### Farmer Isolation Strategy
- A project-level memory bank is used (e.g., `HINDSIGHT_BANK_ID="gramvaani"`).
- Every retained memory is tagged with:
  - `farmer:<farmer_id>`
  - `type:<memory_type>`
- Structured metadata includes `farmer_id`, `memory_type`, `source` (`farmer`, `farmer_profile`, `assistant`, `system`), `timestamp`, and domain fields (`crop`, `location`, `season`, `confidence`).
- During `recall`, strict tag filtering (`tags=[f"farmer:{farmer_id}"]`, `tags_match="all"`) guarantees that Farmer A's memories can never be retrieved by or leak into Farmer B's session.

---

## 7. Files That Will Be Modified

1. `backend/requirements.txt`: Add `hindsight-client` dependency.
2. `backend/.env.example`: Add Hindsight environment variable templates:
   - `HINDSIGHT_API_KEY`
   - `HINDSIGHT_BASE_URL`
   - `HINDSIGHT_BANK_ID`
3. `backend/main.py`: Register memory endpoints (for health check and controlled manual validation) while leaving existing recommendation and core endpoints intact.
4. `backend/services/hindsight/*`: New service layer files.
5. `backend/tests/*`: Automated unit and integration tests.
6. `docs/HINDSIGHT_IMPLEMENTATION.md`: Full architectural and operational documentation.

---

## 8. Files That Should Remain Untouched

- `frontend/*`: The UI, React components, and styling remain untouched in Phase 1 & 2.
- `backend/data_aggregator.py`: Preserved in current working state.
- `backend/advisor_endpoints.py`: Preserved in current working state.
- `backend/hyperlocal_data.py` & `india_complete_data.py`: Preserved in current working state.
- `backend/transcribe_service.py`: Preserved in current working state.
- `backend/deploy-azure.sh`: Preserved in current working state.

---

## 9. Risks and Ambiguities Discovered

1. **Hindsight Cloud Credits**: Cloud credits are limited. The client implementation must be strictly on-demand, caching health check results where appropriate, and avoiding any automatic reflection or background indexing sweeps.
2. **Network Resilience**: If the Hindsight endpoint is unreachable, timed out, or returns a 4xx/5xx status, the service layer must catch exceptions, log cleanly without leaking API keys, and fail gracefully with empty results so Gram Vaani never crashes.
3. **Database Dual Setup**: User authentication currently depends on DynamoDB / MongoDB. Memory operations must decouple from database choice by taking the authenticated `farmer_id` string from `current_user` regardless of backend storage backing.
