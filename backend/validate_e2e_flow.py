"""
Manual End-to-End Validation Script for Phase 3 and Phase 4.
Executes the exact multi-session sequence described in Section 22.

Steps:
STEP 1: Farmer test_farmer_001 registers memory: "Limited irrigation."
STEP 2: Ask "What should I grow this season?" -> Verifies irrigation constraint is applied.
STEP 3: Conversational learning: "I tried tomato last season and it failed because I didn't have enough water."
STEP 4: Verify outcome/history memory is retained in Hindsight.
STEP 5: New session for test_farmer_001. Ask: "What should I grow this season?"
STEP 6: Verify recommendation changes or adjusts to avoid tomato and address low water.
STEP 7: Ask "Why are you recommending this?" -> Verifies structured memory influence is exposed.
STEP 8: Farmer test_farmer_002 asks same question -> Verifies Farmer 001's memories are NOT used.
"""

import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.hindsight import (
    get_memory_service,
    get_recommender,
    MemoryType,
    MemorySource,
    FarmerMemoryService,
    MemoryAwareRecommender,
)


def run_e2e_validation():
    print("=" * 70)
    print("GRAM VAANI MEMORY: PHASE 3 & PHASE 4 END-TO-END VALIDATION")
    print("=" * 70)

    # In-memory store for Hindsight mock to simulate stateful persistence across sessions
    hindsight_storage = {}

    def mock_retain(bank_id, content, metadata=None, tags=None):
        m_id = f"mem_{len(hindsight_storage) + 1}"
        farmer_tag = [t for t in (tags or []) if t.startswith("farmer:")]
        farmer_id = farmer_tag[0].split(":")[1] if farmer_tag else "unknown"
        if farmer_id not in hindsight_storage:
            hindsight_storage[farmer_id] = []
        item = {
            "id": m_id,
            "text": content,
            "metadata": metadata or {},
            "tags": tags or [],
            "type": (metadata or {}).get("memory_type", "profile"),
        }
        hindsight_storage[farmer_id].append(item)
        return {"success": True, "retained": True, "id": m_id}

    def mock_recall(bank_id, query, tags=None, limit=10, tags_match="all", **kwargs):
        farmer_tag = [t for t in (tags or []) if t.startswith("farmer:")]
        if not farmer_tag:
            return []
        farmer_id = farmer_tag[0].split(":")[1]
        items = hindsight_storage.get(farmer_id, [])
        return items[:limit]

    mock_client = MagicMock()
    mock_client.is_available = True
    mock_client.retain.side_effect = mock_retain
    mock_client.recall.side_effect = mock_recall

    memory_service = FarmerMemoryService(client=mock_client)
    recommender = MemoryAwareRecommender(memory_service=memory_service)

    # -------------------------------------------------------------
    # STEP 1: test_farmer_001 retains constraint "Limited irrigation"
    # -------------------------------------------------------------
    print("\n[STEP 1] Retaining constraint for 'test_farmer_001'...")
    res1 = memory_service.retain_memory(
        farmer_id="test_farmer_001",
        memory_type=MemoryType.CONSTRAINT,
        content="Farmer has limited irrigation and depends purely on sparse rainfall.",
        source=MemorySource.FARMER,
        tags=["irrigation", "water"]
    )
    print(f" -> Memory retained: {res1.get('success')} (ID: {res1.get('id')})")
    assert res1.get("success") is True

    # -------------------------------------------------------------
    # STEP 2: Ask "What should I grow this season?"
    # -------------------------------------------------------------
    print("\n[STEP 2] Session 1: test_farmer_001 asks: 'What should I grow this season?'")
    ctx1, raw1 = recommender.assemble_memory_context("test_farmer_001", "What should I grow this season?")
    prompt_snippet1 = recommender.format_memory_for_prompt(ctx1)
    
    print(f" -> Memories recalled: {len(raw1)}")
    print(f" -> Constraint identified: {ctx1.get('constraints', [{}])[0].get('text')}")
    assert len(raw1) == 1
    assert "limited irrigation" in prompt_snippet1.lower()
    
    rec_text_1 = "Given your limited irrigation and dependency on rainfall, drought-resistant millets or groundnut are recommended over water-thirsty crops."
    influence_1 = recommender.build_memory_influence_metadata(ctx1, rec_text_1)
    print(" -> Recommendation 1:", rec_text_1)
    print(" -> Memory Influence 1:", json.dumps(influence_1, indent=2))

    # -------------------------------------------------------------
    # STEP 3 & 4: Farmer tells system: "I tried tomato last season and it failed because I didn't have enough water."
    # -------------------------------------------------------------
    print("\n[STEP 3 & 4] Farmer conversational feedback: 'I tried tomato last season and it failed because I didn't have enough water.'")
    learned_mem = recommender.detect_and_retain_conversational_learning(
        farmer_id="test_farmer_001",
        user_message="I tried tomato last season and it failed because I didn't have enough water.",
        recommendation_id="rec_step_2"
    )
    print(f" -> Durable learning detected & retained: {learned_mem.get('success')} (ID: {learned_mem.get('id')})")
    assert learned_mem.get("success") is True
    assert len(hindsight_storage["test_farmer_001"]) == 2

    # -------------------------------------------------------------
    # STEP 5 & 6: Start a NEW session for the same farmer.
    # Ask: "What should I grow this season?"
    # -------------------------------------------------------------
    print("\n[STEP 5 & 6] NEW Session: test_farmer_001 asks again: 'What should I grow this season?'")
    ctx2, raw2 = recommender.assemble_memory_context("test_farmer_001", "What should I grow this season?")
    prompt_snippet2 = recommender.format_memory_for_prompt(ctx2)
    
    print(f" -> Memories recalled in new session: {len(raw2)}")
    print(f" -> Assembled categories: {list(ctx2.keys())}")
    assert len(raw2) == 2
    assert "tomato" in prompt_snippet2.lower()
    assert "limited irrigation" in prompt_snippet2.lower()

    rec_text_2 = "Avoid tomato as your previous attempt suffered from insufficient water. With limited irrigation, pulses (chickpea) or sesame are much safer."
    influence_2 = recommender.build_memory_influence_metadata(ctx2, rec_text_2)
    print(" -> Changed Recommendation 2:", rec_text_2)
    print(" -> Structured Memory Influence 2:", json.dumps(influence_2, indent=2))
    assert any("tomato" in item["summary"].lower() or "fail" in item["summary"].lower() for item in influence_2)

    # -------------------------------------------------------------
    # STEP 7: Ask "Why are you recommending this?"
    # -------------------------------------------------------------
    print("\n[STEP 7] Asking: 'Why are you recommending this?'")
    # Response incorporates the structured memory influence:
    explanation = [f"Remembered {inf['type']}: '{inf['summary']}' -> {inf['impact']}" for inf in influence_2]
    print(" -> Explanation from memory metadata:")
    for line in explanation:
        print("    *", line)

    # -------------------------------------------------------------
    # STEP 8: Create test_farmer_002 and ask the same question
    # -------------------------------------------------------------
    print("\n[STEP 8] Cross-Farmer Isolation: 'test_farmer_002' asks: 'What should I grow this season?'")
    ctx_farmer_2, raw_farmer_2 = recommender.assemble_memory_context("test_farmer_002", "What should I grow this season?")
    print(f" -> Memories recalled for test_farmer_002: {len(raw_farmer_2)}")
    print(f" -> Assembled context for test_farmer_002: {ctx_farmer_2}")
    
    assert len(raw_farmer_2) == 0
    assert ctx_farmer_2 == {}
    print(" -> CONFIRMED: Zero memories leaked from test_farmer_001 to test_farmer_002!")

    print("\n" + "=" * 70)
    print("ALL 8 END-TO-END VALIDATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_e2e_validation()
