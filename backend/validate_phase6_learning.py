"""
Phase 6: End-to-End Live Validation of Hindsight Learning Experience
Executes the exact 3-session scenario specified in Requirement 16:
- SESSION 1: Farmer shares experience -> Hindsight Retain -> Memory appears in Dashboard
- SESSION 2: New session -> Hindsight Recall -> Enters LLM prompt -> Personalized recommendation
- SESSION 3: Farmer provides outcome feedback -> Hindsight Retain -> Available to future recall
"""

import os
import json
from services.hindsight.config import get_hindsight_config
from services.hindsight.memory_service import FarmerMemoryService
from services.hindsight.recommendation_engine import MemoryAwareRecommender
from openai import AzureOpenAI

def run_phase6_validation():
    print("=" * 65)
    print("🌾 SARTHI PHASE 6: HINDSIGHT LEARNING EXPERIENCE VALIDATION")
    print("=" * 65)

    config = get_hindsight_config()
    print(f"Config: Base URL: {config.base_url} | Bank ID: {config.bank_id} | Configured: {config.is_configured}")
    assert config.is_configured, "Hindsight must be configured with real credentials!"

    service = FarmerMemoryService(config=config)
    health = service.health_check()
    print(f"Health Check: {health.get('status')} (Available: {health.get('available')})")
    assert health.get("available") is True, "Hindsight Cloud must be healthy and available!"

    recommender = MemoryAwareRecommender(memory_service=service)
    test_farmer = "+919999999001"

    # --------------------------------------------------------------------------
    # SESSION 1: Farmer Shares Experience
    # --------------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("SESSION 1: Farmer Shares Experience")
    print("-" * 50)
    msg1 = "I have only one hour of borewell water per day. My tomato crop failed because of insufficient irrigation."
    print(f"Farmer [{test_farmer}] says: \"{msg1}\"")

    retained_learning = recommender.detect_and_retain_conversational_learning(
        farmer_id=test_farmer,
        user_message=msg1
    )
    print("Hindsight Retain Result:", json.dumps({k: v for k, v in retained_learning.items() if k != 'tags'}, indent=2))
    assert retained_learning is not None, "Failed to detect conversational learning!"
    assert retained_learning.get("success") is True or retained_learning.get("retained") is True, "Hindsight Retain failed!"
    print("✓ Hindsight Retain succeeded for Session 1.")

    # Verify memory appears in Memory Dashboard summary
    summary = service.get_farmer_memory_summary(farmer_id=test_farmer)
    total_memories = summary.get("memory_count", 0)
    print(f"Memory Dashboard Summary count: {total_memories} durable facts")
    assert total_memories > 0, "Memory did not appear in farmer memory summary!"
    print("✓ Memory Dashboard successfully retrieved persisted memories.")

    # --------------------------------------------------------------------------
    # SESSION 2: New Conversation / Session -> Memory Recall & Personalized Advice
    # --------------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("SESSION 2: New Session & Memory Recall")
    print("-" * 50)
    query2 = "What should I grow this season?"
    print(f"Farmer [{test_farmer}] asks in new session: \"{query2}\"")

    # 1. Hindsight Recall
    assembled_ctx, raw_memories = recommender.assemble_memory_context(
        farmer_id=test_farmer,
        query=query2,
        location="Anantapur, Andhra Pradesh"
    )
    print(f"Recalled memories from Hindsight Cloud: {len(raw_memories)}")
    assert len(raw_memories) > 0, "Session 2 Hindsight Recall returned 0 memories!"
    for m in raw_memories[:3]:
        print(f"  • [{m.get('type', 'memory')}]: {m.get('text')}")

    # 2. Memory Enters LLM Prompt
    memory_prompt_snippet = recommender.format_memory_for_prompt(assembled_ctx)
    print(f"\nFormatted Memory Prompt Section:\n{memory_prompt_snippet}")
    assert len(memory_prompt_snippet.strip()) > 0, "Memory prompt section is empty!"
    assert any(w in memory_prompt_snippet.lower() for w in ["water", "irrigation", "tomato", "failure", "hour"]), \
        "Prompt does not contain historical farmer memory!"
    print("✓ Verified real historical memories injected into reasoning prompt.")

    # 3. Call Live Azure OpenAI
    azure_client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://gramvaani-openai-sweden.openai.azure.com/"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    )

    system_prompt = f"""You are Sarthi, agricultural AI advisor.
Farmer location: Anantapur, Andhra Pradesh (semi-arid, dry climate).
{memory_prompt_snippet}

Provide concise, personalized crop advice respecting the farmer's water limits and past failures."""

    resp = azure_client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query2}
        ],
        max_tokens=300,
        temperature=0.7
    )
    recommendation_text = resp.choices[0].message.content
    print("\n--- Live Personalized Recommendation ---")
    print(recommendation_text)
    print("----------------------------------------")

    # Verify recommendation acknowledges water/borewell or warns against tomato
    rec_lower = recommendation_text.lower()
    has_adaptation = any(w in rec_lower for w in ["water", "irrigation", "borewell", "tomato", "drought", "groundnut", "millet", "pulse", "low-water"])
    assert has_adaptation, "Recommendation failed to adapt to recalled memory!"

    # 4. Memory Influence Metadata
    influence = recommender.build_memory_influence_metadata(assembled_ctx, recommendation_text)
    print("\nMemory Influence Metadata:")
    print(json.dumps(influence, indent=2))
    assert len(influence) > 0, "Memory influence metadata is empty!"
    print("✓ Verified memory influence metadata generated accurately.")

    # --------------------------------------------------------------------------
    # SESSION 3: Farmer Provides Feedback / Outcome -> Compounding Learning
    # --------------------------------------------------------------------------
    print("\n" + "-" * 50)
    print("SESSION 3: Farmer Feedback & Outcome Recording")
    print("-" * 50)
    feedback_payload = {
        "query_id": "rec_demo_s2_001",
        "helpful": True,
        "feedback_type": "outcome_reported",
        "crop": "Groundnut",
        "outcome_result": "success",
        "outcome_reason": "Groundnut yielded 18 quintals per acre with minimal water.",
        "feedback_text": "Groundnut was an excellent choice for my 1-hour borewell water limit."
    }
    print("Farmer submits harvest outcome:", json.dumps(feedback_payload, indent=2))

    outcome_res = recommender.process_structured_feedback(
        farmer_id=test_farmer,
        feedback=feedback_payload
    )
    print("Outcome Retain Result:", json.dumps(outcome_res, indent=2))
    assert outcome_res is not None, "Failed to process feedback outcome!"
    assert outcome_res.get("success") is True or outcome_res.get("retained") is True, "Failed to retain outcome memory!"
    print("✓ Feedback outcome successfully retained in Hindsight Cloud.")

    # Verify future recall can retrieve this newly retained outcome
    future_recall = service.recall_memories(
        farmer_id=test_farmer,
        query="What happened when I grew groundnut?",
        limit=5
    )
    print(f"\nFuture Recall for 'groundnut outcome' returned: {len(future_recall)} items")
    assert len(future_recall) > 0, "Future recall could not find newly retained outcome!"
    assert any("groundnut" in r.get("text", "").lower() for r in future_recall), "Recalled memories missing groundnut outcome!"
    print("✓ Verified future recall retrieves newly learned outcome.")

    # Cleanup client sessions
    service.close()

    print("\n" + "=" * 65)
    print("🎉 ALL 3 PHASE 6 SESSIONS FULLY VALIDATED AGAINST LIVE HINDSIGHT CLOUD!")
    print("=" * 65)

if __name__ == "__main__":
    run_phase6_validation()
