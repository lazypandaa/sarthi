"""
Gram Vaani Memory - Hindsight Service Package
Provides long-term memory foundation and farmer-isolated memory management.
"""

from .config import HindsightConfig, get_hindsight_config
from .memory_types import (
    MemoryType,
    MemorySource,
    BaseMemoryModel,
    ProfileMemory,
    PreferenceMemory,
    ConstraintMemory,
    CropHistoryMemory,
    RecommendationMemory,
    CorrectionMemory,
    OutcomeMemory,
    IncidentMemory,
)
from .client import HindsightClient
from .memory_service import FarmerMemoryService, get_memory_service
from .recommendation_engine import MemoryAwareRecommender, get_recommender

__all__ = [
    "HindsightConfig",
    "get_hindsight_config",
    "MemoryType",
    "MemorySource",
    "BaseMemoryModel",
    "ProfileMemory",
    "PreferenceMemory",
    "ConstraintMemory",
    "CropHistoryMemory",
    "RecommendationMemory",
    "CorrectionMemory",
    "OutcomeMemory",
    "IncidentMemory",
    "HindsightClient",
    "FarmerMemoryService",
    "get_memory_service",
    "MemoryAwareRecommender",
    "get_recommender",
]
