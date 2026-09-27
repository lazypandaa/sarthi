"""
Farmer Long-Term Memory Service
Enforces farmer isolation, memory taxonomy validation, metadata enrichment,
and credit-conscious deduplication over the Hindsight client.
"""

import hashlib
import logging
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Union

from .client import HindsightClient
from .config import HindsightConfig, get_hindsight_config
from .memory_types import (
    BaseMemoryModel,
    MemorySource,
    MemoryType,
)

logger = logging.getLogger("gramvaani.hindsight.service")


class FarmerMemoryService:
    """
    Domain service for all Gram Vaani farmer memory interactions.
    Provides strict tenant (farmer) isolation and credit-conscious controls.
    """

    def __init__(self, client: Optional[HindsightClient] = None, config: Optional[HindsightConfig] = None):
        self.config = config or get_hindsight_config()
        self.client = client or HindsightClient(self.config)
        
        # Credit-conscious write deduplication cache: (farmer_id, content_hash)
        # Keeps up to 500 recent entries to avoid writing identical facts repeatedly
        self._recent_writes: OrderedDict[str, float] = OrderedDict()
        self._max_recent_writes = 500

    def _normalize_farmer_id(self, farmer_id: Any) -> str:
        """Validates and normalizes farmer identity."""
        if not farmer_id:
            raise ValueError("farmer_id cannot be null or empty.")
        fid = str(farmer_id).strip()
        if not fid:
            raise ValueError("farmer_id cannot be whitespace.")
        return fid

    def _normalize_memory_type(self, m_type: Union[str, MemoryType]) -> MemoryType:
        """Validates that the memory category is in the authoritative 8-part taxonomy."""
        if isinstance(m_type, MemoryType):
            return m_type
        
        clean = str(m_type).strip().lower()
        for member in MemoryType:
            if member.value == clean or member.name.lower() == clean:
                return member
        
        allowed = [m.value for m in MemoryType]
        raise ValueError(f"Invalid memory_type '{m_type}'. Must be one of: {allowed}")

    def _get_write_key(self, farmer_id: str, content: str) -> str:
        h = hashlib.sha256(content.strip().encode("utf-8")).hexdigest()[:16]
        return f"{farmer_id}:{h}"

    def _is_duplicate_write(self, farmer_id: str, content: str) -> bool:
        key = self._get_write_key(farmer_id, content)
        return key in self._recent_writes

    def _record_write(self, farmer_id: str, content: str):
        key = self._get_write_key(farmer_id, content)
        self._recent_writes[key] = datetime.now(timezone.utc).timestamp()
        if len(self._recent_writes) > self._max_recent_writes:
            self._recent_writes.popitem(last=False)

    def health_check(self) -> Dict[str, Any]:
        """Check status of the underlying memory system."""
        return self.client.health_check()

    def retain_memory(
        self,
        farmer_id: str,
        memory_type: Union[str, MemoryType],
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source: Union[str, MemorySource] = MemorySource.FARMER,
        tags: Optional[List[str]] = None,
        crop: Optional[str] = None,
        location: Optional[str] = None,
        season: Optional[str] = None,
        confidence: float = 1.0,
        skip_dedup: bool = False,
    ) -> Dict[str, Any]:
        """
        Retains a verified fact or observation for a specific farmer.
        Enforces farmer isolation and credit-conscious deduplication.
        """
        validated_farmer_id = self._normalize_farmer_id(farmer_id)
        validated_type = self._normalize_memory_type(memory_type)
        
        if not content or not content.strip():
            return {
                "success": False,
                "retained": False,
                "reason": "Content cannot be empty.",
            }

        cleaned_content = content.strip()

        # Credit-conscious deduplication check
        if not skip_dedup and self._is_duplicate_write(validated_farmer_id, cleaned_content):
            logger.info(f"Skipping duplicate memory write for farmer '{validated_farmer_id}'.")
            return {
                "success": True,
                "retained": False,
                "deduplicated": True,
                "duplicate": True,
                "message": "Identical memory was recently retained. Skipped to preserve credits.",
            }

        # Source normalization
        norm_source = source if isinstance(source, MemorySource) else MemorySource(str(source).lower())

        # Build normalized metadata
        now_iso = datetime.now(timezone.utc).isoformat()
        norm_metadata: Dict[str, str] = {
            "farmer_id": validated_farmer_id,
            "memory_type": validated_type.value,
            "source": norm_source.value,
            "timestamp": now_iso,
            "confidence": str(confidence),
        }
        if crop:
            norm_metadata["crop"] = str(crop)
        if location:
            norm_metadata["location"] = str(location)
        if season:
            norm_metadata["season"] = str(season)

        if metadata:
            for k, v in metadata.items():
                if v is not None:
                    norm_metadata[str(k)] = str(v)

        # Build isolation tags: Always include farmer:<id> and type:<type>
        norm_tags = [
            f"farmer:{validated_farmer_id}",
            f"type:{validated_type.value}",
            f"source:{norm_source.value}",
        ]
        if crop:
            norm_tags.append(f"crop:{crop.lower().replace(' ', '_')}")
        if season:
            norm_tags.append(f"season:{season.lower()}")
        if tags:
            for t in tags:
                if t and t not in norm_tags:
                    norm_tags.append(str(t))

        result = self.client.retain(
            bank_id=self.config.bank_id,
            content=cleaned_content,
            metadata=norm_metadata,
            tags=norm_tags,
        )

        if result.get("success"):
            self._record_write(validated_farmer_id, cleaned_content)

        return result

    def retain_model(self, model: BaseMemoryModel) -> Dict[str, Any]:
        """Convenience method to retain any typed memory model directly."""
        return self.retain_memory(
            farmer_id=model.farmer_id,
            memory_type=model.memory_type,
            content=model.to_content(),
            metadata=model.to_metadata(),
            source=model.source,
            tags=model.to_tags(),
            crop=model.crop,
            location=model.location,
            season=model.season,
            confidence=model.confidence,
        )

    def recall_memories(
        self,
        farmer_id: str,
        query: str,
        memory_types: Optional[List[Union[str, MemoryType]]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Recalls memories for a specific farmer.
        Enforces strict farmer isolation via mandatory farmer tag.
        """
        validated_farmer_id = self._normalize_farmer_id(farmer_id)
        
        if not query or not query.strip():
            return []

        # Tag for isolation
        query_tags = [f"farmer:{validated_farmer_id}"]

        # If specific memory types are requested, filter by them
        if memory_types:
            for mt in memory_types:
                vtype = self._normalize_memory_type(mt)
                query_tags.append(f"type:{vtype.value}")

        raw_results = self.client.recall(
            bank_id=self.config.bank_id,
            query=query.strip(),
            tags=query_tags,
            limit=limit,
            tags_match="all" if len(query_tags) > 1 else "any",
        )

        # Secondary strict client-side isolation guard:
        # Guarantee that no memory tagged for another farmer is ever returned
        isolated_results: List[Dict[str, Any]] = []
        expected_tag = f"farmer:{validated_farmer_id}"

        for item in raw_results:
            item_tags = item.get("tags") or []
            item_meta = item.get("metadata") or {}

            # Check tag or metadata
            meta_fid = item_meta.get("farmer_id")
            has_tag = expected_tag in item_tags
            
            # If tags or metadata exist, verify they match the requesting farmer
            if meta_fid and meta_fid != validated_farmer_id:
                logger.warning(
                    f"Cross-farmer leak detected and blocked: memory belongs to '{meta_fid}', requested by '{validated_farmer_id}'"
                )
                continue
            
            if item_tags and not has_tag:
                # Contains farmer tag for another farmer
                other_farmer_tags = [t for t in item_tags if t.startswith("farmer:")]
                if other_farmer_tags and expected_tag not in other_farmer_tags:
                    continue

            isolated_results.append(item)

        return isolated_results

    def get_farmer_memory_summary(self, farmer_id: str) -> Dict[str, Any]:
        """
        Retrieves a structured overview of durable knowledge stored for a farmer
        organized into 4 human-friendly sections: Profile, Preferences, Past Experience, Learned From You.
        """
        validated_farmer_id = self._normalize_farmer_id(farmer_id)
        
        # 1. Profile
        profile_facts = self.recall_memories(
            farmer_id=validated_farmer_id,
            query="farm size soil type location language profile acreage",
            memory_types=[MemoryType.PROFILE],
            limit=6,
        )
        # 2. Preferences
        preferences = self.recall_memories(
            farmer_id=validated_farmer_id,
            query="preference preferred crops organic fertilizer method low water budget",
            memory_types=[MemoryType.PREFERENCE],
            limit=6,
        )
        # 3. Past Experience (Crop history & incidents)
        crop_history = self.recall_memories(
            farmer_id=validated_farmer_id,
            query="crop history past seasons harvest failed success yield pest incident",
            memory_types=[MemoryType.CROP_HISTORY, MemoryType.INCIDENT],
            limit=8,
        )
        # 4. Learned From You (Constraints, corrections, outcomes)
        learned = self.recall_memories(
            farmer_id=validated_farmer_id,
            query="constraint correction outcome water limitation rejected recommendation",
            memory_types=[MemoryType.CONSTRAINT, MemoryType.CORRECTION, MemoryType.OUTCOME],
            limit=8,
        )

        def humanize(items, default_type="general"):
            cleaned = []
            for it in items:
                m = it.get("metadata") or {}
                t = m.get("memory_type") or it.get("type", default_type)
                cleaned.append({
                    "id": it.get("id"),
                    "text": it.get("text", "").strip(),
                    "type": t,
                    "source": m.get("source", "farmer"),
                    "crop": m.get("crop"),
                    "result": m.get("result") or m.get("outcome"),
                    "reason": m.get("reason"),
                    "timestamp": m.get("timestamp") or it.get("timestamp"),
                })
            return cleaned

        profile_clean = humanize(profile_facts, "profile")
        pref_clean = humanize(preferences, "preference")
        exp_clean = humanize(crop_history, "crop_history")
        learned_clean = humanize(learned, "learned")

        # Derive "What Changed?" evolution insights from farmer learning
        what_changed = []
        for l in learned_clean:
            if l["type"] == "correction":
                what_changed.append({
                    "trigger": "Direct Farmer Correction",
                    "summary": l["text"],
                    "impact": "System updated reasoning to align with farmer-verified facts."
                })
            elif l["type"] == "constraint":
                what_changed.append({
                    "trigger": "New Farm Constraint Identified",
                    "summary": l["text"],
                    "impact": "Water-intensive or high-risk crops are now automatically filtered or deprioritized."
                })
        for e in exp_clean:
            if "fail" in e["text"].lower() or (e.get("result") or "").lower() == "failure":
                crop = e.get("crop") or "crop"
                what_changed.append({
                    "trigger": f"Past {crop.capitalize()} Experience",
                    "summary": e["text"],
                    "impact": f"Future recommendations actively account for {crop} limitations and suggest resilient alternatives."
                })

        total_count = len(profile_clean) + len(pref_clean) + len(exp_clean) + len(learned_clean)

        return {
            "farmer_id": validated_farmer_id,
            "has_memory": total_count > 0,
            "memory_count": total_count,
            "service_status": {
                "available": self.client.is_available,
                "configured": self.config.is_configured,
            },
            "sections": {
                "profile": profile_clean,
                "preferences": pref_clean,
                "past_experience": exp_clean,
                "learned_from_you": learned_clean,
            },
            "what_changed": what_changed,
            # Backward compatibility keys
            "profile_memories": profile_clean,
            "constraint_memories": [m for m in learned_clean if m["type"] == "constraint"],
            "preference_memories": pref_clean,
        }


# Global service instance cache
_memory_service_instance: Optional[FarmerMemoryService] = None


def get_memory_service() -> FarmerMemoryService:
    """Retrieve or initialize the singleton FarmerMemoryService."""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = FarmerMemoryService()
    return _memory_service_instance
