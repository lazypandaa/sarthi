#!/usr/bin/env python3
"""
Controlled Manual Validation Script for Gram Vaani Memory
Tests the exact scenario described in Section 9 of the specifications:
- test_farmer_001 retains constraint and preference
- test_farmer_001 recalls them
- test_farmer_002 attempts recall and verifies strict zero-leakage isolation
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.hindsight import (
    FarmerMemoryService,
    HindsightConfig,
    HindsightClient,
    MemoryType,
    get_hindsight_config,
)


def run_manual_validation(mock_mode_if_unconfigured: bool = True):
    print("=" * 60)
    print("🌾 GRAM VAANI MEMORY - CONTROLLED MANUAL VALIDATION")
    print("=" * 60)

    cfg = get_hindsight_config()
    print(f"Current Config: {cfg}")

    service = FarmerMemoryService(config=cfg)
    health = service.health_check()
    print(f"Health Check: {health}\n")

    # If unconfigured in local environment, set up an in-memory test double
    # to demonstrate the exact workflow end-to-end without failing.
    if not cfg.is_configured and mock_mode_if_unconfigured:
        print("ℹ️ Live Hindsight credentials not present in .env.")
        print("  Running with an isolated in-memory verification double to validate contract.\n")
        
        class MockHindsightClient(HindsightClient):
            def __init__(self):
                super().__init__(HindsightConfig(api_key="mock", base_url="http://mock", bank_id="gramvaani"))
                self._storage = []

            @property
            def is_available(self):
                return True

            def retain(self, bank_id, content, metadata=None, tags=None):
                self._storage.append({
                    "id": f"mem_{len(self._storage)+1}",
                    "text": content,
                    "metadata": metadata or {},
                    "tags": tags or [],
                })
                return {"success": True, "retained": True, "bank_id": bank_id}

            def recall(self, bank_id, query, tags=None, limit=10, tags_match="all"):
                tags = tags or []
                matched = []
                query_words = set(query.lower().split())
                for item in self._storage:
                    item_tags = set(item.get("tags", []))
                    if all(t in item_tags for t in tags):
                        # Simple keyword relevance score
                        text_words = set(item["text"].lower().split())
                        overlap = len(query_words.intersection(text_words))
                        matched.append((overlap, item))
                matched.sort(key=lambda x: x[0], reverse=True)
                return [m[1] for m in matched[:limit]]

        service = FarmerMemoryService(client=MockHindsightClient(), config=cfg)

    # --- Step 1: Farmer 001 retains constraint ---
    farmer_1 = "test_farmer_001"
    print(f"1. Retaining constraint for [{farmer_1}]:")
    print("   Fact: 'I have limited irrigation.'")
    res1 = service.retain_memory(
        farmer_id=farmer_1,
        memory_type=MemoryType.CONSTRAINT,
        content="I have limited irrigation.",
    )
    print(f"   Result: {res1}\n")

    # --- Step 2: Farmer 001 recalls irrigation situation ---
    print(f"2. Recalling irrigation situation for [{farmer_1}]:")
    print("   Query: 'What do you know about my irrigation situation?'")
    recall1 = service.recall_memories(
        farmer_id=farmer_1,
        query="What do you know about my irrigation situation?",
        memory_types=[MemoryType.CONSTRAINT],
    )
    print(f"   Recalled ({len(recall1)} item):")
    for r in recall1:
        print(f"   -> Text: '{r.get('text')}' | Tags: {r.get('tags')}")
    assert any("irrigation" in r.get("text", "").lower() for r in recall1), "Farmer 001 recall failed!"
    print("   ✓ Verified Farmer 001 successfully retrieved irrigation constraint.\n")

    # --- Step 3: Farmer 001 retains preference ---
    print(f"3. Retaining preference for [{farmer_1}]:")
    print("   Fact: 'I prefer lower-water crops.'")
    res2 = service.retain_memory(
        farmer_id=farmer_1,
        memory_type=MemoryType.PREFERENCE,
        content="I prefer lower-water crops.",
    )
    print(f"   Result: {res2}\n")

    # --- Step 4: Farmer 001 recalls crop-related preference ---
    print(f"4. Recalling crop preference for [{farmer_1}]:")
    print("   Query: 'What crop-related preference do you remember?'")
    recall2 = service.recall_memories(
        farmer_id=farmer_1,
        query="What crop-related preference do you remember?",
        memory_types=[MemoryType.PREFERENCE],
    )
    print(f"   Recalled ({len(recall2)} item):")
    for r in recall2:
        print(f"   -> Text: '{r.get('text')}' | Tags: {r.get('tags')}")
    assert any("lower-water" in r.get("text", "").lower() for r in recall2), "Farmer 001 preference recall failed!"
    print("   ✓ Verified Farmer 001 successfully retrieved crop preference.\n")

    # --- Step 5: Critical Cross-Farmer Isolation Test ---
    farmer_2 = "test_farmer_002"
    print(f"5. Cross-Farmer Isolation Test with [{farmer_2}]:")
    print(f"   Querying [{farmer_2}] for irrigation and crop preference...")
    leak_check_1 = service.recall_memories(farmer_id=farmer_2, query="What is my irrigation situation?")
    leak_check_2 = service.recall_memories(farmer_id=farmer_2, query="What crop-related preference do you remember?")
    print(f"   Items returned for [{farmer_2}] query 1: {len(leak_check_1)}")
    print(f"   Items returned for [{farmer_2}] query 2: {len(leak_check_2)}")

    assert len(leak_check_1) == 0, f"Isolation failure! Farmer 2 received: {leak_check_1}"
    assert len(leak_check_2) == 0, f"Isolation failure! Farmer 2 received: {leak_check_2}"
    print(f"   ✓ CRITICAL ISOLATION VERIFIED: [{farmer_2}] cannot access any memories belonging to [{farmer_1}].\n")

    print("=" * 60)
    print("🎉 ALL MANUAL VALIDATION CHECKS PASSED PERFECTLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_manual_validation()
