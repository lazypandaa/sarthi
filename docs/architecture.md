# Sarthi System Architecture

This document describes the end-to-end architecture of **Sarthi**, an agricultural AI platform that combines authoritative Government of India agronomic baselines with persistent, long-term farmer memory powered by [Hindsight](https://github.com/vectorize-io/hindsight).

> **Publishing note**: When publishing the article and LinkedIn post, tag Code.in as required by the submission guide.

---

## 1. High-Level System Architecture

Sarthi enforces a strict separation between **authoritative agricultural ground truth** (which the LLM is never allowed to fabricate) and **personal farmer operational memory** (retained across seasons via Hindsight).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLIENT PRESENTATION LAYER                             │
│                                                                             │
│  [ React 19 + TypeScript + Vite Web App ]         [ Native Android App ]    │
│  • Voice-First Audio Recorder                     • Jetpack Compose UI      │
│  • Memory Dashboard ("What I Remember")           • Background Audio Record │
│  • Reasoning Influence Badges                     • Low-Bandwidth Offline   │
│  • Mandi Market Intelligence & Crop Calendar      • Memory-Informed Cards   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTPS / JSON / Audio WAV
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND GATEWAY                             │
│                      (Python 3.10+ / Python 3.14)                           │
│                                                                             │
│  [ Authentication & Security ]        [ Core Routers ]                      │
│  • JWT Bearer Verification             • /process-audio & /process-text      │
│  • Phone Number Identity Binding       • /api/recommendation                │
│  • Rate Limiting & Input Validation    • /api/feedback                      │
│                                        • /api/memory/*                      │
└───────────────────┬─────────────────────────────────────┬───────────────────┘
                    │                                     │
                    ▼                                     ▼
┌─────────────────────────────────────┐ ┌─────────────────────────────────────┐
│  AUTHORITATIVE AGRI DATA LAYER      │ │    HINDSIGHT LONG-TERM MEMORY       │
│  (Locally Persisted & Cached)       │ │    (Semantic Agent Memory)          │
│                                     │ │                                     │
│  • Soil Health Card Portal          │ │  • HindsightClient SDK Wrapper      │
│    (702 District Soil Baselines)    │ │  • FarmerMemoryService              │
│  • ICAR Master Crops (22 Crops)     │ │    - Tenant Isolation (farmer:<id>) │
│  • CRIDA Multi-Season Calendars     │ │    - SHA-256 Deduplication Cache    │
│    (13 Kharif/Rabi/Zaid Schedules)  │ │    - 8-Type Memory Taxonomy         │
│  • Agmarknet APMC Mandi Rates       │ │  • MemoryAwareRecommender           │
│  • IMD Agromet Weather Advisories   │ │    - Targeted Recall (Limit=6)      │
│  • In-Memory TTL Cache (<10ms)      │ │    - Precedence Override Policy     │
│  • Azure Table Storage / SQLite DB  │ │    - Memory Influence Generator     │
└───────────────────┬─────────────────┘ └─────────────────┬───────────────────┘
                    │                                     │
                    └───────────────────┬─────────────────┘
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HYBRID REASONING ENGINE (AZURE OPENAI)                   │
│                                                                             │
│  Combined Prompt Structure:                                                 │
│  1. System Role & Agricultural Constraints                                  │
│  2. Local Agronomic Baseline (District Soil pH, NPK, Mandi Price, Weather)  │
│  3. Remembered Farmer Context (Borewell limits, crop failures, preferences)  │
│  4. Farmer Query & Active Overrides                                         │
│                                                                             │
│  Execution: Azure OpenAI GPT-4o-mini (Temperature=0.7, Max Tokens=600)      │
│  Output: Personalized recommendation + Structured memory influence metadata  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Agricultural Ground Truth Layer

To prevent the LLM from hallucinating soil chemistry, planting dates, or market rates, Sarthi pre-ingests and normalizes official government datasets into a low-latency database layer:

| Domain | Source Authority | Records Ingested | Primary Ingestion Script | Serving Latency |
| :--- | :--- | :--- | :--- | :--- |
| **District Soil Baselines** | Soil Health Card Portal (DA&FW) | 702 Districts (pH, EC, OC, N, P, K, amendments) | [`ingestion/sync_soil.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/ingestion/sync_soil.py) | < 10ms |
| **Crop Science & Practices**| ICAR Research Institutes | 22 Master Crops (water, duration, soil tolerances) | [`ingestion/sync_crops.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/ingestion/sync_crops.py) | < 10ms |
| **Crop Calendar Operations**| CRIDA & State Agri Universities | 13 Multi-Season Schedules (Kharif, Rabi, Zaid) | [`ingestion/sync_calendar.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/ingestion/sync_calendar.py) | < 10ms |
| **APMC Mandi Rates** | Agmarknet & e-NAM (DMI) | Real-time APMC mandi modal, min, max prices | [`ingestion/sync_markets.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/ingestion/sync_markets.py) | < 10ms |
| **Agromet Advisories** | IMD Agromet Advisory Services | Active weather warnings, frost, humidity alerts | [`ingestion/sync_advisories.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/ingestion/sync_advisories.py) | < 10ms |

All data is served through [`backend/services/agri_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/agri_service.py) backed by Azure Table Storage (with automatic local SQLite fallback for offline development) and in-memory TTL caching.

---

## 3. Hindsight Long-Term Memory Service Layer

The Hindsight integration resides in [`backend/services/hindsight/`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/):

- **`config.py`**: Reads `HINDSIGHT_API_KEY`, `HINDSIGHT_BASE_URL`, and `HINDSIGHT_BANK_ID` from the environment. Gracefully flags unconfigured environments without crashing.
- **`client.py`**: Wraps the official `hindsight-client` Python SDK with timeout handling (30s), retry limits (3 attempts), credential masking, and thread-pool execution (`_run_coro`) to prevent event-loop collisions inside FastAPI async handlers.
- **`memory_types.py`**: Defines the 8-category taxonomy (`profile`, `preference`, `constraint`, `crop_history`, `recommendation`, `correction`, `outcome`, `incident`) and typed Pydantic models.
- **`memory_service.py`**: Provides the `FarmerMemoryService` domain class. Enforces farmer tenant isolation (`farmer:<phone_number>`), deduplicates writes via SHA-256 caching, runs secondary client-side isolation checks on recalled units, and compiles 4-section summary dashboards.
- **`recommendation_engine.py`**: Contains `MemoryAwareRecommender`. Implements decision-relevance gating (`is_memory_relevant_query`), targeted recall, the precedence policy (current query overriding stale memories), LLM prompt enrichment, structured influence generation, conversational learning extraction, and structured feedback processing.

For detailed documentation of the memory service, see [`docs/hindsight-memory.md`](hindsight-memory.md).

---

## 4. Multi-Tenant Security & Tenant Isolation

Agricultural data often contains sensitive operational and economic realities. Sarthi enforces three concentric layers of tenant isolation:

1. **Authentication Layer**: All memory-accessing endpoints require a valid JWT token. The farmer identity is extracted directly from the signed JWT payload (`current_user["phone_number"]`).
2. **Tag-Level Bank Partitioning**: Every memory unit in Hindsight is tagged with `farmer:<farmer_id>`. Recall queries include `tags=[f"farmer:{farmer_id}"]`.
3. **Application Verification Guard**: When candidate memories return from Hindsight, `FarmerMemoryService` verifies that each item's metadata `farmer_id` matches the authenticated caller. Any mismatched memory is discarded.

---

## 5. Resilience & Fault Tolerance

The platform is designed to degrade gracefully if any external dependency becomes unavailable:

| Component | Failure Mode | System Behavior |
| :--- | :--- | :--- |
| **Hindsight Memory Cloud** | Unreachable, rate-limited, or unconfigured | Retain operations return `success: false` (logged). Recall returns `[]`. Recommendation engine proceeds using authoritative government ground truth statelessly. |
| **Azure OpenAI** | Rate limit or transient error | Returns rule-based fallback advisory based on ingested Soil Health Card and ICAR crop compatibility. |
| **Azure Table Storage** | Network disconnection | Seamlessly falls back to local SQLite database populated during ingestion. |
| **Azure Speech / STT** | Audio decoding failure | Prompts user to re-record or submit text input. |

---

## 6. Official External Resources

- [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight)
- [Hindsight documentation](https://hindsight.vectorize.io/)
- [Vectorize's explanation of agent memory](https://vectorize.io/what-is-agent-memory)
