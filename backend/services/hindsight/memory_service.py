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

    def close(self):
        """Release any client session resources."""
        if self.client:
            self.client.close()

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
        Handles single or multi-type taxonomy filtering correctly without tag collision.
        """
        validated_farmer_id = self._normalize_farmer_id(farmer_id)
        
        if not query or not query.strip():
            return []

        # Tag for isolation
        expected_tag = f"farmer:{validated_farmer_id}"
        query_tags = [expected_tag]
        tags_match = "any"
        limit_to_send = limit

        # If caller requested exactly 1 memory type, we can filter at the Hindsight tag level with "all"
        if memory_types and len(memory_types) == 1:
            vtype = self._normalize_memory_type(memory_types[0])
            query_tags.append(f"type:{vtype.value}")
            tags_match = "all"
            limit_to_send = limit
        elif memory_types and len(memory_types) > 1:
            # When multiple types are requested, querying with all type tags and tags_match='all'
            # causes Hindsight to return 0 because memories have only one type tag.
            # We query by the mandatory farmer tag, request adequate candidate units,
            # and perform taxonomy filtering in application code.
            limit_to_send = max(limit * 3, 25)

        raw_results = self.client.recall(
            bank_id=self.config.bank_id,
            query=query.strip(),
            tags=query_tags,
            limit=limit_to_send,
            tags_match=tags_match,
        )

        allowed_types: Optional[Set[str]] = None
        if memory_types:
            allowed_types = {self._normalize_memory_type(mt).value for mt in memory_types}

        # Secondary strict client-side isolation guard and taxonomy filter:
        isolated_results: List[Dict[str, Any]] = []

        for item in raw_results:
            item_tags = item.get("tags") or []
            item_meta = item.get("metadata") or {}

            # Check tag or metadata for farmer isolation
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

            # Determine taxonomy type from metadata or tags
            mem_type = item_meta.get("memory_type")
            if not mem_type:
                for t in item_tags:
                    if t.startswith("type:"):
                        mem_type = t.split(":", 1)[1]
                        break
            mem_type = (mem_type or item.get("type") or "profile").lower()

            # Filter by requested taxonomy types if specified
            if allowed_types and mem_type not in allowed_types:
                continue

            isolated_results.append(item)
            if len(isolated_results) >= limit:
                break

        return isolated_results

    def get_farmer_memory_summary(self, farmer_id: str) -> Dict[str, Any]:
        """
        Retrieves a structured overview of durable knowledge stored for a farmer
        organized into 4 human-friendly sections: Profile, Preferences, Past Experience, Learned From You.
        Optimized to use ONE single farmer-scoped recall request to conserve credits.
        """
        validated_farmer_id = self._normalize_farmer_id(farmer_id)
        
        # Single credit-conscious recall query covering the farmer's full memory profile
        all_memories = self.recall_memories(
            farmer_id=validated_farmer_id,
            query="farm size soil type location language profile preferences constraints water irrigation crop history past seasons harvest failure success yield pest incident corrections outcomes",
            memory_types=None,  # All types permitted for this farmer
            limit=30,
        )

        def humanize(items, default_type="general"):
            cleaned = []
            for it in items:
                m = it.get("metadata") or {}
                tags = it.get("tags") or []
                t = m.get("memory_type")
                if not t:
                    for tag in tags:
                        if tag.startswith("type:"):
                            t = tag.split(":", 1)[1]
                            break
                t = t or it.get("type") or default_type
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

        profile_raw = []
        preferences_raw = []
        crop_history_raw = []
        learned_raw = []

        for item in all_memories:
            m = item.get("metadata") or {}
            tags = item.get("tags") or []
            m_type = m.get("memory_type")
            if not m_type:
                for t in tags:
                    if t.startswith("type:"):
                        m_type = t.split(":", 1)[1]
                        break
            m_type = (m_type or item.get("type") or "profile").lower()

            if m_type == MemoryType.PROFILE.value:
                profile_raw.append(item)
            elif m_type == MemoryType.PREFERENCE.value:
                preferences_raw.append(item)
            elif m_type in [MemoryType.CROP_HISTORY.value, MemoryType.INCIDENT.value]:
                crop_history_raw.append(item)
            elif m_type in [MemoryType.CONSTRAINT.value, MemoryType.CORRECTION.value, MemoryType.OUTCOME.value]:
                learned_raw.append(item)
            else:
                profile_raw.append(item)

        profile_clean = humanize(profile_raw, "profile")
        pref_clean = humanize(preferences_raw, "preference")
        exp_clean = humanize(crop_history_raw, "crop_history")
        learned_clean = humanize(learned_raw, "learned")

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

    def reset_demo_farmer_memories(self, farmer_id: str) -> Dict[str, Any]:
        """
        Safely clears memories for ONLY designated demo farmer accounts.
        Strictly prevents clearing real farmers' memories.
        """
        validated_farmer_id = self._normalize_farmer_id(farmer_id)
        allowed_demo_ids = {"+919999999001", "demo_farmer", "test_farmer_001"}
        if validated_farmer_id not in allowed_demo_ids:
            raise PermissionError(f"Reset is strictly forbidden for non-demo farmer ID: {validated_farmer_id}")

        if not self.client.is_available:
            return {"success": True, "deleted_count": 0, "farmer_id": validated_farmer_id, "mock": True}

        deleted_count = 0
        try:
            import asyncio
            raw_client = getattr(self.client, "_raw_client", None)
            if raw_client and hasattr(raw_client, "list_memories"):
                mems = raw_client.list_memories(bank_id=self.config.bank_id, limit=100)
                expected_tag = f"farmer:{validated_farmer_id}"
                doc_ids = set()
                for m in getattr(mems, "items", []):
                    tags = getattr(m, "tags", []) or []
                    doc_id = getattr(m, "document_id", None)
                    if expected_tag in tags and doc_id:
                        doc_ids.add(doc_id)

                for doc_id in doc_ids:
                    try:
                        coro = raw_client.documents.delete_document(bank_id=self.config.bank_id, document_id=doc_id)
                        asyncio.run(coro)
                        deleted_count += 1
                    except Exception as del_err:
                        logger.warning(f"Error deleting demo document {doc_id}: {del_err}")

        except Exception as e:
            logger.error(f"Error resetting demo farmer memories: {e}")

        return {
            "success": True,
            "farmer_id": validated_farmer_id,
            "deleted_documents": deleted_count,
            "message": f"Successfully reset demo memories for {validated_farmer_id}"
        }



# Global service instance cache
_memory_service_instance: Optional[FarmerMemoryService] = None


def get_memory_service() -> FarmerMemoryService:
    """Retrieve or initialize the singleton FarmerMemoryService."""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = FarmerMemoryService()
    return _memory_service_instance
