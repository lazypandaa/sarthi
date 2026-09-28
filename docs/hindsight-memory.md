# Sarthi Long-Term Memory Engine: Hindsight Integration

This document provides a technical overview of how [Hindsight](https://github.com/vectorize-io/hindsight) is integrated into Sarthi to provide long-term, semantic memory for Indian smallholder farmers.

> **Publishing note**: When publishing the article and LinkedIn post, tag Code.in as required by the submission guide.

---

## 1. Why Hindsight Is Used

Standard agricultural chatbots operate statelessly: every session starts fresh, treating a returning farmer as a complete stranger. They forget critical farm realities such as:
- A borewell running dry by March
- Heavy soil salinity in a specific plot
- A devastating tomato wilt failure in the previous Kharif season
- An explicit decision to transition away from synthetic chemical inputs

While traditional Retrieval-Augmented Generation (RAG) retrieves static domain knowledge from documents (e.g., agronomy manuals, government advisories), it does not maintain an evolving, personal memory of the farmer across conversations and seasons.

Sarthi integrates [Hindsight](https://github.com/vectorize-io/hindsight) to provide an adaptive, long-term memory engine. Hindsight enables Sarthi to:
1. Retain durable facts, operational constraints, preferences, and verified harvest outcomes across sessions.
2. Recall relevant historical memories when agricultural decisions are made.
3. Apply a precedence policy so that recent farmer corrections supersede stale assumptions.
4. Close the feedback loop by turning post-harvest outcomes and farmer corrections into future memory.

For further background on memory architectures, refer to the official [Hindsight documentation](https://hindsight.vectorize.io/) and [Vectorize's explanation of agent memory](https://vectorize.io/what-is-agent-memory).

---

## 2. Farmer Namespace & Isolation Strategy

In a multi-tenant platform serving farmers across different districts and villages, strict memory isolation is essential:

- **Shared Memory Bank**: A single configured memory bank (`HINDSIGHT_BANK_ID="sarthi"`, default fallback `"sarthi"`) is maintained to avoid bank-per-user overhead while keeping tenant costs predictable.
- **Mandatory Namespace Tagging**: Every memory unit retained is tagged with `farmer:<farmer_id>`, where `farmer_id` is the authenticated farmer's canonical identity (phone number).
- **Recall Query Scoping**: All recall requests include `tags=[f"farmer:{farmer_id}"]` to restrict candidate retrieval to the requesting farmer.
- **Secondary Client-Side Isolation Guard**: Even after Hindsight executes retrieval, `FarmerMemoryService.recall_memories()` in [`backend/services/hindsight/memory_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_service.py) inspects the metadata and tags of every returned item. If an item's `farmer_id` does not match the requesting farmer, it is dropped and logged before returning.
- **JWT Identity Binding**: In the FastAPI endpoints ([`backend/main.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/main.py)), `farmer_id` is extracted strictly from the validated JWT token (`current_user["phone_number"]`), preventing callers from accessing or modifying another farmer's memory profile.

---

## 3. Authoritative 8-Part Memory Taxonomy

Sarthi does not store raw conversational filler or verbatim chat logs. Memory retention is strictly restricted to durable, structured facts classified under an 8-category taxonomy defined in [`backend/services/hindsight/memory_types.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_types.py):

| Category | Enum Value | Description | Typical Source |
| :--- | :--- | :--- | :--- |
| **Profile** | `profile` | Verified farm attributes (soil type, acreage, district, mandal, coordinates) | `farmer_profile`, `farmer` |
| **Preference** | `preference` | Cultivation preferences (e.g., low-water crops, organic methods, risk tolerance) | `farmer` |
| **Constraint** | `constraint` | Hard operational limits (e.g., borewell supplies water 1 hour/day, labor shortage) | `farmer` |
| **Crop History** | `crop_history` | Historical cultivation records, seasons, and realized outcomes | `farmer` |
| **Recommendation**| `recommendation`| Significant agricultural advice previously issued by the assistant | `assistant` |
| **Correction** | `correction` | Explicit corrections by the farmer overriding previous assumptions | `farmer` |
| **Outcome** | `outcome` | Realized harvest results, pest response, or economic yield from prior advice | `farmer` |
| **Incident** | `incident` | Unscheduled farm events (e.g., localized frost, hail damage, pest flare-up) | `farmer`, `system` |

---

## 4. Retain Flow

Information enters Hindsight through three distinct channels:

```
[ Channel 1: Direct Form / UI ]      [ Channel 2: Chat / Voice Message ]     [ Channel 3: Structured Feedback ]
  POST /api/memory/retain               POST /process-text or /process-audio     POST /api/feedback
            │                                         │                                    │
            ▼                                         ▼                                    ▼
FarmerMemoryService.retain_memory()    recommender.detect_and_retain_...       recommender.process_structured...
            │                                         │                                    │
            └─────────────────────────────────────────┼────────────────────────────────────┘
                                                      ▼
                                       FarmerMemoryService.retain_memory()
                                                      │
                                                      ├── Validate farmer_id & memory_type
                                                      ├── SHA-256 Deduplication Check
                                                      ├── Metadata Normalization
                                                      ├── Isolation Tags: [farmer:<id>, type:<type>]
                                                      ▼
                                              HindsightClient.retain()
                                                      │
                                                      ├── Thread-pool async runner (_run_coro)
                                                      └── Hindsight SDK aretain() / retain()
```

### Key Components:
- **`FarmerMemoryService.retain_memory()`** ([`backend/services/hindsight/memory_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_service.py)): Normalizes the farmer identifier, validates the memory type against the `MemoryType` enum, constructs normalized metadata (`farmer_id`, `memory_type`, `source`, `timestamp`, `confidence`, `crop`, `location`, `season`), and attaches isolation tags (`farmer:<id>`, `type:<type>`, `source:<source>`).
- **Conversational Learning Detection** ([`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py)): In `detect_and_retain_conversational_learning()`, natural language messages are analyzed using pattern extractors (`FAILURE_PATTERNS`, `SUCCESS_PATTERNS`, and constraint/preference cues). Non-factual statements, casual chitchat, and greetings are ignored.
- **Credit-Conscious Deduplication**: To preserve API credits, an in-memory `OrderedDict` tracks the SHA-256 hash of recent writes per farmer (`farmer_id:hash`). Identical facts submitted within the recent window are skipped locally without triggering an external API request.

---

## 5. Recall Flow

Memories are recalled when an agricultural decision requires historical context:

```
Farmer Query (e.g. "What should I grow this season?")
         │
         ▼
Decision Gate: recommender.is_memory_relevant_query(query)
         ├── False ──> Bypass recall (0 Hindsight calls)
         └── True
                 │
                 ▼
recommender.build_recall_query(query, location)
                 │
                 ▼
FarmerMemoryService.recall_memories(farmer_id, query, memory_types, limit=6)
                 │
                 ├── Set query tags: [f"farmer:{farmer_id}"]
                 ├── HindsightClient.recall(bank_id, query, tags, max_tokens=2048, budget="mid")
                 │
                 ▼
Secondary Client-Side Isolation Verification
                 ├── Drop items where metadata["farmer_id"] != requesting farmer
                 └── Filter by allowed memory_types
                 │
                 ▼
Assembled Memory Context: { constraints: [...], crop_history: [...], preferences: [...] }
```

### Key Components:
- **Credit-Conscious Relevance Gate**: Queries like `"hello"`, `"namaste"`, or general weather checks without crop decisions bypass recall entirely (`is_memory_relevant_query()` returns `False`).
- **Targeted Query Construction**: `build_recall_query()` extracts decision keywords (`crop`, `water`, `irrigation`, `season`) to construct a focused search query under 200 characters.
- **Token and Budget Bounds**: Recall calls specify `max_tokens=2048` and retrieval budget `"mid"` to prevent excessive token consumption.

---

## 6. Memory Integration into Recommendation Reasoning

Recalled memories are integrated into Azure OpenAI GPT-4o-mini reasoning using a multi-step pipeline in [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py):

### 1. Precedence Policy (`apply_precedence_policy`)
Before feeding memories to the LLM, the recommender checks if the farmer's current query contains an explicit update that overrides older memories:
- If a farmer states *"I installed a new drip irrigation system"*, stale constraints indicating *"limited irrigation"* or *"dry borewell"* are suppressed.
- If a farmer states *"I don't want to grow groundnut anymore"*, older preferences for groundnut are removed from the active context.

### 2. Prompt Formatting (`format_memory_for_prompt`)
The filtered memories are assembled into a structured prompt block:
```
=== REMEMBERED FARMER CONTEXT (from Hindsight Long-Term Memory) ===
Verified Farm Constraints:
  - [CONSTRAINT]: Farmer operational constraint: Borewell supplies water only 1 hour daily.

Past Crop Experience:
  - [PAST CROP HISTORY]: Farmer previously attempted Tomato cultivation and reported failure: Tomato crop failed due to insufficient irrigation.

IMPORTANT REASONING DIRECTIVE:
Weigh current external agricultural conditions together with these remembered farmer constraints/history.
If a crop is suitable under current season/weather but conflicts with a remembered constraint (e.g., limited irrigation) or previously failed due to that constraint, explicitly account for it in your recommendation and suggest realistic alternatives.
```

### 3. Memory Influence Metadata (`build_memory_influence_metadata`)
Alongside the natural language advice, the engine produces structured explanation metadata returned in the API response:
```json
[
  {
    "type": "constraint",
    "summary": "Farmer operational constraint: Borewell supplies water only 1 hour daily.",
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

## 7. Feedback and Outcomes Learning Loop

The feedback loop in `POST /api/feedback` allows real-world harvest results and corrections to become persistent memories:

1. **Outcome Reporting**: When a farmer reports harvest results (`outcome_result="success"` or `"failure"`, `outcome_reason`, `crop`), the system stores an `OutcomeMemory` tagged with the recommendation identifier (`related_recommendation_id`).
2. **Explicit Corrections**: When a farmer submits a correction (`correction_previous`, `correction_new`), a `CorrectionMemory` is created with `MemorySource.FARMER`.
3. **Actionable Negative Feedback**: When a farmer gives negative feedback explaining an operational limit (e.g., *"I cannot grow this because I do not have enough water"*), the engine classifies the feedback as a `ConstraintMemory`.

---

## 8. Graceful Fallback & Fault Tolerance

The integration is designed so that Hindsight outages never break core advisory functionality:

- **Unconfigured Mode**: If `HINDSIGHT_API_KEY` is not provided, `HindsightConfig.is_configured` evaluates to `False`. The client initializes in disabled fallback mode without throwing exceptions.
- **Non-Fatal Retain**: Retain operations catch all SDK and network exceptions, returning `{"success": False, "retained": False, "error": str(e)}`.
- **Non-Fatal Recall**: Recall operations catch exceptions and return an empty list `[]`. The recommendation engine falls back to standard regional agricultural data (soil baseline, ICAR practices, Agmarknet rates, IMD weather).
- **Masked Credentials**: The client logs status with `masked_api_key` (`xxxx...yyyy`), preventing credentials from appearing in application logs.

---

## 9. Verification & Automated Test Suite

The Hindsight integration is verified by 35 automated tests in `backend/tests/`:

1. **`tests/test_hindsight_memory.py`** (12 unit tests):
   - Configuration loading and missing key fallback
   - Client initialization and masked credential representation
   - Retain request construction, metadata, and tags
   - Recall request construction with farmer scoping
   - Error boundary resilience (no unhandled exceptions on network failure)
   - Cross-farmer memory isolation
   - Serialization of all 8 taxonomy models
   - SHA-256 deduplication cache behavior

2. **`tests/test_memory_api.py`** (4 integration tests):
   - `/api/memory/health` endpoint reporting
   - Unauthorized access prevention (401 without JWT)
   - Retain and recall authorization with JWT identity extraction

3. **`tests/test_phase3_phase4.py`** (16 end-to-end integration tests):
   - Recommendation generation with and without memory
   - Precedence policy (current query overriding stale constraint)
   - Cross-farmer isolation in recommendation contexts
   - Memory influence metadata generation
   - Feedback outcome retention and linkage to recommendation ID
   - Retain failure resilience

4. **`tests/test_hindsight_live.py`** (3 live integration tests):
   - Live Hindsight Cloud connectivity check
   - Live retain and multi-type recall validation
   - Live cross-farmer isolation verification against cloud backend

5. **`validate_e2e_flow.py`**:
   - Executes an 8-step multi-session sequence verifying constraint retention, recommendation adaptation, conversational failure learning, new session recall, influence explanation, and cross-farmer isolation.

---

## 10. Official External Resources

- [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight)
- [Hindsight documentation](https://hindsight.vectorize.io/)
- [Vectorize's explanation of agent memory](https://vectorize.io/what-is-agent-memory)
