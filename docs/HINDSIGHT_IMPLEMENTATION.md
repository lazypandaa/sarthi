# Gram Vaani Memory — Hindsight Integration (Phase 1 & Phase 2)

## 1. Why Hindsight Was Added

Standard agricultural chatbots operate statelessly: every session starts fresh, forgetting crucial farm-specific constraints (e.g., lack of borewell water, soil salinity, past crop failures, or specific budget limits). While traditional RAG retrieves static general agricultural knowledge from static documents, it does not maintain an evolving, personal memory of the farmer across conversations.

**Hindsight** was integrated into Gram Vaani to provide a long-term, semantic memory foundation. It allows the assistant to retain durable facts, constraints, preferences, and verified corrections across sessions, and recall them accurately when relevant.

---

## 2. What Information Gram Vaani Remembers

Gram Vaani does **not** store entire verbatim chat transcripts or transient conversational filler. It selectively retains structured, durable facts across eight clear categories:

1. **Profile**: Landholding size, soil type, district/mandal, preferred language.
2. **Preferences**: Low-water crop preferences, organic method choices, risk-tolerance indicators.
3. **Constraints**: Irrigation limits, power schedule constraints, financial or labor limitations.
4. **Crop History**: Prior seasons cultivated, past crop outcomes, and reasons for failure/success.
5. **Recommendations**: High-value previous agricultural advice provided by the system.
6. **Corrections**: Authoritative farmer corrections overriding previously inferred or outdated facts.
7. **Outcomes**: Realized yield, pest response, or harvest results tied to previous advice.
8. **Incidents**: Significant farm events (e.g., pest outbreak flare-ups, unseasonal rains, frost).

---

## 3. Memory Taxonomy

The taxonomy is codified in `backend/services/hindsight/memory_types.py`:

| Taxonomy Type | Enum Value | Description | Typical Source |
| :--- | :--- | :--- | :--- |
| **Profile** | `profile` | Verified farm attributes (soil, acreage, location) | `farmer_profile`, `farmer` |
| **Preference** | `preference` | Working preferences and inclinations | `farmer` |
| **Constraint** | `constraint` | Hard operational or environmental limits | `farmer` |
| **Crop History** | `crop_history` | Historical cultivation and season outcomes | `farmer` |
| **Recommendation** | `recommendation` | Significant advice given to the farmer | `assistant` |
| **Correction** | `correction` | Explicit corrections overriding old assumptions | `farmer` |
| **Outcome** | `outcome` | Verified results from prior recommendations | `farmer` |
| **Incident** | `incident` | Unscheduled farm events (pest, disease, storm) | `farmer`, `system` |

---

## 4. Farmer Isolation Strategy

In a multi-tenant application serving many farmers across different villages, **farmer memory isolation is critical**:
- **Shared Project Bank**: A single configured memory bank (e.g. `HINDSIGHT_BANK_ID="gramvaani"`) is maintained to avoid bank-per-user sprawl while keeping costs predictable.
- **Mandatory Namespace Tagging**: Every memory retained is tagged with `farmer:<farmer_id>` (where `farmer_id` is the authenticated phone number).
- **Enforced Recall Query Tags**: All recall queries automatically include `tags=[f"farmer:{farmer_id}"]` with `tags_match="all"`.
- **Secondary Client-Side Isolation Guard**: The `FarmerMemoryService` verifies that every item returned matches the requesting farmer's identity. Any memory belonging to another farmer is dropped before returning.
- **Auth Token Binding**: In API endpoints (`/api/memory/*`), `farmer_id` is extracted strictly from the validated JWT token (`current_user["phone_number"]`), preventing any farmer from requesting or tampering with another farmer's data.

---

## 5. Retain Flow

```
Farmer Action / Input
         │
         ▼
Extract Verified Fact & Category
         │
         ▼
FarmerMemoryService.retain_memory(...)
         │
         ├── Validate farmer_id & memory_type
         ├── Deduplication Check (skip if recently retained identical content)
         ├── Normalize Metadata (timestamp, source, crop, location, confidence)
         ├── Attach Isolation Tags (farmer:<id>, type:<type>, source:<source>)
         │
         ▼
HindsightClient.retain(...)
         │
         ├── Call Hindsight SDK (with timeout & retry limits)
         └── Graceful error handling (logs failure without crashing application)
```

