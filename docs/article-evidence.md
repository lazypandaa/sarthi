# Article Evidence: Technical Foundation for Sarthi & Hindsight

This document compiles verified facts, architecture details, code locations, and empirical test results from the Sarthi codebase to support generating the final technical article.

> **Publishing note**: When publishing the article and LinkedIn post, tag Code.in as required by the submission guide.

---

## Project Summary

**Sarthi** is an agricultural advisory platform designed for smallholder farmers in India. It pairs authoritative agronomic ground truth—ingested from verified Government of India datasets (Soil Health Card portal, ICAR crop practices, Agmarknet mandi rates, and IMD Agromet weather advisories)—with persistent long-term semantic memory powered by [Hindsight](https://github.com/vectorize-io/hindsight).

By retaining operational constraints, past harvest outcomes, and farmer corrections across seasons, Sarthi prevents generic advice from repeating past crop failures.

---

## The Core Problem

Conventional agricultural chatbots operate statelessly. In every new conversation or season, the assistant starts with zero personal context about the farm:
1. **Loss of Farm Constraints**: The system forgets that a farmer's borewell yields water for only one hour daily, that their soil has high salinity, or that they lack working capital for chemical inputs.
2. **Repeated Advisory Failures**: When a recommended crop fails due to unseasonal rain or localized pest infestation, the stateless assistant has no recollection of the event and repeats the exact same recommendation in the subsequent season.
3. **Absence of a Learning Loop**: Post-harvest feedback and farmer-provided corrections are discarded after the session terminates, leaving no mechanism for the assistant to adapt over time.

---

## Hindsight Integration

The integration is implemented in the Python backend under [`backend/services/hindsight/`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/):

| File Path | Primary Classes / Functions | Responsibility |
| :--- | :--- | :--- |
| `backend/services/hindsight/config.py` | `HindsightConfig`, `get_hindsight_config()` | Loads configuration from environment variables (`HINDSIGHT_API_KEY`, `HINDSIGHT_BASE_URL`, `HINDSIGHT_BANK_ID`, `HINDSIGHT_TIMEOUT`). Safely masks keys for logging. |
| `backend/services/hindsight/client.py` | `HindsightClient` | Wraps official `hindsight-client` SDK. Implements `_run_coro()` thread-pool executor for asyncio safety, 30s timeout, retry limits (3 attempts), and fallback error isolation. |
| `backend/services/hindsight/memory_types.py` | `MemoryType`, `MemorySource`, `BaseMemoryModel`, `ProfileMemory`, `ConstraintMemory`, `CropHistoryMemory`, `OutcomeMemory`, `CorrectionMemory`, `PreferenceMemory`, `RecommendationMemory`, `IncidentMemory` | Implements 8-category taxonomy models, metadata converters, and tag generators. |
| `backend/services/hindsight/memory_service.py` | `FarmerMemoryService`, `get_memory_service()` | Manages tenant isolation (`farmer:<phone_number>`), SHA-256 deduplication cache (500 entries), retain and recall operations, client-side cross-tenant leakage guards, and 4-section summary compilation. |
| `backend/services/hindsight/recommendation_engine.py`| `MemoryAwareRecommender`, `get_recommender()` | Coordinates decision-relevance gating (`is_memory_relevant_query`), targeted recall, precedence policy enforcement (`apply_precedence_policy`), LLM prompt assembly (`format_memory_for_prompt`), memory influence metadata generation (`build_memory_influence_metadata`), conversational learning detection (`detect_and_retain_conversational_learning`), and structured feedback retention (`process_structured_feedback`). |
| `backend/main.py` | FastAPI route handlers | Endpoints: `GET /api/memory/health`, `POST /api/memory/retain`, `POST /api/memory/recall`, `GET /api/memory/summary`, `POST /api/recommendation`, `POST /api/memory/compare`, `POST /api/memory/demo/reset`, `POST /process-text`, `POST /process-audio`, `POST /api/feedback`. |

---

## Retain Flow

Information enters Hindsight memory through three specific paths:

1. **Conversational Extraction**:
   - Location: `MemoryAwareRecommender.detect_and_retain_conversational_learning()` in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L317-L456).
   - Triggered by: `POST /process-text` or `POST /process-audio` in [`backend/main.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/main.py).
   - Logic: Analyzes incoming user messages using regular expressions (`FAILURE_PATTERNS`, `SUCCESS_PATTERNS`, and constraint phrases). When a farmer states *"I tried tomato last season and it failed because I didn't have enough water"*, the method automatically extracts `crop="Tomato"`, `outcome="failed"`, and retains a `CropHistoryMemory` unit.

2. **Structured Feedback & Outcome Submission**:
   - Location: `MemoryAwareRecommender.process_structured_feedback()` in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L457-L540).
   - Triggered by: `POST /api/feedback` in [`backend/main.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/main.py).
   - Logic: Retains `OutcomeMemory` (result, crop, reason) or `CorrectionMemory` (previous info, corrected info) linked to `related_recommendation_id`.

