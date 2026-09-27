"""
Comprehensive Automated Tests for Gram Vaani Hindsight Memory Layer
Covers configuration, client robustness, memory models, farmer isolation,
graceful error handling, and mocked Hindsight API interactions.
"""

import pytest
from unittest.mock import MagicMock, patch

from services.hindsight import (
    HindsightConfig,
    get_hindsight_config,
    MemoryType,
    MemorySource,
    ProfileMemory,
    PreferenceMemory,
    ConstraintMemory,
    CropHistoryMemory,
    RecommendationMemory,
    CorrectionMemory,
    OutcomeMemory,
    IncidentMemory,
    HindsightClient,
    FarmerMemoryService,
)


# 1. Hindsight configuration loads correctly
def test_hindsight_config_loaded_with_values(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_API_KEY", "test-key-12345678")
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "https://api.test.hindsight.io")
    monkeypatch.setenv("HINDSIGHT_BANK_ID", "test-bank")
    monkeypatch.setenv("HINDSIGHT_TIMEOUT", "45.0")

    cfg = get_hindsight_config()
    assert cfg.is_configured is True
    assert cfg.api_key == "test-key-12345678"
    assert cfg.base_url == "https://api.test.hindsight.io"
    assert cfg.bank_id == "test-bank"
    assert cfg.timeout_seconds == 45.0
    assert "test-key" not in cfg.masked_api_key or "..." in cfg.masked_api_key


# 2. Missing API key is handled safely
def test_hindsight_config_missing_api_key(monkeypatch):
    monkeypatch.delenv("HINDSIGHT_API_KEY", raising=False)
    monkeypatch.setenv("HINDSIGHT_BASE_URL", "https://api.test.hindsight.io")

    cfg = get_hindsight_config()
    assert cfg.is_configured is False
    assert cfg.api_key is None

    client = HindsightClient(cfg)
    assert client.is_available is False
    health = client.health_check()
    assert health["status"] == "unconfigured"
    assert health["available"] is False


# 3. Hindsight client initializes correctly
def test_hindsight_client_init_success():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="my-bank",
    )
    with patch("hindsight_client.Hindsight") as mock_hindsight:
        client = HindsightClient(cfg)
        assert client.is_available is True
        mock_hindsight.assert_called_once_with(
            base_url="https://api.test.hindsight.io",
            api_key="test-key-9999",
            timeout=30.0,
            max_attempts=3,
        )


# 4 & 6 & 7 & 8: Retain request is correctly constructed with farmer identity, memory type, and metadata
def test_retain_request_construction():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="gramvaani",
    )
    mock_client = MagicMock(spec=HindsightClient)
    mock_client.retain.return_value = {"success": True, "retained": True}

    service = FarmerMemoryService(client=mock_client, config=cfg)
    result = service.retain_memory(
        farmer_id="9876543210",
        memory_type=MemoryType.CONSTRAINT,
        content="Irrigation is limited to 2 hours every 3 days.",
        metadata={"sub_region": "Mandal-B"},
        source=MemorySource.FARMER,
        crop="Cotton",
        location="Guntur, Andhra Pradesh",
        season="Kharif",
        confidence=0.95,
    )

    assert result["success"] is True
    mock_client.retain.assert_called_once()
    call_args = mock_client.retain.call_args[1]

    assert call_args["bank_id"] == "gramvaani"
    assert call_args["content"] == "Irrigation is limited to 2 hours every 3 days."
    
    # Metadata checks
    meta = call_args["metadata"]
    assert meta["farmer_id"] == "9876543210"
    assert meta["memory_type"] == "constraint"
    assert meta["source"] == "farmer"
    assert meta["crop"] == "Cotton"
    assert meta["location"] == "Guntur, Andhra Pradesh"
    assert meta["season"] == "Kharif"
    assert meta["confidence"] == "0.95"
    assert meta["sub_region"] == "Mandal-B"

    # Tags check (farmer isolation & classification)
    tags = call_args["tags"]
    assert "farmer:9876543210" in tags
    assert "type:constraint" in tags
    assert "source:farmer" in tags
    assert "crop:cotton" in tags