---

## 6. Recall Flow

```
Recall Request (query, memory_types, limit)
         │
         ▼
FarmerMemoryService.recall_memories(...)
         │
         ├── Validate farmer_id
         ├── Assemble Required Tags ([f"farmer:{farmer_id}", f"type:{m_type}"])
         │
         ▼
HindsightClient.recall(...)
         │
         ├── Execute search with token limit & mid budget
         └── Return raw candidate results
         │
         ▼
Isolation Verification Filter
         ├── Verify metadata["farmer_id"] == requesting farmer
         └── Drop any mismatched memories
         │
         ▼
Structured Memory Results Returned
```

---

## 7. Error Handling & Resilience

- **Fail-Safe Design**: Hindsight failure never crashes Gram Vaani. If the Hindsight Cloud service is unavailable, unreachable, or rate-limited:
  - Errors are caught and logged with sanitized information (API keys are never printed).
  - Retain operations return `{"success": False, "retained": False, "error": ...}`.
  - Recall operations return `[]` (empty list), allowing the application to continue functioning statelessly.
- **Safe Initialization**: If `HINDSIGHT_API_KEY` is omitted, the service starts in `"unconfigured"` mode without raising exceptions.

---

## 8. Credit-Conscious Strategy

To conserve limited Hindsight Cloud credits:
1. **No Automatic Chat Retention**: Normal chat interactions are **not** retained verbatim. Only verified long-term facts are retained.
2. **In-Memory Write Deduplication**: The service tracks recent writes per farmer using SHA-256 content hashes. Repeated identical retain calls are deduplicated locally.
3. **Budget Caps**: Recall calls specify bounded token caps (`max_tokens=2048`) and a `"mid"` retrieval budget.
4. **No Automated Polling or Reflect**: Reflection and continuous background polling are intentionally omitted in this foundation phase.

---

---

## 10. Phase 3: Memory-Aware Recommendations Implementation

In Phase 3, Hindsight memories directly influence Gram Vaani's agricultural recommendation engine without altering existing agronomic intelligence or introducing extraneous vector databases:

### 1. Architectural Flow
```
Farmer Request
     │
     ▼
Credit-Conscious Gate (is_memory_relevant_query)
     │── [Not Decision-Relevant] ──> Standard Agri Reasoning (0 Hindsight calls)
     └── [Decision-Relevant]
              │
              ▼
     Targeted Recall (farmer_id, query)
              │
              ▼
     Taxonomy Categorization & Precedence Filter (apply_precedence_policy)
              │
              ▼
     Structured Prompt Enrichment (format_memory_for_prompt)
              │
              ▼
     Azure OpenAI Recommendation (GPT-4o-mini)
              │
              ▼
     Compute Memory Influence Metadata (build_memory_influence_metadata)
              │
              ▼
     Response with query_id, recommendation_id, memory_context, & memory_influence
```

### 2. Credit-Conscious Safeguards
- Non-agricultural queries (greetings, general conversation) bypass Hindsight completely (0 Recall calls).
- Agri-decision queries issue exactly **1** targeted recall capped at `limit=6`.
- Bounded token windows prevent unbounded memory injection.

### 3. Precedence Policy
Current verified farmer statements supersede stale memories before prompts are generated:
- If a farmer states *"I installed a new drip irrigation system"*, stale constraints stating *"Limited irrigation"* are suppressed.
- If a farmer states *"I don't want to grow groundnut anymore"*, stale preferences for groundnut are removed.

### 4. Structured Memory Influence Metadata
Every recommendation response exposes:
```json
{
  "recommendation_id": "rec_uuid",
  "memory_context": {
    "used": true,
    "memory_count": 2,
    "types": ["constraint", "crop_history"]
  },
  "memory_influence": [
    {
      "type": "constraint",
      "summary": "Farmer has limited irrigation",
      "impact": "Prioritized drought-tolerant / lower-water crops"
    },
    {
      "type": "crop_history",
      "summary": "Previous tomato crop failure",
      "impact": "Deprioritized tomato to avoid repeat failure"
    }
  ]
}
```