3. **Direct Farmer Teaching**:
   - Location: `FarmerMemoryService.retain_memory()` in [`backend/services/hindsight/memory_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_service.py#L79-L170).
   - Triggered by: `POST /api/memory/retain` in [`backend/main.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/main.py).
   - Deduplication: An in-memory SHA-256 hash table (`_recent_writes`) verifies whether identical content was recently written for that farmer. If a duplicate is detected, write is skipped locally to conserve API credits.

---

## Recall Flow

Memories are recalled when the farmer asks a decision-oriented question:

1. **Credit-Conscious Relevance Gate**:
   - Location: `MemoryAwareRecommender.is_memory_relevant_query()` in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L70-L86).
   - Checks if query contains agricultural decision terms (`AGRI_DECISION_KEYWORDS`). Greetings and generic queries return `False` and bypass Hindsight entirely (0 API calls).

2. **Query Assembly & Scoped Recall**:
   - Location: `FarmerMemoryService.recall_memories()` in [`backend/services/hindsight/memory_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_service.py#L191-L281).
   - Issues a recall request to the shared bank `sarthi` with tags `[f"farmer:{farmer_id}"]`, `max_tokens=2048`, and `budget="mid"`, capped at `limit=6`.

3. **Client-Side Cross-Tenant Isolation Filter**:
   - Location: Lines 242–279 of `memory_service.py`.
   - Iterates through candidate results returned by Hindsight. If an item contains metadata or tags belonging to a different `farmer_id`, it is dropped and a security warning is logged.

---

## Recommendation Flow

1. **Precedence Policy**:
   - Location: `MemoryAwareRecommender.apply_precedence_policy()` in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L181-L214).
   - Suppresses stale memories when current user statements supersede them. For example, if a remembered constraint says *"limited irrigation"*, but the current query indicates *"I installed a new drip irrigation system"*, the stale constraint is removed from the active context.

2. **Prompt Composition**:
   - Location: `MemoryAwareRecommender.format_memory_for_prompt()` in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L215-L254).
   - Formats remembered constraints, crop histories, preferences, and profiles into a structured prompt section with reasoning instructions.

3. **LLM Execution**:
   - Executed via Azure OpenAI GPT-4o-mini (`backend/main.py#L2242-L2256`).
   - Merges the formatted memory section with authoritative government ground truth (district soil chemistry, ICAR guidelines, mandi prices, and weather).

4. **Structured Influence Metadata**:
   - Location: `MemoryAwareRecommender.build_memory_influence_metadata()` in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L255-L316).
   - Generates explicit pairs detailing each memory type, summary, and its exact impact on the recommendation (e.g., *"Deprioritized Tomato and recommended alternatives to avoid repeat failure"*).

---

## Memory Types

