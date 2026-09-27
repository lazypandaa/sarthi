"""
API Integration Tests for Memory Endpoints in main.py
Tests authentication integration, JWT extraction of farmer identity,
and route-level error boundaries.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import os
import sys

# Ensure local backend directory has precedence over outer repositories
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from main import app, get_current_user
from services.hindsight import MemoryType, FarmerMemoryService

client = TestClient(app)


def test_memory_health_endpoint():
    response = client.get("/api/memory/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "available" in data


def test_memory_retain_unauthorized():
    response = client.post(
        "/api/memory/retain",
        json={"memory_type": "constraint", "content": "Water is scarce"},
    )
    assert response.status_code == 401 or response.status_code == 403


def test_memory_retain_authorized():
    app.dependency_overrides[get_current_user] = lambda: {
        "phone_number": "9000011111",
        "location": "Guntur, Andhra Pradesh",
        "language": "te",
    }
    
    with patch("main.get_memory_service") as mock_get_svc:
        mock_svc = MagicMock(spec=FarmerMemoryService)
        mock_svc.retain_memory.return_value = {"success": True, "retained": True}
        mock_get_svc.return_value = mock_svc

        response = client.post(
            "/api/memory/retain",
            headers={"Authorization": "Bearer fake-test-token"},
            json={
                "memory_type": "constraint",
                "content": "Limited borewell depth, only 150 feet.",
                "crop": "Paddy",
            },
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Check farmer identity was extracted from current_user (9000011111)
        mock_svc.retain_memory.assert_called_once()
        call_kwargs = mock_svc.retain_memory.call_args[1]
        assert call_kwargs["farmer_id"] == "9000011111"
        assert call_kwargs["memory_type"] == "constraint"
        assert call_kwargs["content"] == "Limited borewell depth, only 150 feet."

    app.dependency_overrides.clear()


def test_memory_recall_authorized():
    app.dependency_overrides[get_current_user] = lambda: {
        "phone_number": "9000022222",
        "location": "Warangal, Telangana",
        "language": "te",
    }

    with patch("main.get_memory_service") as mock_get_svc:
        mock_svc = MagicMock(spec=FarmerMemoryService)
        mock_svc.recall_memories.return_value = [
            {
                "id": "mem_1",
                "text": "Prefers drought-resistant crops.",
                "tags": ["farmer:9000022222", "type:preference"],
                "metadata": {"farmer_id": "9000022222"},
            }
        ]
        mock_get_svc.return_value = mock_svc

        response = client.post(
            "/api/memory/recall",
            headers={"Authorization": "Bearer fake-test-token"},
            json={"query": "What crops do I prefer?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["farmer_id"] == "9000022222"
        assert data["count"] == 1
        assert data["memories"][0]["text"] == "Prefers drought-resistant crops."

        mock_svc.recall_memories.assert_called_once()
        call_kwargs = mock_svc.recall_memories.call_args[1]
        assert call_kwargs["farmer_id"] == "9000022222"

    app.dependency_overrides.clear()