---

## 11. Phase 4: Learning / Feedback / Outcome Loop Implementation

Phase 4 closes the loop so that farmer experiences become future long-term memories:

### 1. Conversational Learning Detection
`recommender.detect_and_retain_conversational_learning(...)`:
- Extracts explicit past failures and successes from natural language messages (e.g. *"I tried tomato last season and it failed because I didn't have enough water"*).
- Detects newly disclosed hard constraints or explicit preferences.
- Rejects casual chitchat and non-factual statements.

### 2. Structured Feedback Endpoint (`POST /api/feedback`)
Supports structured outcomes and authoritative corrections:
- `outcome_reported`: Records `result` (`success` / `failure` / `partial`), `crop`, and `outcome_reason`.
- `corrected`: Records `previous_info` and `corrected_info` from the farmer.
- Links outcome memories directly to the generating recommendation via `related_recommendation_id`.

### 3. Anti-Pollution & Credit Consciousness
- SHA-256 deduplication cache prevents identical retain calls.
- Unverified outcomes and assistant-generated conjectures are never retained.

---

## 12. Phase 5: Memory & Reasoning UI Implementation

Phase 5 translates the Hindsight memory foundation into an intuitive, judge-impressing, and farmer-friendly user experience:

### 1. "What I Remember" Experience (`MemoryDashboard.jsx`)
Accessible directly from the navigation bar (🧠 **Memory**), the dashboard organizes stored knowledge into four human-understandable sections:
- **Farmer Profile**: Acreage, soil type, district/village, language.
- **Preferences**: Low-water crop preferences, organic cultivation choices, budget priorities.
- **Past Experience**: Historical crop varieties, past successes, recorded failures, and pest incidents.
- **Learned From You**: Authoritative corrections, operational constraints (e.g. borewell water limits), and verified harvest outcomes.
- **Interactive "Teach Agent"**: Allows farmers to type or dictate a new constraint or preference directly, immediately retaining it via `POST /api/memory/retain`.

### 2. Relevant Memory in Recommendations (`MemoryInfluenceCard.jsx`)
Directly beneath any agricultural advice (voice or text), a dedicated reasoning card reveals:
- **Influence Badge**: `🧠 Personalized using your past experience (X memories recalled)`.
- **"Based on what I remember"**: Bullet points showing the exact recalled constraints or crop histories.
- **"Why this recommendation?"**: Transparent explanation of how memories shaped the advice (e.g., *"Deprioritized Tomato to avoid repeat failure; prioritized drought-tolerant Groundnut"*).
- **Privacy Assurance**: Clear indicator that memories are private to the farmer's registered phone number.
- **Direct Correction Action**: Shortcut allowing farmers to correct or update any outdated remembered fact.

### 3. "How Advice Has Evolved" (What Changed?)
Provides a side-by-side view demonstrating how advice adapted over time when a farmer reported constraints or failures.

### 4. Enhanced Feedback & Outcome Modal (`EnhancedFeedbackModal.jsx`)
Upgrades the simple feedback dialog into a structured learning interface:
- **Helpful / Accepted** (👍 / 👎)
- **Correction** (✏️): Farmers can correct outdated assumptions.
- **Report Outcome** (🌾): Capture harvest outcomes (Success, Failure, Partial) and reasons (water, pests, mandi price), feeding directly into the Phase 4 loop.

---

## 13. Verification & Testing

- **Backend Automated Tests**: 32 unit and integration tests passing in `backend/tests/`:
  - `test_hindsight_memory.py`: 12 tests (config, models, isolation, client errors).
  - `test_memory_api.py`: 4 tests (auth, JWT farmer extraction, health).
  - `test_phase3_phase4.py`: 16 tests covering all acceptance criteria from Section 21.
- **Frontend Production Build**: `npm run build` succeeds cleanly with Vite v7 (0 lint/TypeScript/build errors).
- **Manual End-to-End Test**: `backend/validate_e2e_flow.py` confirms all 8 steps of the multi-session test scenario (Section 22).