# 5. Recall request is correctly constructed
def test_recall_request_construction():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="gramvaani",
    )
    mock_client = MagicMock(spec=HindsightClient)
    mock_client.recall.return_value = [
        {
            "id": "mem_1",
            "text": "Irrigation is limited.",
            "tags": ["farmer:9876543210", "type:constraint"],
            "metadata": {"farmer_id": "9876543210"},
        }
    ]

    service = FarmerMemoryService(client=mock_client, config=cfg)
    results = service.recall_memories(
        farmer_id="9876543210",
        query="What is my irrigation situation?",
        memory_types=[MemoryType.CONSTRAINT],
        limit=5,
    )

    assert len(results) == 1
    assert results[0]["text"] == "Irrigation is limited."
    mock_client.recall.assert_called_once()
    call_args = mock_client.recall.call_args[1]

    assert call_args["bank_id"] == "gramvaani"
    assert call_args["query"] == "What is my irrigation situation?"
    assert "farmer:9876543210" in call_args["tags"]
    assert "type:constraint" in call_args["tags"]
    assert call_args["limit"] == 5


# 9. Hindsight API errors do not crash Gram Vaani
def test_api_errors_do_not_crash_service():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="gramvaani",
    )
    mock_client = MagicMock(spec=HindsightClient)
    mock_client.retain.side_effect = RuntimeError("Hindsight Cloud 503 Service Unavailable")
    mock_client.recall.side_effect = TimeoutError("Connection timed out after 30s")

    # In HindsightClient implementation, retain and recall catch exceptions and return fallbacks
    real_client = HindsightClient(cfg)
    real_client._raw_client = MagicMock()
    real_client._raw_client.retain.side_effect = Exception("Cloud rate limit exceeded (429)")
    real_client._raw_client.recall.side_effect = Exception("Network connection reset")

    service = FarmerMemoryService(client=real_client, config=cfg)

    # Retain must not crash
    retain_res = service.retain_memory(
        farmer_id="9876543210",
        memory_type=MemoryType.PREFERENCE,
        content="Prefers organic fertilizers",
    )
    assert retain_res["success"] is False
    assert "error" in retain_res

    # Recall must not crash, returns empty list
    recall_res = service.recall_memories(
        farmer_id="9876543210",
        query="organic fertilizer preference",
    )
    assert recall_res == []


# 10. Empty recall results are handled correctly
def test_empty_recall_results_handled():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="gramvaani",
    )
    mock_client = MagicMock(spec=HindsightClient)
    mock_client.recall.return_value = []

    service = FarmerMemoryService(client=mock_client, config=cfg)
    results = service.recall_memories(farmer_id="9876543210", query="nonexistent crop")
    assert isinstance(results, list)
    assert len(results) == 0


# 11. Memories belonging to Farmer A cannot be requested as Farmer B (isolation test)
def test_cross_farmer_isolation():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="gramvaani",
    )
    
    # Simulate an external response that maliciously or accidentally includes Farmer A's memory
    mock_client = MagicMock(spec=HindsightClient)
    mock_client.recall.return_value = [
        {
            "id": "mem_farmer_A",
            "text": "Farmer A has 5 acres of red soil.",
            "tags": ["farmer:farmer_A", "type:profile"],
            "metadata": {"farmer_id": "farmer_A"},
        },
        {
            "id": "mem_farmer_B",
            "text": "Farmer B has 2 acres of black soil.",
            "tags": ["farmer:farmer_B", "type:profile"],
            "metadata": {"farmer_id": "farmer_B"},
        },
    ]

    service = FarmerMemoryService(client=mock_client, config=cfg)

    # Farmer B queries memories
    results_farmer_B = service.recall_memories(farmer_id="farmer_B", query="tell me my land profile")

    # Farmer B MUST ONLY receive Farmer B's memory
    assert len(results_farmer_B) == 1
    assert results_farmer_B[0]["id"] == "mem_farmer_B"
    assert results_farmer_B[0]["text"] == "Farmer B has 2 acres of black soil."

    # Verify Farmer A's memory was completely excluded
    for item in results_farmer_B:
        assert item["metadata"]["farmer_id"] != "farmer_A"
        assert "farmer:farmer_A" not in item["tags"]


