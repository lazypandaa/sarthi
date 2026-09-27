"""
Real Live Integration Tests for Hindsight Cloud API.
These tests execute only when a valid HINDSIGHT_API_KEY is present in the environment.
They verify real cloud retain, real multi-type recall, tenant isolation,
dashboard summarization, and recommendation prompt injection.
"""

import os
import uuid
import pytest
from dotenv import load_dotenv

load_dotenv()

HINDSIGHT_KEY = os.getenv("HINDSIGHT_API_KEY")
IS_LIVE_CONFIGURED = bool(
    HINDSIGHT_KEY
    and HINDSIGHT_KEY.strip()
    and not HINDSIGHT_KEY.startswith("your-")
    and not HINDSIGHT_KEY.startswith("test-")
)

pytestmark = pytest.mark.skipif(
    not IS_LIVE_CONFIGURED,
    reason="Live HINDSIGHT_API_KEY is not configured. Skipping live cloud tests to protect CI."
)


@pytest.fixture(scope="module")
def memory_service():
    from services.hindsight import get_memory_service
    svc = get_memory_service()
    yield svc
    svc.close()


@pytest.fixture(scope="module")
def unique_farmer():
    return f"+9199999{uuid.uuid4().hex[:6]}"


def test_live_hindsight_connectivity(memory_service):
    """Verify live connectivity and version negotiation with Hindsight Cloud."""
    health = memory_service.health_check()
    assert health.get("status") in ["healthy", "ready"]
    assert health.get("available") is True
    assert "version" in health or "base_url" in health


def test_live_retain_and_multi_type_recall(memory_service, unique_farmer):
    """
    Verify real Hindsight Cloud Retain and multi-type Recall.
    Proves that a single recall request across multiple taxonomy types succeeds.
    """
    from services.hindsight import MemoryType

    # 1. Retain constraint
    r1 = memory_service.retain_memory(
        farmer_id=unique_farmer,
        memory_type=MemoryType.CONSTRAINT,
        content="Daily borewell limit is 1.5 hours in hot summer.",
        crop="chili",
        season="summer",
        skip_dedup=True,
    )
    assert r1.get("success") is True
    assert r1.get("retained") is True

    # 2. Retain crop history
    r2 = memory_service.retain_memory(
        farmer_id=unique_farmer,
        memory_type=MemoryType.CROP_HISTORY,
        content="Chili crop suffered severe leaf curl disease last season.",
        crop="chili",
        skip_dedup=True,
    )
    assert r2.get("success") is True
    assert r2.get("retained") is True

    # 3. Retain preference
    r3 = memory_service.retain_memory(
        farmer_id=unique_farmer,
        memory_type=MemoryType.PREFERENCE,
        content="Farmer prefers natural pest management and organic bio-fertilizers.",
        skip_dedup=True,
    )
    assert r3.get("success") is True
    assert r3.get("retained") is True

    # 4. Multi-type recall
    recalled = memory_service.recall_memories(
        farmer_id=unique_farmer,
        query="chili crop pest and borewell water",
        memory_types=[MemoryType.CONSTRAINT, MemoryType.CROP_HISTORY, MemoryType.PREFERENCE],
        limit=10,
    )

    assert len(recalled) > 0, "Multi-type recall must return memories from Hindsight Cloud"
    
    # Verify retrieved contents contain relevant facts
    combined_texts = " ".join(item.get("text", "") for item in recalled).lower()
    assert "borewell" in combined_texts or "water" in combined_texts or "chili" in combined_texts


def test_live_farmer_isolation(memory_service, unique_farmer):
    """
    Verify strict cross-farmer isolation against real Hindsight Cloud.
    Farmer B must receive ZERO memories belonging to Farmer A.
    """
    foreign_farmer = f"+9188888{uuid.uuid4().hex[:6]}"

    results = memory_service.recall_memories(
        farmer_id=foreign_farmer,
        query="borewell water irrigation chili crop",
        limit=10,
    )

    assert len(results) == 0, f"Foreign farmer {foreign_farmer} must receive zero memories of {unique_farmer}"


def test_live_dashboard_summary_unified_call(memory_service, unique_farmer):
    """
    Verify that get_farmer_memory_summary retrieves all categories
    and populates them accurately via a unified credit-conscious recall.
    """
    summary = memory_service.get_farmer_memory_summary(unique_farmer)

    assert summary.get("farmer_id") == unique_farmer
    assert summary.get("service_status", {}).get("available") is True
    assert summary.get("memory_count", 0) > 0
    assert summary.get("has_memory") is True

    sections = summary.get("sections", {})
    # Past experience or learned must have captured the earlier memories
    past_exp = sections.get("past_experience", [])
    learned = sections.get("learned_from_you", [])
    prefs = sections.get("preferences", [])

    total_section_items = len(past_exp) + len(learned) + len(prefs)
    assert total_section_items > 0, "Summary sections must be populated from live Hindsight memories"


def test_live_recommendation_memory_injection(unique_farmer):
    """
    Verify that the MemoryAwareRecommender retrieves memories from Hindsight
    and injects them into the prompt block.
    """
    from services.hindsight import get_recommender
    recommender = get_recommender()

    grouped, raw = recommender.assemble_memory_context(
        farmer_id=unique_farmer,
        query="What should I plant this season?",
    )

    assert len(raw) > 0, "assemble_memory_context must retrieve memories for this farmer"
    prompt_section = recommender.format_memory_for_prompt(grouped)

    assert "=== REMEMBERED FARMER CONTEXT" in prompt_section
    assert "IMPORTANT REASONING DIRECTIVE:" in prompt_section
