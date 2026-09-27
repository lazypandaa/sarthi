"""
Gram Vaani Memory-Aware Recommendation & Learning Engine (Phase 3 & Phase 4)
Handles:
1. Targeted Hindsight recall before recommendation generation
2. Memory context assembly with strict precedence policy
3. Structured memory-influence metadata generation
4. Learning extraction from conversational feedback and structured outcome reporting
"""

import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from .memory_service import FarmerMemoryService, get_memory_service
from .memory_types import (
    CorrectionMemory,
    CropHistoryMemory,
    ConstraintMemory,
    MemorySource,
    MemoryType,
    OutcomeMemory,
    PreferenceMemory,
    ProfileMemory,
)

logger = logging.getLogger("gramvaani.hindsight.recommender")

# Keywords that indicate agricultural decisions where long-term memory is valuable
AGRI_DECISION_KEYWORDS: Set[str] = {
    "grow", "plant", "crop", "crops", "farming", "sow", "cultivate", "cultivation",
    "harvest", "irrigation", "water", "borewell", "fertilizer", "manure", "soil",
    "paddy", "rice", "wheat", "cotton", "tomato", "chili", "chilli", "groundnut",
    "maize", "soybean", "pulses", "gram", "rabi", "kharif", "season", "yield",
    "recommend", "suggest", "suitable", "pest", "disease", "outbreak",
    # Multilingual keywords (Hindi / Telugu romanized / devanagari)
    "फसल", "बोना", "उगाना", "खेती", "सिंचाई", "पानी", "खाद", "मिट्टी", "पैदावार",
    "పంట", "సాగు", "విత్తనాలు", "నీరు", "ఎరువులు"
}

# Negation and override cues
OVERRIDE_PATTERNS = [
    r"(?:no\s+longer|don't\s+want|do\s+not\s+want|stop|quit)\s+(?:growing|planting)?\s*([a-zA-Z]+)",
    r"(?:installed|built|added|now\s+have|got)\s+(?:a\s+)?(?:new\s+)?(drip|borewell|sprinkler|irrigation|canal|solar\s+pump|water\s+system)",
    r"(?:now\s+prefer|prefer\s+now)\s+([a-zA-Z\s]+)",
]

# Explicit outcome / failure / success cues in conversational feedback
FAILURE_PATTERNS = [
    r"(?:failed|ruined|died|loss|did\s+not\s+work|didn't\s+work|poor\s+yield|destroyed)\s+(?:because|due\s+to|since)?\s*([^\.]+)",
    r"tried\s+([a-zA-Z]+)\s+.*(?:failed|didn't\s+work|died)",
    r"([a-zA-Z]+)\s+.*(?:crop\s+)?failed",
]

SUCCESS_PATTERNS = [
    r"([a-zA-Z]+)\s+(?:worked\s+well|succeeded|good\s+yield|great\s+harvest|produced\s+well)",
    r"(?:harvested|got)\s+good\s+(?:yield|harvest)\s+(?:from|in|with)\s+([a-zA-Z]+)",
]