Only 8 memory types are codified in [`backend/services/hindsight/memory_types.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_types.py):
1. `profile`: Verified soil type, acreage, district, location.
2. `preference`: Low-water crop preference, organic farming preference.
3. `constraint`: Irrigation limitation (e.g., borewell runs 1 hour/day), power availability.
4. `crop_history`: Cultivation history, season, historical yield, failure reasons.
5. `recommendation`: Record of previous system advice.
6. `correction`: Farmer corrections overriding prior system assumptions.
7. `outcome`: Verified harvest results tied to previous advice.
8. `incident`: Frost damage, pest outbreaks, localized weather events.

---

## Farmer Isolation

- **Namespace Tagging**: Every stored memory unit is tagged with `farmer:<farmer_id>` (phone number).
- **Enforced Query Scoping**: Every recall call explicitly queries with `tags=[f"farmer:{farmer_id}"]`.
- **Dual-Verification Guard**: Returned memories are inspected by `FarmerMemoryService.recall_memories()`. If `metadata["farmer_id"]` does not match the requester, the memory is discarded.
- **Authentication**: JWT authentication in `backend/main.py` extracts the farmer's identity directly from the token, preventing unauthorized access to other tenants.

---

## Feedback and Outcomes

- Handled by `POST /api/feedback` in [`backend/main.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/main.py#L1103-L1145) calling `recommender.process_structured_feedback()`.
- Captures harvest results (`outcome_result="success" | "failure" | "partial"`), reasons (`outcome_reason`), and notes (`feedback_text`), linking them directly to `related_recommendation_id`.
- Actionable negative feedback explaining constraints (e.g., *"Cannot grow tomato due to lack of water"*) is stored as a `ConstraintMemory`.

---

## Corrections

- Supported via `correction_new` and `correction_previous` fields in `POST /api/feedback`.
- Stored as `MemoryType.CORRECTION` with `MemorySource.FARMER`.
- Conversational overrides are detected in `apply_precedence_policy()`, dynamically filtering out stale assumptions during subsequent reasoning sessions.

---

## Memory Visibility

- **Memory Dashboard** (`frontend/src/App.tsx#L870-L895`): Displays four distinct sections:
  1. *Farm Profile* (soil, landholding, village)
  2. *Working Preferences* (crop preferences, organic inputs)
  3. *Past Experience* (historical crop outcomes, failure notes)
  4. *Learned From You* (operational constraints, water limits, corrections)
- **Evolution Timeline** (`what_changed`): Shows triggers, recorded memories, and system adaptation notes.
- **Recommendation Influence Card**: Displays a badge indicating memories used and includes an expandable "Why this recommendation?" section.
- **Teach Sarthi Modal**: Farmers can directly submit new constraints, water observations, or crop preferences.

---

## Failure Handling

- If Hindsight Cloud is unreachable, unconfigured, or rate-limited:
  - `HindsightClient.retain()` catches exceptions and returns `{"success": False, "retained": False, "error": ...}`.
  - `HindsightClient.recall()` catches exceptions and returns `[]`.
  - The recommendation engine falls back gracefully to standard agricultural context without throwing errors or breaking the user experience.

---

## Testing Evidence

The repository contains 51 automated tests in `backend/tests/`, all passing (100% success rate):

- `tests/test_hindsight_memory.py` (12 tests): Validates configuration loading, client initialization, request serialization, isolation tags, taxonomy models, deduplication caching, and exception handling.
- `tests/test_memory_api.py` (4 tests): Validates JWT authorization and memory endpoints.
- `tests/test_phase3_phase4.py` (16 tests): Validates recommendation without memory, recommendation with memory, precedence policy, memory influence metadata, conversational learning detection, feedback outcome retention, and graceful fallback.
- `tests/test_hindsight_live.py` (3 tests): Validates live connectivity, retain/recall, and isolation against Hindsight Cloud.
- `tests/test_agri_recovery.py` (14 tests): Validates ground truth retrieval across 702 districts.
- `tests/test_auth_azure_tables.py` (2 tests): Validates user authentication flows.

Additionally:
- `backend/validate_e2e_flow.py`: Standalone script running an 8-step multi-session simulation. Confirms zero memory leakage between farmers and verified recommendation evolution.
- `frontend/`: `npm run build` succeeds cleanly with zero TypeScript or Vite build errors.

---

## Concrete Before/After Example

This scenario is directly supported and validated by `backend/validate_e2e_flow.py` and `tests/test_phase3_phase4.py`:

### Before Memory (Stateless Mode):
- **Farmer Query**: *"What should I grow this season?"* (Location: Anantapur, Andhra Pradesh; Kharif season; red sandy loam soil).
- **System Recommendation**:
  > *"Based on regional soil and current Kharif weather, recommended crops include Groundnut, Cotton, and Tomato. Tomato offers high market value in local APMC mandis."*
- **Outcome in Field**: The farmer attempts Tomato, but their borewell runs dry, leading to total crop failure.

### After Memory (Hindsight Long-Term Memory Active):
- **Farmer Reports Failure**: *"I tried tomato last season and it failed because I didn't have enough water. My borewell only runs for one hour a day."*
- **Hindsight Retain**:
  - `ConstraintMemory`: *"Farmer operational constraint: Borewell only runs for one hour a day."*
  - `CropHistoryMemory`: *"Farmer previously attempted Tomato cultivation and reported failure: insufficient water."*
- **Next Season Query**: *"What should I grow this season?"*
- **Hindsight Recall**: Both the water limitation and the previous tomato failure are retrieved and injected into the prompt.
- **System Recommendation**:
  > *"Avoid Tomato. Your previous crop suffered total loss due to water shortage, and your borewell supplies water for only one hour daily. Instead, prioritize drought-tolerant crops like Pearl Millet (Bajra) or early-maturing Groundnut, which match your red soil and limited water availability."*
- **Memory Influence Metadata**:
  ```json
  [
    {
      "type": "constraint",
      "summary": "Farmer operational constraint: Borewell only runs for one hour a day.",
      "impact": "Prioritized drought-tolerant / lower-water crops and warned against high-water options."
    },
    {
      "type": "crop_history",
      "summary": "Farmer previously attempted Tomato cultivation and reported failure...",
      "impact": "Deprioritized Tomato and recommended alternatives to avoid repeat failure."
    }
  ]
  ```

---

## Engineering Lessons

1. **Asyncio Event Loop Concurrency**: The official Hindsight SDK provides both synchronous (`retain`) and asynchronous (`aretain`) methods. Inside FastAPI async route handlers, calling synchronous SDK methods can result in event loop conflicts. Sarthi resolved this by implementing `_run_coro()` in `client.py`, which executes async SDK calls inside an isolated thread pool worker.
2. **Selective Tag Filtering vs. Multi-Tag Collisions**: In Hindsight, querying with multiple taxonomy tags using `tags_match="all"` returns zero results because a single memory unit belongs to only one category (e.g., `type:constraint`). Sarthi solved this by querying Hindsight with the mandatory tenant tag (`farmer:<farmer_id>`) and performing secondary taxonomy filtering in application code.
3. **Credit Conservation in Agent Memory**: Unrestricted retain and recall calls in conversational loops can quickly deplete API credits. Implementing an in-memory SHA-256 deduplication cache and a decision-relevance keyword gate reduced redundant API calls significantly.
4. **Precedence Over Accumulation**: Agent memory cannot simply accumulate facts monotonically. When a farmer upgrades infrastructure (e.g., installs drip irrigation), old constraints must be actively superseded during reasoning.

---

## Honest Limitation / Debugging Story

### The Tag Collision Challenge in Multi-Type Recall
During initial integration of the Hindsight recall API, Sarthi attempted to retrieve multiple memory types simultaneously by passing tags such as `["farmer:+919999999001", "type:constraint", "type:crop_history"]` with `tags_match="all"`.

Because each retained document in Hindsight only had a single `type:` tag attached, requiring *all* tags to match caused Hindsight to return an empty array (`[]`), effectively blinding the recommendation engine to existing memories. Conversely, using `tags_match="any"` without a mandatory farmer filter risked retrieving memories from other farmers that shared the same `type:constraint` tag.

**Solution Implemented**:
In [`backend/services/hindsight/memory_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_service.py#L208-L240), Sarthi restructured the query:
1. Always scope the Hindsight query strictly to `farmer:<farmer_id>`.
2. When multiple memory categories are requested, query by the farmer tag alone with an expanded candidate limit (`limit_to_send = max(limit * 3, 25)`).
3. Perform taxonomy categorization and multi-type filtering in application code.
4. Enforce a secondary client-side isolation check to ensure that no cross-tenant memory ever reaches the recommendation prompt.

---

## Required External Resources

- [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight)
- [Hindsight documentation](https://hindsight.vectorize.io/)
- [Vectorize's explanation of agent memory](https://vectorize.io/what-is-agent-memory)
