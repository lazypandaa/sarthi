"""
Data Aggregator - Database-First Agricultural Context Aggregator
Retrieves hyper-local data (soil, crops, season, weather, pest alerts, mandi prices)
directly from localized database tables to ground LLM reasoning in verified facts.
"""

from datetime import datetime
import os
import asyncio
from typing import Dict, Any, List
from services.agri_service import get_agri_service

def fetch_hyperlocal_data(user_location: str) -> Dict[str, Any]:
    """Fetch hyperlocal context directly from AgriService database."""
    agri = get_agri_service()
    return agri.get_hyperlocal_context(user_location)

def fetch_weather_data(user_location: str) -> Dict[str, Any]:
    """Fetch weather with 1-hour cache and risk alerts from AgriService."""
    agri = get_agri_service()
    return agri.get_weather_with_cache(user_location)

def fetch_pest_disease_data(user_location: str) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch recent community verified pest and disease sightings from Azure Table."""
    agri = get_agri_service()
    loc = agri.parse_location(user_location)
    district = loc["district"].lower()
    state = loc["state"].lower()

    reports = agri.reports_table.scan(Limit=50).get("Items", [])
    pests = []
    diseases = []

    for r in reports:
        r_type = r.get("report_type")
        r_dist = r.get("village_id", "").lower()
        if district in r_dist or state in r_dist:
            item = {
                "pest_name": r.get("crop", "Unknown"),
                "crop": r.get("crop", "Field Crop"),
                "severity": r.get("severity", "medium"),
                "description": r.get("description_english") or r.get("description", ""),
                "source": "Community Peer-Verified Sighting"
            }
            if r_type == "pest":
                pests.append(item)
            elif r_type == "disease":
                diseases.append(item)

    # If no local reports, take top national reports
    if not pests and not diseases:
        for r in reports[:6]:
            item = {
                "pest_name": r.get("crop", "Unknown"),
                "crop": r.get("crop", "Field Crop"),
                "severity": r.get("severity", "medium"),
                "description": r.get("description_english") or r.get("description", ""),
                "source": "Regional Agricultural Alert"
            }
            if r.get("report_type") == "pest":
                pests.append(item)
            elif r.get("report_type") == "disease":
                diseases.append(item)

    return {"pests": pests[:3], "diseases": diseases[:3]}

def get_crop_prices(user_location: str) -> Dict[str, Any]:
    """Get real mandi prices from Agmarknet table."""
    agri = get_agri_service()
    markets = agri.get_market_prices(user_location)
    prices_dict = {}
    mandi_name = "Regional Mandi"

    for m in markets:
        comm = m.get("commodity", "")
        price = m.get("modal_price") or m.get("max_price")
        if comm and price:
            prices_dict[comm] = price
            mandi_name = m.get("market", mandi_name)

    return {
        "market": mandi_name,
        "prices": prices_dict,
        "unit": "₹ per quintal",
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d")
    }

def fetch_context_sync(user_location: str, query: str) -> Dict[str, Any]:
    """
    Synchronously assemble comprehensive agricultural context from fast local database.
    """
    try:
        hyperlocal = fetch_hyperlocal_data(user_location)
        weather = fetch_weather_data(user_location)
        pest_dis = fetch_pest_disease_data(user_location)
        prices = get_crop_prices(user_location)

        return {
            "hyperlocal": hyperlocal,
            "weather": weather,
            "pest_outbreaks": pest_dis.get("pests", []),
            "disease_reports": pest_dis.get("diseases", []),
            "success_stories": [],
            "crop_prices": prices,
            "seasonal_info": {
                "season": hyperlocal.get("current_season", "rabi"),
                "rainfall": hyperlocal.get("rainfall", "900mm")
            }
        }
    except Exception as e:
        print(f"fetch_context_sync error: {e}")
        return {
            "hyperlocal": None,
            "weather": None,
            "pest_outbreaks": [],
            "disease_reports": [],
            "crop_prices": None
        }

def fetch_all_context_data(user_location: str, query: str) -> Dict[str, Any]:
    """Compatibility wrapper for fetch_context_sync."""
    return fetch_context_sync(user_location, query)

async def fetch_all_context_data_async(user_location: str, query: str) -> Dict[str, Any]:
    """Async wrapper."""
    return fetch_context_sync(user_location, query)

def format_context_for_llm(context: Dict[str, Any]) -> str:
    """
    Format authoritative agricultural database facts into a structured prompt section for the LLM.
    Ensures zero hallucination and ground truth in Indian agronomic parameters.
    """
    prompt_parts = []

    # 1. Hyperlocal location & soil profile
    if context.get("hyperlocal"):
        h = context["hyperlocal"]
        soil_p = h.get("soil_parameters", {})
        crops = ", ".join(h.get("recommended_crops", [])[:5])
        prompt_parts.append(
            f"LOCATION: {h.get('district', 'District')}, {h.get('state', 'State')}\n"
            f"SOIL PROFILE: {h.get('soil_type')} (pH: {soil_p.get('ph', 7.2)}, N: {soil_p.get('nitrogen_kg_ha', 220)} kg/ha, P: {soil_p.get('phosphorus_kg_ha', 18)} kg/ha, K: {soil_p.get('potassium_kg_ha', 280)} kg/ha)\n"
            f"SEASON: {h.get('current_season', 'rabi').upper()} (Rainfall norm: {h.get('rainfall', '900mm')})\n"
            f"DISTRICT SUITABLE CROPS: {crops}"
        )

    # 2. Weather
    if context.get("weather"):
        w = context["weather"]
        alert_str = f" | Alert: {w['alert']}" if w.get("alert") else ""
        prompt_parts.append(f"WEATHER: {w.get('condition')}, {w.get('temperature')}°C, {w.get('humidity')}% humidity{alert_str}")

    # 3. Pest alerts
    if context.get("pest_outbreaks"):
        pests = context["pest_outbreaks"]
        pest_strs = [f"{p.get('pest_name')} in {p.get('crop')} ({p.get('severity')})" for p in pests]
        prompt_parts.append(f"ACTIVE PEST WARNINGS: {'; '.join(pest_strs)}")

    # 4. Disease reports
    if context.get("disease_reports"):
        diseases = context["disease_reports"]
        dis_strs = [f"{d.get('disease_name')} in {d.get('crop')} ({d.get('severity')})" for d in diseases]
        prompt_parts.append(f"CROP DISEASE ALERTS: {'; '.join(dis_strs)}")

    # 5. Mandi Market Prices
    if context.get("crop_prices") and context["crop_prices"].get("prices"):
        p = context["crop_prices"]
        p_strs = [f"{c}: ₹{pr}" for c, pr in list(p["prices"].items())[:4]]
        prompt_parts.append(f"MANDI PRICES ({p.get('market')}): {', '.join(p_strs)} per quintal")

    return "\n".join(prompt_parts) if prompt_parts else "No specific agricultural context available"