class MemoryAwareRecommender:
    """
    Coordinates Hindsight memory retrieval, prompt contextualization,
    and post-recommendation outcome/correction extraction.
    """

    def __init__(self, memory_service: Optional[FarmerMemoryService] = None):
        self.memory_service = memory_service or get_memory_service()

    def is_memory_relevant_query(self, query: str) -> bool:
        """
        Credit-conscious gate: Determines whether a query needs long-term memory.
        Returns False for casual greetings, weather queries without decision context, etc.
        """
        if not query or len(query.strip()) < 3:
            return False

        q_lower = query.lower()

        # Pure greetings or non-farming checks
        if q_lower in ["hi", "hello", "hey", "namaste", "good morning", "good evening", "how are you"]:
            return False

        words = set(re.findall(r"[\w]+", q_lower))
        return bool(words.intersection(AGRI_DECISION_KEYWORDS)) or any(k in q_lower for k in AGRI_DECISION_KEYWORDS)

    def build_recall_query(self, text: str, location: Optional[str] = None) -> str:
        """Constructs a concise, targeted search query for Hindsight."""
        core_tokens = []
        q_lower = text.lower()
        for token in re.findall(r"[\w]+", q_lower):
            if token in AGRI_DECISION_KEYWORDS:
                core_tokens.append(token)
        
        # Fallback or enrichment
        query_str = " ".join(core_tokens) if core_tokens else text
        if "water" in q_lower or "irrigation" in q_lower:
            query_str += " irrigation constraint"
        if "grow" in q_lower or "plant" in q_lower or "season" in q_lower:
            query_str += " crop preference history outcome"

        return query_str.strip()[:200]

    def assemble_memory_context(
        self,
        farmer_id: str,
        query: str,
        location: Optional[str] = None,
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        Recalls and groups relevant memories for the current decision.
        Returns (grouped_context, raw_memories).
        """
        if not self.is_memory_relevant_query(query):
            return {}, []

        search_query = self.build_recall_query(query, location)
        
        try:
            raw_memories = self.memory_service.recall_memories(
                farmer_id=farmer_id,
                query=search_query,
                memory_types=[
                    MemoryType.CONSTRAINT,
                    MemoryType.PREFERENCE,
                    MemoryType.CROP_HISTORY,
                    MemoryType.CORRECTION,
                    MemoryType.OUTCOME,
                    MemoryType.PROFILE,
                ],
                limit=6,  # Cap token consumption
            )
        except Exception as e:
            logger.error(f"Failed to recall memories for farmer '{farmer_id}': {e}")
            raw_memories = []

        if not raw_memories:
            return {}, []

        grouped: Dict[str, List[Dict[str, Any]]] = {
            "constraints": [],
            "preferences": [],
            "crop_history": [],
            "corrections": [],
            "outcomes": [],
            "profile": [],
        }

        for item in raw_memories:
            meta = item.get("metadata") or {}
            m_type = meta.get("memory_type") or item.get("type") or "profile"
            text = item.get("text", "").strip()
            if not text:
                continue

            entry = {
                "id": item.get("id"),
                "text": text,
                "type": m_type,
                "source": meta.get("source", "farmer"),
                "crop": meta.get("crop"),
            }

            if m_type == MemoryType.CONSTRAINT.value:
                grouped["constraints"].append(entry)
            elif m_type == MemoryType.PREFERENCE.value:
                grouped["preferences"].append(entry)
            elif m_type == MemoryType.CROP_HISTORY.value:
                grouped["crop_history"].append(entry)
            elif m_type == MemoryType.CORRECTION.value:
                grouped["corrections"].append(entry)
            elif m_type == MemoryType.OUTCOME.value:
                grouped["outcomes"].append(entry)
            elif m_type == MemoryType.PROFILE.value:
                grouped["profile"].append(entry)

        # Apply precedence: filter out stale memories superseded by current query
        filtered_grouped = self.apply_precedence_policy(grouped, query)
        return filtered_grouped, raw_memories

    def apply_precedence_policy(
        self,
        grouped: Dict[str, List[Dict[str, Any]]],
        current_query: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Ensures that current explicit statements override stale memories.
        E.g., if a memory says 'limited irrigation' but current query states 'I installed drip irrigation',
        the stale constraint is suppressed from reasoning.
        """
        q_lower = current_query.lower()

        # Check for new irrigation override
        new_irrigation = bool(
            re.search(
                r"(?:installed|built|have|got|added|now\s+have)\s+(?:a\s+)?(?:new\s+)?(?:drip|borewell|sprinkler|irrigation|canal|solar\s+pump|water)",
                q_lower,
            )
        )
        if new_irrigation:
            # Demote or remove old water constraints
            grouped["constraints"] = [
                c for c in grouped["constraints"]
                if "irrigation" not in c["text"].lower() and "water" not in c["text"].lower()
            ]

        # Check for crop preference override (e.g. "I don't want to grow groundnut anymore")
        for pref in list(grouped["preferences"]):
            crop = pref.get("crop")
            if crop and re.search(rf"(?:don't|not|stop|no\s+longer).*?\b{crop.lower()}\b", q_lower):
                grouped["preferences"].remove(pref)

        return grouped

    def format_memory_for_prompt(self, assembled_context: Dict[str, List[Dict[str, Any]]]) -> str:
        """Formats the structured memories into a concise, readable block for the LLM prompt."""
        if not assembled_context or not any(assembled_context.values()):
            return ""

        sections = []

        if assembled_context.get("constraints"):
            c_lines = [f"  - [CONSTRAINT]: {c['text']}" for c in assembled_context["constraints"]]
            sections.append("Verified Farm Constraints:\n" + "\n".join(c_lines))

        if assembled_context.get("crop_history"):
            h_lines = [f"  - [PAST CROP HISTORY]: {h['text']}" for h in assembled_context["crop_history"]]
            sections.append("Past Crop Experience:\n" + "\n".join(h_lines))

        if assembled_context.get("outcomes"):
            o_lines = [f"  - [RECORDED OUTCOME]: {o['text']}" for o in assembled_context["outcomes"]]
            sections.append("Past Outcomes:\n" + "\n".join(o_lines))

        if assembled_context.get("corrections"):
            cor_lines = [f"  - [FARMER CORRECTION]: {cor['text']}" for cor in assembled_context["corrections"]]
            sections.append("Farmer Corrections (Authoritative):\n" + "\n".join(cor_lines))

        if assembled_context.get("preferences"):
            p_lines = [f"  - [PREFERENCE]: {p['text']}" for p in assembled_context["preferences"]]
            sections.append("Farmer Preferences:\n" + "\n".join(p_lines))

        if assembled_context.get("profile"):
            pf_lines = [f"  - [PROFILE]: {pf['text']}" for pf in assembled_context["profile"]]
            sections.append("Known Farm Profile:\n" + "\n".join(pf_lines))

        header = "=== REMEMBERED FARMER CONTEXT (from Hindsight Long-Term Memory) ==="
        footer = (
            "IMPORTANT REASONING DIRECTIVE:\n"
            "Weigh current external agricultural conditions together with these remembered farmer constraints/history.\n"
            "If a crop is suitable under current season/weather but conflicts with a remembered constraint (e.g., limited irrigation) "
            "or previously failed due to that constraint, explicitly account for it in your recommendation and suggest realistic alternatives."
        )
        return f"\n{header}\n" + "\n\n".join(sections) + f"\n\n{footer}\n"

    def build_memory_influence_metadata(
        self,
        assembled_context: Dict[str, List[Dict[str, Any]]],
        recommendation_text: str,
    ) -> List[Dict[str, str]]:
        """
        Builds structured explanation of how retrieved memories shaped the recommendation.
        Exposed in backend API responses for future UI integration.
        """
        influence: List[Dict[str, str]] = []
        rec_lower = recommendation_text.lower()

        # Constraints
        for c in assembled_context.get("constraints", []):
            text = c["text"]
            if "irrigation" in text.lower() or "water" in text.lower():
                influence.append({
                    "type": "constraint",
                    "summary": text,
                    "impact": "Prioritized drought-tolerant / lower-water crops and warned against high-water options.",
                })
            else:
                influence.append({
                    "type": "constraint",
                    "summary": text,
                    "impact": "Constrained crop and management options to match farm limits.",
                })

        # Past Crop History & Outcomes
        for h in assembled_context.get("crop_history", []) + assembled_context.get("outcomes", []):
            text = h["text"]
            crop = h.get("crop")
            impact_desc = "Factored previous harvest outcome into recommendation."
            if "fail" in text.lower() or "insufficient" in text.lower():
                impact_desc = f"Deprioritized {crop or 'failing crop'} and recommended alternatives to avoid repeat failure."
            elif "success" in text.lower() or "well" in text.lower():
                impact_desc = f"Maintained confidence in proven successful crop ({crop or 'history'})."

            influence.append({
                "type": h.get("type", "crop_history"),
                "summary": text,
                "impact": impact_desc,
            })

        # Corrections
        for cor in assembled_context.get("corrections", []):
            influence.append({
                "type": "correction",
                "summary": cor["text"],
                "impact": "Overrode previous assumptions based on authoritative farmer statement.",
            })

        # Preferences
        for p in assembled_context.get("preferences", []):
            influence.append({
                "type": "preference",
                "summary": p["text"],
                "impact": "Filtered recommendations towards farmer's stated preferences.",
            })

        return influence

    def detect_and_retain_conversational_learning(
        self,
        farmer_id: str,
        user_message: str,
        recommendation_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        PHASE 4: Listens to incoming farmer messages for explicit durable learning:
        - Past failures / successes
        - New or corrected constraints
        - Hard preferences
        Credit-conscious: Skips non-factual statements and casual chat.
        """
        if not user_message or len(user_message.strip()) < 10:
            return None

        msg = user_message.strip()
        msg_lower = msg.lower()

        # 1. Detect explicit past failure with reason (Outcome / Crop History)
        # e.g., "I tried tomato last season and it failed because I didn't have enough water"
        for pattern in FAILURE_PATTERNS:
            match = re.search(pattern, msg_lower)
            if match:
                crop = None
                for c in ["tomato", "paddy", "cotton", "chili", "chilli", "groundnut", "maize", "soybean", "wheat", "onion"]:
                    if c in msg_lower:
                        crop = c.capitalize()
                        break

                content = f"Farmer previously attempted {crop or 'crop'} cultivation and reported failure: {msg}."
                meta = {
                    "source": MemorySource.FARMER.value,
                    "outcome": "failed",
                }
                if crop:
                    meta["crop"] = crop
                if recommendation_id:
                    meta["related_recommendation_id"] = recommendation_id

                extracted_facts = []
                if any(w in msg_lower for w in ["limited irrigation", "not enough water", "insufficient irrigation", "borewell", "water"]):
                    extracted_facts.append("Limited irrigation")
                if crop:
                    extracted_facts.append(f"Previous {crop.lower()} failure")
                else:
                    extracted_facts.append("Previous crop failure")
                if any(w in msg_lower for w in ["water", "irrigation", "borewell"]):
                    extracted_facts.append("Water-related constraint")

                res = self.memory_service.retain_memory(
                    farmer_id=farmer_id,
                    memory_type=MemoryType.CROP_HISTORY,
                    content=content,
                    metadata=meta,
                    crop=crop,
                    source=MemorySource.FARMER,
                )
                if isinstance(res, dict):
                    res["extracted_facts"] = extracted_facts
                    res["memory_type"] = "crop_history"
                    res["summary"] = content
                return res

        # 2. Detect explicit success (Outcome)
        # e.g., "Groundnut worked well this season"
        for pattern in SUCCESS_PATTERNS:
            match = re.search(pattern, msg_lower)
            if match:
                crop = match.group(1).capitalize()
                content = f"Farmer reported that {crop} cultivation was successful: {msg}."
                meta = {
                    "source": MemorySource.FARMER.value,
                    "outcome": "success",
                    "crop": crop,
                }
                if recommendation_id:
                    meta["related_recommendation_id"] = recommendation_id

                res = self.memory_service.retain_memory(
                    farmer_id=farmer_id,
                    memory_type=MemoryType.OUTCOME,
                    content=content,
                    metadata=meta,
                    crop=crop,
                    source=MemorySource.FARMER,
                )
                if isinstance(res, dict):
                    res["extracted_facts"] = [f"Successful {crop.lower()} harvest", "Positive outcome history"]
                    res["memory_type"] = "outcome"
                    res["summary"] = content
                return res

        # 3. Detect explicit constraint disclosure
        # e.g., "I have limited irrigation", "No borewell on my land", "Only 2 hours of electricity"
        if any(w in msg_lower for w in [
            "limited irrigation", "no borewell", "water shortage", "not enough water", "no water",
            "dry land", "one hour of borewell", "hour of borewell", "borewell water", "insufficient irrigation",
            "hours of electricity", "water limitation"
        ]):
            extracted_facts = ["Limited irrigation"]
            if any(w in msg_lower for w in ["one hour", "1 hour", "hour of borewell"]):
                extracted_facts.append("Borewell limited to 1 hour daily")
            extracted_facts.append("Water-related constraint")

            res = self.memory_service.retain_memory(
                farmer_id=farmer_id,
                memory_type=MemoryType.CONSTRAINT,
                content=f"Farmer operational constraint: {msg}",
                metadata={"source": MemorySource.FARMER.value},
                source=MemorySource.FARMER,
            )
            if isinstance(res, dict):
                res["extracted_facts"] = extracted_facts
                res["memory_type"] = "constraint"
                res["summary"] = f"Farmer operational constraint: {msg}"
            return res

        # 4. Detect explicit preference
        # e.g., "I prefer lower-water crops", "I prefer organic fertilizers only"
        if any(w in msg_lower for w in ["i prefer", "we prefer", "only want to grow", "prefer lower-water", "prefer low-water", "require less water"]):
            extracted_facts = ["Crop & farming preference"]
            if any(w in msg_lower for w in ["lower-water", "less water", "low-water"]):
                extracted_facts.append("Prefers crops requiring less water")

            res = self.memory_service.retain_memory(
                farmer_id=farmer_id,
                memory_type=MemoryType.PREFERENCE,
                content=f"Farmer stated preference: {msg}",
                metadata={"source": MemorySource.FARMER.value},
                source=MemorySource.FARMER,
            )
            if isinstance(res, dict):
                res["extracted_facts"] = extracted_facts
                res["memory_type"] = "preference"
                res["summary"] = f"Farmer stated preference: {msg}"
            return res

        return None

    def process_structured_feedback(
        self,
        farmer_id: str,
        feedback: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        PHASE 4: Converts structured user feedback into verified long-term memory units.
        Handles outcomes, corrections, and actionable negative feedback.
        """
        query_id = feedback.get("query_id")
        feedback_type = feedback.get("feedback_type", "general")
        feedback_text = feedback.get("feedback_text") or ""
        outcome_result = feedback.get("outcome_result")
        outcome_reason = feedback.get("outcome_reason")
        crop = feedback.get("crop")
        correction_new = feedback.get("correction_new")
        correction_prev = feedback.get("correction_previous")

        # 1. Outcome Reporting
        if outcome_result or feedback_type == "outcome_reported":
            result = outcome_result or ("success" if feedback.get("helpful") else "failure")
            reason_str = f" Reason: {outcome_reason}." if outcome_reason else ""
            crop_str = f" for crop {crop}" if crop else ""
            content = f"Recorded outcome result: {result}{crop_str}.{reason_str} Feedback notes: {feedback_text}".strip()
            
            meta = {
                "related_recommendation_id": query_id or "",
                "result": result,
                "source": MemorySource.FARMER.value,
            }
            if crop:
                meta["crop"] = crop
            if outcome_reason:
                meta["reason"] = outcome_reason

            return self.memory_service.retain_memory(
                farmer_id=farmer_id,
                memory_type=MemoryType.OUTCOME,
                content=content,
                metadata=meta,
                crop=crop,
                source=MemorySource.FARMER,
            )

        # 2. Correction Reporting
        if correction_new or feedback_type == "corrected":
            prev_info = correction_prev or "Previous assistant advice/assumption"
            new_info = correction_new or feedback_text
            content = f"Farmer correction: Previous assumption '{prev_info}' corrected to: '{new_info}'."
            
            meta = {
                "related_recommendation_id": query_id or "",
                "previous_info": prev_info,
                "corrected_info": new_info,
                "source": MemorySource.FARMER.value,
            }
            if crop:
                meta["crop"] = crop

            return self.memory_service.retain_memory(
                farmer_id=farmer_id,
                memory_type=MemoryType.CORRECTION,
                content=content,
                metadata=meta,
                crop=crop,
                source=MemorySource.FARMER,
            )

        # 3. Actionable negative feedback explaining a constraint
        # E.g. helpful=False, feedback_text="I cannot follow this because I don't have enough water for tomato"
        if feedback.get("helpful") is False and feedback_text:
            text_lower = feedback_text.lower()
            if any(w in text_lower for w in ["water", "irrigation", "borewell", "labor", "money", "budget", "land", "soil"]):
                content = f"Farmer rejected recommendation ({query_id}) due to constraint: {feedback_text}"
                return self.memory_service.retain_memory(
                    farmer_id=farmer_id,
                    memory_type=MemoryType.CONSTRAINT,
                    content=content,
                    metadata={"related_recommendation_id": query_id or "", "source": MemorySource.FARMER.value},
                    source=MemorySource.FARMER,
                )

        return None


# Global singleton
_recommender_instance: Optional[MemoryAwareRecommender] = None


def get_recommender() -> MemoryAwareRecommender:
    """Retrieves or initializes the singleton MemoryAwareRecommender."""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = MemoryAwareRecommender()
    return _recommender_instance
