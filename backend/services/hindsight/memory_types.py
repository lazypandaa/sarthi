"""
Farmer Long-Term Memory Models & Taxonomy
Defines the 8 durable memory categories, source classifications, and structured schemas.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """The 8 authoritative Gram Vaani long-term memory categories."""
    PROFILE = "profile"
    PREFERENCE = "preference"
    CONSTRAINT = "constraint"
    CROP_HISTORY = "crop_history"
    RECOMMENDATION = "recommendation"
    CORRECTION = "correction"
    OUTCOME = "outcome"
    INCIDENT = "incident"


class MemorySource(str, Enum):
    """Identifies the authority and provenance of stored information."""
    FARMER = "farmer"
    FARMER_PROFILE = "farmer_profile"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    EXTERNAL_DATA = "external_data"


class BaseMemoryModel(BaseModel):
    """Base schema for all farmer memory units."""
    farmer_id: str = Field(..., description="Canonical farmer identity (phone number)")
    memory_type: MemoryType = Field(..., description="Category in the 8-part memory taxonomy")
    source: MemorySource = Field(default=MemorySource.FARMER, description="Source provenance")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO timestamp")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    crop: Optional[str] = None
    location: Optional[str] = None
    season: Optional[str] = None

    def to_content(self) -> str:
        """Subclasses define natural language memory representation."""
        raise NotImplementedError

    def to_metadata(self) -> Dict[str, str]:
        """Convert fields to string-valued dictionary for Hindsight SDK."""
        meta: Dict[str, str] = {
            "farmer_id": str(self.farmer_id),
            "memory_type": str(self.memory_type.value),
            "source": str(self.source.value),
            "timestamp": str(self.timestamp),
            "confidence": str(self.confidence),
        }
        if self.crop:
            meta["crop"] = str(self.crop)
        if self.location:
            meta["location"] = str(self.location)
        if self.season:
            meta["season"] = str(self.season)
        return meta

    def to_tags(self) -> List[str]:
        """Generate isolation and classification tags."""
        tags = [
            f"farmer:{self.farmer_id}",
            f"type:{self.memory_type.value}",
            f"source:{self.source.value}",
        ]
        if self.crop:
            tags.append(f"crop:{self.crop.lower().replace(' ', '_')}")
        if self.season:
            tags.append(f"season:{self.season.lower()}")
        return tags


class ProfileMemory(BaseMemoryModel):
    """Durable farmer/farm attributes from verified profile or explicitly stated context."""
    memory_type: MemoryType = MemoryType.PROFILE
    fact: str
    farm_size: Optional[str] = None
    soil_type: Optional[str] = None
    preferred_language: Optional[str] = None

    def to_content(self) -> str:
        parts = [self.fact]
        if self.farm_size:
            parts.append(f"Farm size: {self.farm_size}.")
        if self.soil_type:
            parts.append(f"Soil type: {self.soil_type}.")
        if self.location:
            parts.append(f"Location: {self.location}.")
        return " ".join(parts)


class PreferenceMemory(BaseMemoryModel):
    """Farmer preferences (e.g. low-water crops, organic methods, risk aversion)."""
    memory_type: MemoryType = MemoryType.PREFERENCE
    fact: str
    preference_category: Optional[str] = None

    def to_content(self) -> str:
        return f"Farmer preference: {self.fact}"


class ConstraintMemory(BaseMemoryModel):
    """Critical farming constraints (e.g. irrigation limitations, budget, labor)."""
    memory_type: MemoryType = MemoryType.CONSTRAINT
    fact: str
    constraint_category: Optional[str] = None

    def to_content(self) -> str:
        return f"Farm operational constraint: {self.fact}"


class CropHistoryMemory(BaseMemoryModel):
    """Past crop cultivation experience, outcomes, and reasons."""
    memory_type: MemoryType = MemoryType.CROP_HISTORY
    crop: str
    season: Optional[str] = None
    outcome: str = "unknown"  # success | failed | partial | unknown
    reason: Optional[str] = None
    notes: Optional[str] = None

    def to_content(self) -> str:
        content = f"Historical crop: {self.crop}."
        if self.season:
            content += f" Season: {self.season}."
        content += f" Outcome: {self.outcome}."
        if self.reason:
            content += f" Reason: {self.reason}."
        if self.notes:
            content += f" Notes: {self.notes}."
        return content


class RecommendationMemory(BaseMemoryModel):
    """High-value previous agricultural recommendations."""
    memory_type: MemoryType = MemoryType.RECOMMENDATION
    recommendation: str
    context: Optional[str] = None
    reason: Optional[str] = None

    def to_content(self) -> str:
        content = f"Previous recommendation: {self.recommendation}."
        if self.context:
            content += f" Context: {self.context}."
        if self.reason:
            content += f" Reasoning: {self.reason}."
        return content


class CorrectionMemory(BaseMemoryModel):
    """Authoritative farmer correction overriding prior or inferred information."""
    memory_type: MemoryType = MemoryType.CORRECTION
    previous_information: str
    corrected_information: str
    source: MemorySource = MemorySource.FARMER

    def to_content(self) -> str:
        return (
            f"Correction by farmer: Previous assumption '{self.previous_information}' "
            f"was corrected to '{self.corrected_information}'."
        )

    def to_metadata(self) -> Dict[str, str]:
        meta = super().to_metadata()
        meta["previous_info"] = self.previous_information
        meta["corrected_info"] = self.corrected_information
        return meta


class OutcomeMemory(BaseMemoryModel):
    """Realized result of a crop or treatment tied to a previous recommendation."""
    memory_type: MemoryType = MemoryType.OUTCOME
    related_recommendation: Optional[str] = None
    result: str  # success | failure | partial | unknown
    reason: Optional[str] = None

    def to_content(self) -> str:
        content = f"Outcome result: {self.result}."
        if self.related_recommendation:
            content += f" Related recommendation: {self.related_recommendation}."
        if self.reason:
            content += f" Reason/Analysis: {self.reason}."
        return content


class IncidentMemory(BaseMemoryModel):
    """Significant agricultural incidents (pest outbreak, frost damage, flood, etc.)."""
    memory_type: MemoryType = MemoryType.INCIDENT
    incident_type: str  # pest | disease | weather | irrigation | other
    description: str
    severity: str = "medium"  # low | medium | high | severe

    def to_content(self) -> str:
        content = f"Farm incident ({self.incident_type}, severity: {self.severity}): {self.description}."
        if self.crop:
            content += f" Affected crop: {self.crop}."
        if self.location:
            content += f" Location: {self.location}."
        return content
