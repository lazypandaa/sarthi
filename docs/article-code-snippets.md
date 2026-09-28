# Sarthi Technical Article: Code Snippets

This document compiles small, verified code excerpts from the Sarthi codebase suitable for inclusion in the technical article. Each snippet illustrates a key architectural principle of long-term agent memory using [Hindsight](https://github.com/vectorize-io/hindsight).

> **Publishing note**: When publishing the article and LinkedIn post, tag Code.in as required by the submission guide.

---

## Snippet 1: The Precedence Policy (Current Facts Override Stale Memories)

- **File Path**: [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L181-L214)
- **Function**: `MemoryAwareRecommender.apply_precedence_policy()`
- **What It Demonstrates**: Dynamic suppression of outdated constraints when the farmer's current query indicates infrastructure improvements (e.g., installing drip irrigation).
- **Why It Matters to the Article**: Explains how agent memory avoids "stale context paralysis." Without precedence logic, an agent would perpetually believe a farmer has water shortages even after they install modern irrigation.

```python
def apply_precedence_policy(
    self,
    grouped: Dict[str, List[Dict[str, Any]]],
    current_query: str,
) -> Dict[str, List[Dict[str, Any]]]:
    """Ensures that current explicit statements override stale memories."""
    q_lower = current_query.lower()

    # Check for new irrigation override
    new_irrigation = bool(
        re.search(
            r"(?:installed|built|have|got|added|now\s+have)\s+(?:a\s+)?(?:new\s+)?(?:drip|borewell|sprinkler|irrigation|canal|solar\s+pump|water)",
            q_lower,
        )
    )
    if new_irrigation:
        # Demote or remove old water constraints
        grouped["constraints"] = [
            c for c in grouped["constraints"]
            if "irrigation" not in c["text"].lower() and "water" not in c["text"].lower()
        ]

    # Check for crop preference override (e.g. "I don't want to grow groundnut anymore")
    for pref in list(grouped["preferences"]):
        crop = pref.get("crop")
        if crop and re.search(rf"(?:don't|not|stop|no\s+longer).*?\b{crop.lower()}\b", q_lower):
            grouped["preferences"].remove(pref)

    return grouped
```

---

## Snippet 2: Memory Context Assembly for LLM Prompt Injection

- **File Path**: [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L215-L254)
- **Function**: `MemoryAwareRecommender.format_memory_for_prompt()`
- **What It Demonstrates**: Translating categorized memories into a clean, prioritized markdown block with explicit reasoning directives for Azure OpenAI GPT-4o-mini.
- **Why It Matters to the Article**: Bridges the gap between vector/semantic memory retrieval and generative reasoning. Shows readers exactly how [Hindsight](https://github.com/vectorize-io/hindsight) memories enter the LLM's system prompt.

```python
def format_memory_for_prompt(self, assembled_context: Dict[str, List[Dict[str, Any]]]) -> str:
    """Formats structured memories into a concise block for the LLM prompt."""
    if not assembled_context or not any(assembled_context.values()):
        return ""

    sections = []
    if assembled_context.get("constraints"):
        c_lines = [f"  - [CONSTRAINT]: {c['text']}" for c in assembled_context["constraints"]]
        sections.append("Verified Farm Constraints:\n" + "\n".join(c_lines))

    if assembled_context.get("crop_history"):
        h_lines = [f"  - [PAST CROP HISTORY]: {h['text']}" for h in assembled_context["crop_history"]]
        sections.append("Past Crop Experience:\n" + "\n".join(h_lines))

    header = "=== REMEMBERED FARMER CONTEXT (from Hindsight Long-Term Memory) ==="
    footer = (
        "IMPORTANT REASONING DIRECTIVE:\n"
        "Weigh current external agricultural conditions together with these remembered farmer constraints/history.\n"
        "If a crop is suitable under current season/weather but conflicts with a remembered constraint (e.g., limited irrigation) "
        "or previously failed due to that constraint, explicitly account for it in your recommendation and suggest realistic alternatives."
    )
    return f"\n{header}\n" + "\n\n".join(sections) + f"\n\n{footer}\n"
```

---

## Snippet 3: Conversational Learning Extraction (Natural Language to Durable Memory)

- **File Path**: [`backend/services/hindsight/recommendation_engine.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/recommendation_engine.py#L336-L379)
- **Function**: `MemoryAwareRecommender.detect_and_retain_conversational_learning()`
- **What It Demonstrates**: Automated extraction of harvest failures, affected crop entities, and underlying causes directly from user speech transcripts or chat text.
- **Why It Matters to the Article**: Illustrates that farmers do not need to fill out complex forms to train their agent. Casual voice or text messages naturally feed the long-term memory engine.

```python
# Detect explicit past failure with reason (Outcome / Crop History)
# e.g., "I tried tomato last season and it failed because I didn't have enough water"
for pattern in FAILURE_PATTERNS:
    match = re.search(pattern, msg_lower)
    if match:
        crop = None
        for c in ["tomato", "paddy", "cotton", "chili", "chilli", "groundnut", "maize", "soybean", "wheat", "onion"]:
            if c in msg_lower:
                crop = c.capitalize()
                break

        content = f"Farmer previously attempted {crop or 'crop'} cultivation and reported failure: {msg}."
        meta = {
            "source": MemorySource.FARMER.value,
            "outcome": "failed",
        }
        if crop:
            meta["crop"] = crop
        if recommendation_id:
            meta["related_recommendation_id"] = recommendation_id

        res = self.memory_service.retain_memory(
            farmer_id=farmer_id,
            memory_type=MemoryType.CROP_HISTORY,
            content=content,
            metadata=meta,
            crop=crop,
            source=MemorySource.FARMER,
        )
        return res
```

---

## Snippet 4: Dual-Layer Tenant Isolation Guard

- **File Path**: [`backend/services/hindsight/memory_service.py`](file:///Users/eshwarkrishna/Documents/Hack%20with%20HYD/gramvaani/backend/services/hindsight/memory_service.py#L240-L270)
- **Function**: `FarmerMemoryService.recall_memories()`
- **What It Demonstrates**: Application-side isolation verification that inspects every returned memory unit from Hindsight to prevent cross-tenant data leakage.
- **Why It Matters to the Article**: Emphasizes enterprise-grade data security in multi-tenant systems. While the vector bank is shared for cost efficiency, data access is strictly partitioned.

```python
# Secondary strict client-side isolation guard and taxonomy filter:
isolated_results: List[Dict[str, Any]] = []

for item in raw_results:
    item_tags = item.get("tags") or []
    item_meta = item.get("metadata") or {}

    meta_fid = item_meta.get("farmer_id")
    has_tag = expected_tag in item_tags
    
    # If tags or metadata exist, verify they match the requesting farmer
    if meta_fid and meta_fid != validated_farmer_id:
        logger.warning(
            f"Cross-farmer leak detected and blocked: memory belongs to '{meta_fid}', requested by '{validated_farmer_id}'"
        )
        continue
    
    if item_tags and not has_tag:
        other_farmer_tags = [t for t in item_tags if t.startswith("farmer:")]
        if other_farmer_tags and expected_tag not in other_farmer_tags:
            continue

    isolated_results.append(item)
    if len(isolated_results) >= limit:
        break

return isolated_results
```

---

## Official External Resources

- [Hindsight GitHub repository](https://github.com/vectorize-io/hindsight)
- [Hindsight documentation](https://hindsight.vectorize.io/)
- [Vectorize's explanation of agent memory](https://vectorize.io/what-is-agent-memory)