# 12. Correction memories can be represented
def test_correction_memory_representation():
    correction = CorrectionMemory(
        farmer_id="9876543210",
        previous_information="Reliable borewell irrigation",
        corrected_information="Borewell dried up; limited tanker water only",
    )

    content = correction.to_content()
    meta = correction.to_metadata()
    tags = correction.to_tags()

    assert "Correction by farmer" in content
    assert "Reliable borewell irrigation" in content
    assert "limited tanker water only" in content

    assert meta["farmer_id"] == "9876543210"
    assert meta["memory_type"] == "correction"
    assert meta["previous_info"] == "Reliable borewell irrigation"
    assert meta["corrected_info"] == "Borewell dried up; limited tanker water only"

    assert "farmer:9876543210" in tags
    assert "type:correction" in tags


# 13. Outcome memories can be represented
def test_outcome_memory_representation():
    outcome = OutcomeMemory(
        farmer_id="9876543210",
        related_recommendation="Apply neem oil spray for aphid control",
        result="success",
        reason="Aphid population reduced by 85% within 48 hours without burning foliage",
    )

    content = outcome.to_content()
    meta = outcome.to_metadata()
    tags = outcome.to_tags()

    assert "Outcome result: success" in content
    assert "neem oil spray" in content
    assert "Aphid population reduced" in content

    assert meta["farmer_id"] == "9876543210"
    assert meta["memory_type"] == "outcome"
    assert "farmer:9876543210" in tags
    assert "type:outcome" in tags


# 14. All 8 memory models instantiate and serialize cleanly
def test_all_eight_memory_taxonomy_models():
    fid = "test_farmer_999"

    models = [
        ProfileMemory(farmer_id=fid, fact="Farmer owns 3 acres.", farm_size="3 acres", soil_type="Black Cotton"),
        PreferenceMemory(farmer_id=fid, fact="Prefers drip-irrigated horticulture."),
        ConstraintMemory(farmer_id=fid, fact="Electricity available only 4 hours daily at night."),
        CropHistoryMemory(farmer_id=fid, crop="Chili", season="Kharif", outcome="failed", reason="Thrips infestation"),
        RecommendationMemory(farmer_id=fid, recommendation="Intercrop chili with marigold", reason="Repels nematodes"),
        CorrectionMemory(farmer_id=fid, previous_information="Has tractor", corrected_information="Hires bullocks only"),
        OutcomeMemory(farmer_id=fid, related_recommendation="Marigold border", result="success", reason="Lower pest count"),
        IncidentMemory(farmer_id=fid, incident_type="pest", crop="Chili", severity="high", description="Severe thrips flare-up"),
    ]

    expected_types = [
        MemoryType.PROFILE,
        MemoryType.PREFERENCE,
        MemoryType.CONSTRAINT,
        MemoryType.CROP_HISTORY,
        MemoryType.RECOMMENDATION,
        MemoryType.CORRECTION,
        MemoryType.OUTCOME,
        MemoryType.INCIDENT,
    ]

    for model, exp_type in zip(models, expected_types):
        assert model.memory_type == exp_type
        content = model.to_content()
        assert len(content) > 5
        meta = model.to_metadata()
        assert meta["farmer_id"] == fid
        assert meta["memory_type"] == exp_type.value
        tags = model.to_tags()
        assert f"farmer:{fid}" in tags
        assert f"type:{exp_type.value}" in tags


# 15. Credit-conscious deduplication
def test_credit_conscious_deduplication():
    cfg = HindsightConfig(
        api_key="test-key-9999",
        base_url="https://api.test.hindsight.io",
        bank_id="gramvaani",
    )
    mock_client = MagicMock(spec=HindsightClient)
    mock_client.retain.return_value = {"success": True, "retained": True}

    service = FarmerMemoryService(client=mock_client, config=cfg)

    # First write
    res1 = service.retain_memory("farmer_1", MemoryType.PREFERENCE, "Prefers low-cost seeds")
    assert res1["success"] is True
    assert res1["retained"] is True
    assert mock_client.retain.call_count == 1

    # Second write with identical content
    res2 = service.retain_memory("farmer_1", MemoryType.PREFERENCE, "Prefers low-cost seeds")
    assert res2["success"] is True
    assert res2["retained"] is False
    assert res2.get("deduplicated") is True
    # Client retain should NOT be called again
    assert mock_client.retain.call_count == 1

    # Different farmer with same content should NOT be blocked
    res3 = service.retain_memory("farmer_2", MemoryType.PREFERENCE, "Prefers low-cost seeds")
    assert res3["success"] is True
    assert res3["retained"] is True
    assert mock_client.retain.call_count == 2
