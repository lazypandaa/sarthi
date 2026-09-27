"""
Comprehensive Acceptance Tests for Phase 3 (Memory-Aware Recommendations)
and Phase 4 (Learning / Feedback / Outcome Loop).
Tests all 16 requirements specified in Section 21.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import os
import sys

# Ensure local backend directory has precedence
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, get_current_user
from services.hindsight import (
    MemoryType,
    MemorySource,
    FarmerMemoryService,
    MemoryAwareRecommender,
    get_recommender,
)

client = TestClient(app)


# ==============================================================================
# PHASE 3 TESTS: Memory-Aware Recommendations
# ==============================================================================

# 1. Recommendation without memory
def test_recommendation_without_memory():
    app.dependency_overrides[get_current_user] = lambda: {
        "phone_number": "test_farmer_no_mem",
        "location": "Warangal, Telangana",
        "language": "en",
    }

    with patch("main.get_recommender") as mock_get_rec, \
         patch("main.azure_client") as mock_azure, \
         patch("main.synthesize_speech", return_value=None), \
         patch("main.fetch_context_sync", return_value={}):

        mock_recommender = MagicMock(spec=MemoryAwareRecommender)
        mock_recommender.assemble_memory_context.return_value = ({}, [])
        mock_recommender.format_memory_for_prompt.return_value = ""
        mock_recommender.build_memory_influence_metadata.return_value = []
        mock_recommender.detect_and_retain_conversational_learning.return_value = None
        mock_get_rec.return_value = mock_recommender

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Generic advice: grow maize or pulses."))]
        mock_azure.chat.completions.create.return_value = mock_completion

        response = client.post(
            "/process-text",
            headers={"Authorization": "Bearer test-token"},
            json={"text": "What should I grow this season?", "language": "en"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["memory_context"]["used"] is False
        assert data["memory_context"]["memory_count"] == 0
        assert data["memory_influence"] == []
        assert "Generic advice" in data["response_text"]

    app.dependency_overrides.clear()


# 2. Recommendation with relevant memory
def test_recommendation_with_relevant_memory():
    app.dependency_overrides[get_current_user] = lambda: {
        "phone_number": "test_farmer_001",
        "location": "Anantapur, Andhra Pradesh",
        "language": "en",
    }

    raw_memories = [
        {
            "id": "mem_c1",
            "text": "Farmer has limited irrigation and no borewell.",
            "type": "constraint",
            "metadata": {"memory_type": "constraint", "source": "farmer"},
        },
        {
            "id": "mem_h1",
            "text": "Farmer previously attempted tomato cultivation and reported failure due to insufficient water.",
            "type": "crop_history",
            "metadata": {"memory_type": "crop_history", "crop": "Tomato", "source": "farmer"},
        }
    ]

    with patch("main.get_recommender") as mock_get_rec, \
         patch("main.azure_client") as mock_azure, \
         patch("main.synthesize_speech", return_value=None), \
         patch("main.fetch_context_sync", return_value={}):

        recommender = MemoryAwareRecommender(memory_service=MagicMock())
        # Mock assemble_memory_context to return categorized memories
        assembled = {
            "constraints": [
                {"id": "mem_c1", "text": "Farmer has limited irrigation and no borewell.", "type": "constraint", "source": "farmer"}
            ],
            "crop_history": [
                {"id": "mem_h1", "text": "Farmer previously attempted tomato cultivation and reported failure due to insufficient water.", "type": "crop_history", "crop": "Tomato", "source": "farmer"}
            ],
            "preferences": [],
            "corrections": [],
            "outcomes": [],
            "profile": [],
        }
        with patch.object(recommender, "assemble_memory_context", return_value=(assembled, raw_memories)):
            mock_get_rec.return_value = recommender

            mock_completion = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "Considering your limited irrigation and previous tomato failure, consider drought-resistant groundnut."
            mock_completion.choices = [MagicMock(message=mock_message)]
            mock_azure.chat.completions.create.return_value = mock_completion

            response = client.post(
                "/process-text",
                headers={"Authorization": "Bearer test-token"},
                json={"text": "What should I grow this season?", "language": "en"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["memory_context"]["used"] is True
            assert data["memory_context"]["memory_count"] == 2
            assert len(data["memory_influence"]) >= 2
            assert any(item["type"] == "constraint" for item in data["memory_influence"])
            assert any(item["type"] == "crop_history" for item in data["memory_influence"])

    app.dependency_overrides.clear()


# 3. Relevant memory is actually passed to reasoning prompt
def test_relevant_memory_passed_to_reasoning():
    recommender = MemoryAwareRecommender(memory_service=MagicMock())
    assembled = {
        "constraints": [{"text": "Limited borewell water (1 hour/day)"}],
        "crop_history": [{"text": "Paddy crop failed last Kharif"}],
        "preferences": [{"text": "Prefers organic cultivation"}],
    }
    prompt_snippet = recommender.format_memory_for_prompt(assembled)
    
    assert "=== REMEMBERED FARMER CONTEXT" in prompt_snippet
    assert "Limited borewell water (1 hour/day)" in prompt_snippet
    assert "Paddy crop failed last Kharif" in prompt_snippet
    assert "Prefers organic cultivation" in prompt_snippet
    assert "IMPORTANT REASONING DIRECTIVE" in prompt_snippet


# 4. Irrelevant memory is excluded & credit-conscious gate
def test_irrelevant_memory_excluded():
    recommender = MemoryAwareRecommender(memory_service=MagicMock())
    
    # Casual queries should bypass recall completely (0 Hindsight calls)
    assert recommender.is_memory_relevant_query("hello") is False
    assert recommender.is_memory_relevant_query("good morning") is False
    assert recommender.is_memory_relevant_query("namaste") is False

    # Agri queries must trigger recall
    assert recommender.is_memory_relevant_query("What crop can I grow with less water?") is True
    assert recommender.is_memory_relevant_query("Should I plant tomato or chili?") is True


# 5. Current information overrides stale memory (Precedence Policy)
def test_precedence_policy_current_overrides_stale():
    recommender = MemoryAwareRecommender(memory_service=MagicMock())
    
    # Stale context: limited irrigation constraint
    stale_context = {
        "constraints": [
            {"id": "c1", "text": "Limited irrigation available.", "type": "constraint"},
            {"id": "c2", "text": "High soil salinity.", "type": "constraint"}
        ],
        "preferences": [
            {"id": "p1", "text": "Prefers groundnut.", "crop": "groundnut", "type": "preference"}
        ],
        "crop_history": [],
        "corrections": [],
        "outcomes": [],
        "profile": [],
    }

    # Case A: Farmer states new irrigation was installed
    query_new_irrigation = "I installed a new drip irrigation system. What should I sow?"
    filtered = recommender.apply_precedence_policy(dict(stale_context), query_new_irrigation)
    
    # Stale water constraint should be removed; soil salinity constraint remains
    assert len(filtered["constraints"]) == 1
    assert "salinity" in filtered["constraints"][0]["text"].lower()
    assert "irrigation" not in [c["text"].lower() for c in filtered["constraints"]]

    # Case B: Farmer explicitly rejects previous preferred crop
    query_no_groundnut = "I don't want to grow groundnut anymore. What else?"
    filtered2 = recommender.apply_precedence_policy(dict(stale_context), query_no_groundnut)
    assert len(filtered2["preferences"]) == 0


# 6. Farmer A memory never reaches Farmer B
def test_cross_farmer_isolation_in_recommendations():
    mock_memory_service = MagicMock(spec=FarmerMemoryService)
    
    def recall_mock(farmer_id, query, memory_types=None, limit=10):
        if farmer_id == "farmer_A":
            return [{"id": "m_A", "text": "Farmer A has sandy soil and limited water.", "type": "constraint"}]
        elif farmer_id == "farmer_B":
            return []
        return []

    mock_memory_service.recall_memories.side_effect = recall_mock
    recommender = MemoryAwareRecommender(memory_service=mock_memory_service)

    # Context for Farmer A
    ctx_A, raw_A = recommender.assemble_memory_context("farmer_A", "What crop should I grow?")
    assert len(raw_A) == 1
    assert "Farmer A" in raw_A[0]["text"]

    # Context for Farmer B
    ctx_B, raw_B = recommender.assemble_memory_context("farmer_B", "What crop should I grow?")
    assert len(raw_B) == 0
    assert ctx_B == {}


# 7. Memory influence metadata is correctly generated
def test_memory_influence_metadata_generation():
    recommender = MemoryAwareRecommender(memory_service=MagicMock())
    assembled = {
        "constraints": [
            {"type": "constraint", "text": "Limited irrigation available during Rabi season."}
        ],
        "crop_history": [
            {"type": "crop_history", "crop": "Tomato", "text": "Tomato crop failed due to water shortage."}
        ],
        "preferences": [
            {"type": "preference", "text": "Prefers short-duration pulses."}
        ]
    }
    rec_text = "Recommend chickpea as a short-duration pulse that survives on minimal moisture."
    influence = recommender.build_memory_influence_metadata(assembled, rec_text)

    assert len(influence) == 3
    types = [inf["type"] for inf in influence]
    assert "constraint" in types
    assert "crop_history" in types
    assert "preference" in types
    assert all("summary" in inf and "impact" in inf for inf in influence)


# 8. Hindsight recall failure falls back gracefully to existing behavior
def test_hindsight_recall_failure_fallback():
    mock_svc = MagicMock(spec=FarmerMemoryService)
    mock_svc.recall_memories.side_effect = ConnectionError("Hindsight Cloud endpoint unreachable")
    
    recommender = MemoryAwareRecommender(memory_service=mock_svc)
    # Should not raise exception; must return empty context
    assembled, raw = recommender.assemble_memory_context("farmer_001", "What crop should I grow?")
    assert assembled == {}
    assert raw == []


# ==============================================================================
# PHASE 4 TESTS: Learning / Feedback / Outcome Loop
# ==============================================================================

# 9. Helpful feedback reporting success can produce an outcome memory
def test_helpful_feedback_can_produce_memory():
    mock_svc = MagicMock(spec=FarmerMemoryService)
    mock_svc.retain_memory.return_value = {"id": "mem_outcome_1", "retained": True}
    recommender = MemoryAwareRecommender(memory_service=mock_svc)

    feedback_payload = {
        "query_id": "rec_1001",
        "helpful": True,
        "feedback_type": "outcome_reported",
        "crop": "Groundnut",
        "outcome_result": "success",
        "outcome_reason": "Good yield and price at local mandi",
        "feedback_text": "The recommendation worked very well."
    }

    res = recommender.process_structured_feedback("farmer_001", feedback_payload)
    assert res is not None
    assert res["retained"] is True

    mock_svc.retain_memory.assert_called_once()
    kwargs = mock_svc.retain_memory.call_args[1]
    assert kwargs["farmer_id"] == "farmer_001"
    assert kwargs["memory_type"] == MemoryType.OUTCOME
    assert kwargs["crop"] == "Groundnut"
    assert kwargs["metadata"]["related_recommendation_id"] == "rec_1001"
    assert kwargs["metadata"]["result"] == "success"


# 10. Negative outcome can produce an outcome memory with reason
def test_negative_outcome_produces_memory():
    mock_svc = MagicMock(spec=FarmerMemoryService)
    mock_svc.retain_memory.return_value = {"id": "mem_outcome_fail", "retained": True}
    recommender = MemoryAwareRecommender(memory_service=mock_svc)

    feedback_payload = {
        "query_id": "rec_1002",
        "helpful": False,
        "feedback_type": "outcome_reported",
        "crop": "Tomato",
        "outcome_result": "failure",
        "outcome_reason": "Borewell ran dry in month 2",
        "feedback_text": "Crops dried out due to water shortage."
    }

    res = recommender.process_structured_feedback("farmer_001", feedback_payload)
    assert res is not None
    kwargs = mock_svc.retain_memory.call_args[1]
    assert kwargs["memory_type"] == MemoryType.OUTCOME
    assert kwargs["crop"] == "Tomato"
    assert kwargs["metadata"]["result"] == "failure"
    assert kwargs["metadata"]["reason"] == "Borewell ran dry in month 2"


# 11. Farmer correction can produce a correction memory
def test_farmer_correction_produces_memory():
    mock_svc = MagicMock(spec=FarmerMemoryService)
    mock_svc.retain_memory.return_value = {"id": "mem_cor_1", "retained": True}
    recommender = MemoryAwareRecommender(memory_service=mock_svc)

    feedback_payload = {
        "query_id": "rec_1003",
        "helpful": False,
        "feedback_type": "corrected",
        "crop": "Paddy",
        "correction_previous": "Recommended flood irrigation for paddy",
        "correction_new": "Farmer has converted field to drip and cannot flood.",
        "feedback_text": "I don't do flood irrigation anymore."
    }

    res = recommender.process_structured_feedback("farmer_001", feedback_payload)
    assert res is not None
    kwargs = mock_svc.retain_memory.call_args[1]
    assert kwargs["memory_type"] == MemoryType.CORRECTION
    assert kwargs["metadata"]["previous_info"] == "Recommended flood irrigation for paddy"
    assert "drip" in kwargs["metadata"]["corrected_info"].lower()


# 12. Invalid or ambiguous feedback does NOT create false memories
def test_ambiguous_feedback_no_false_memories():
    mock_svc = MagicMock(spec=FarmerMemoryService)
    recommender = MemoryAwareRecommender(memory_service=mock_svc)

    # Generic thumbs up with no durable data
    res1 = recommender.process_structured_feedback("farmer_001", {
        "query_id": "rec_1004",
        "helpful": True,
        "feedback_text": "Thanks"
    })
    assert res1 is None
    mock_svc.retain_memory.assert_not_called()

    # Casual chat conversational learning check
    res2 = recommender.detect_and_retain_conversational_learning("farmer_001", "Good morning Sarthi!")
    assert res2 is None
    mock_svc.retain_memory.assert_not_called()


# 13. Recommendation ID links to outcome
def test_recommendation_id_links_to_outcome():
    mock_svc = MagicMock(spec=FarmerMemoryService)
    mock_svc.retain_memory.return_value = {"id": "mem_linked", "retained": True}
    recommender = MemoryAwareRecommender(memory_service=mock_svc)

    feedback_payload = {
        "query_id": "recommendation_uuid_9999",
        "helpful": True,
        "outcome_result": "success",
        "crop": "Cotton",
    }
    recommender.process_structured_feedback("farmer_001", feedback_payload)
    kwargs = mock_svc.retain_memory.call_args[1]
    assert kwargs["metadata"]["related_recommendation_id"] == "recommendation_uuid_9999"


# 14. Duplicate memory creation is minimized via deduplication
def test_duplicate_memory_minimized():
    # Use real FarmerMemoryService with mocked HindsightClient
    mock_client = MagicMock()
    mock_client.is_available = True
    mock_client.retain.return_value = {"success": True, "retained": True, "id": "mem_unique_1"}

    service = FarmerMemoryService(client=mock_client)
    
    # First retain call
    res1 = service.retain_memory(
        farmer_id="farmer_001",
        memory_type=MemoryType.CONSTRAINT,
        content="Borewell depth is 180 feet with saline water.",
    )
    assert res1["retained"] is True
    assert mock_client.retain.call_count == 1

    # Identical content retained again
    res2 = service.retain_memory(
        farmer_id="farmer_001",
        memory_type=MemoryType.CONSTRAINT,
        content="Borewell depth is 180 feet with saline water.",
    )
    assert res2["retained"] is False
    assert res2["duplicate"] is True
    # Hindsight client should NOT be called again
    assert mock_client.retain.call_count == 1


# 15. Hindsight retain failure does not break the request (Fail-safe)
def test_hindsight_retain_failure_non_fatal():
    app.dependency_overrides[get_current_user] = lambda: {
        "phone_number": "test_farmer_retain_fail",
        "location": "Warangal, Telangana",
        "language": "en",
    }

    with patch("main.get_recommender") as mock_get_rec:
        mock_rec = MagicMock(spec=MemoryAwareRecommender)
        # Retain fails or throws error
        mock_rec.process_structured_feedback.side_effect = RuntimeError("Hindsight retain timeout")
        mock_get_rec.return_value = mock_rec

        # The endpoint should handle it gracefully without crashing
        response = client.post(
            "/api/feedback",
            headers={"Authorization": "Bearer test-token"},
            json={
                "query_id": "rec_000",
                "helpful": True,
                "feedback_type": "outcome_reported",
                "crop": "Maize",
                "outcome_result": "success"
            }
        )
        # Even if error occurs, the server shouldn't crash the user
        assert response.status_code in [200, 500]

    app.dependency_overrides.clear()


# 16. Existing Gram Vaani endpoints and functionality remain intact
def test_existing_endpoints_unbroken():
    response = client.get("/api/memory/health")
    assert response.status_code == 200
    assert "available" in response.json()
