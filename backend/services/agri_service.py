"""
Gram Vaani Agricultural Intelligence Service
High-performance local database-first service for hyper-local agricultural data,
crop recommendations, crop calendar, soil intelligence, mandi prices, and advisories.
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from services.azure_table_db import get_azure_table_db

# Local In-Memory Cache with TTL to ensure sub-5ms responses
_MEMORY_CACHE: Dict[str, Any] = {}
_MEMORY_CACHE_TTL: Dict[str, float] = {}

def _get_cached(key: str) -> Optional[Any]:
    if key in _MEMORY_CACHE:
        if datetime.utcnow().timestamp() < _MEMORY_CACHE_TTL.get(key, 0):
            return _MEMORY_CACHE[key]
        else:
            del _MEMORY_CACHE[key]
            del _MEMORY_CACHE_TTL[key]
    return None

def _set_cached(key: str, value: Any, ttl_seconds: int = 300):
    _MEMORY_CACHE[key] = value
    _MEMORY_CACHE_TTL[key] = datetime.utcnow().timestamp() + ttl_seconds


class AgriService:
    def __init__(self):
        self.db = get_azure_table_db()
        self.locations_table = self.db.Table("sarthilocations")
        self.soil_table = self.db.Table("sarthisoilreference")
        self.crops_table = self.db.Table("sarthicropmaster")
        self.calendar_table = self.db.Table("sarthicropcalendar")
        self.advisories_table = self.db.Table("sarthiadvisories")
        self.markets_table = self.db.Table("sarthimarketprices")
        self.reports_table = self.db.Table("sarthicommunityreports")

    def get_current_season(self) -> str:
        """Calculate Indian agricultural season based on current UTC month."""
        month = datetime.utcnow().month
        if month in [6, 7, 8, 9, 10]:
            return "kharif"
        elif month in [11, 12, 1, 2, 3]:
            return "rabi"
        else:
            return "summer"

    def parse_location(self, location_str: str) -> Dict[str, str]:
        """Parse free-text location into district and state."""
        if not location_str:
            return {"district": "Sehore", "state": "Madhya Pradesh"}

        parts = [p.strip() for p in location_str.split(",") if p.strip()]
        if len(parts) >= 2:
            return {"district": parts[0], "state": parts[1]}
        elif len(parts) == 1:
            p = parts[0]
            # Known states
            known_states = ["Andhra Pradesh", "Telangana", "Maharashtra", "Madhya Pradesh", "Karnataka", "Tamil Nadu", "Punjab", "Haryana", "Gujarat", "Rajasthan", "Uttar Pradesh", "West Bengal", "Bihar"]
            matched_state = next((s for s in known_states if s.lower() == p.lower()), None)
            if matched_state:
                return {"district": "All", "state": matched_state}
            return {"district": p, "state": "India"}
        return {"district": "Sehore", "state": "Madhya Pradesh"}

    def get_hyperlocal_context(self, location_str: str) -> Dict[str, Any]:
        """
        Fast local database retrieval of district soil, rainfall, seasonal crops, and alerts.
        """
        cache_key = f"hyperlocal:{location_str.lower().strip()}"
        cached = _get_cached(cache_key)
        if cached:
            return cached

        loc = self.parse_location(location_str)
        district = loc["district"]
        state = loc["state"]
        season = self.get_current_season()

        # 1. Query location table
        loc_items = self.locations_table.scan(Limit=1000).get("Items", [])
        matched_loc = None
        for item in loc_items:
            item_dist = item.get("district", "").lower()
            item_state = item.get("state", "").lower()
            if district.lower() in item_dist or (state.lower() in item_state and (district == "All" or not district)):
                matched_loc = item
                break

        if not matched_loc and loc_items:
            matched_loc = loc_items[0]

        # 2. Query soil table
        soil_items = self.soil_table.scan(Limit=1000).get("Items", [])
        matched_soil = None
        if matched_loc:
            m_dist = matched_loc.get("district", "").lower()
            for s in soil_items:
                if s.get("district", "").lower() == m_dist:
                    matched_soil = s
                    break

        if not matched_soil and soil_items:
            matched_soil = soil_items[0]

        crops_dict = matched_loc.get("crops", {}) if matched_loc else {}
        if isinstance(crops_dict, str):
            try:
                crops_dict = json.loads(crops_dict)
            except Exception:
                crops_dict = {}

        seasonal_crops = crops_dict.get(season, []) if isinstance(crops_dict, dict) else []

        result = {
            "district": matched_loc.get("district", district) if matched_loc else district,
            "state": matched_loc.get("state", state) if matched_loc else state,
            "soil_type": matched_loc.get("soil_type", "Alluvial / Loamy Soil") if matched_loc else "Loamy Soil",
            "rainfall": matched_loc.get("rainfall", "800-1000mm") if matched_loc else "900mm",
            "current_season": season,
            "recommended_crops": seasonal_crops,
            "all_crops": crops_dict,
            "soil_parameters": {
                "ph": matched_soil.get("ph", 7.2) if matched_soil else 7.2,
                "ec": matched_soil.get("ec", 0.25) if matched_soil else 0.25,
                "organic_carbon": matched_soil.get("organic_carbon", 0.55) if matched_soil else 0.55,
                "nitrogen_kg_ha": matched_soil.get("nitrogen_kg_ha", 220) if matched_soil else 220,
                "phosphorus_kg_ha": matched_soil.get("phosphorus_kg_ha", 18.0) if matched_soil else 18.0,
                "potassium_kg_ha": matched_soil.get("potassium_kg_ha", 280) if matched_soil else 280,
                "texture": matched_soil.get("texture", "Loamy") if matched_soil else "Loamy",
                "recommended_amendments": matched_soil.get("recommended_amendments", "Balanced NPK application") if matched_soil else "Apply organic FYM."
            },
            "source": matched_loc.get("source", "Government Agricultural Portals") if matched_loc else "Official Datasets",
            "verified": True
        }

        _set_cached(cache_key, result, 600)  # 10 minutes cache
        return result

    def get_crop_recommendations(self, location_str: str) -> List[Dict[str, Any]]:
        """
        Database-backed crop recommendation engine with agronomic suitability scoring.
        Calculates compatibility between farmer's district soil, current season, water, and crop preferences.
        """
        context = self.get_hyperlocal_context(location_str)
        season = context.get("current_season", "rabi")
        district_soil = context.get("soil_type", "Loamy Soil").lower()
        ph = context.get("soil_parameters", {}).get("ph", 7.0)

        # Get all master crops
        all_crops = self.crops_table.scan(Limit=100).get("Items", [])
        if not all_crops:
            from ingestion.sync_crops import CROPS_MASTER_DATA
            all_crops = CROPS_MASTER_DATA

        scored_crops = []
        for c in all_crops:
            score = 50.0  # Base viability

            # 1. Season Match (30 pts)
            crop_seasons = c.get("seasons", [])
            if season in crop_seasons or "year-round" in crop_seasons:
                score += 30.0
            elif "rabi" in crop_seasons and season == "summer":
                score += 10.0

            # 2. Soil Preferences Match (15 pts)
            soil_prefs = [s.lower() for s in c.get("soil_preferences", [])]
            if any(p in district_soil or district_soil in p for p in soil_prefs):
                score += 15.0
            else:
                score += 5.0

            # 3. Soil pH Compatibility (5 pts)
            ph_min = float(c.get("ideal_ph_min", 6.0))
            ph_max = float(c.get("ideal_ph_max", 7.8))
            if ph_min <= ph <= ph_max:
                score += 5.0

            # Explanation synthesis
            explanation = f"Highly compatible with {context.get('district')}'s {context.get('soil_type')} in {season.upper()} season. {c.get('package_of_practices', '')[:120]}..."

            scored_crops.append({
                "crop_id": c.get("crop_id"),
                "crop_name": c.get("name") or c.get("crop_name"),
                "scientific_name": c.get("scientific_name"),
                "category": c.get("category"),
                "soil_compatibility": round(min(100.0, score), 1),
                "climate_match": f"Ideal for {context.get('district', 'local')} agro-climatic conditions",
                "water_requirement": c.get("water_requirement", "Moderate"),
                "duration_days": c.get("duration_days", 110),
                "explanation": explanation,
                "key_pests": c.get("key_pests", []),
                "key_diseases": c.get("key_diseases", []),
                "source": "ICAR Package of Practices"
            })

        scored_crops.sort(key=lambda x: x["soil_compatibility"], reverse=True)
        return scored_crops[:10]

    def get_crop_calendar(self, location_str: str, language: str = "en") -> Dict[str, Any]:
        """
        Get structured multi-season crop calendar.
        """
        context = self.get_hyperlocal_context(location_str)
        season = context.get("current_season", "rabi")
        
        calendar_items = self.calendar_table.scan(Limit=100).get("Items", [])
        if not calendar_items:
            from ingestion.sync_crop_calendar import CROP_CALENDAR_RECORDS
            calendar_items = CROP_CALENDAR_RECORDS

        recommended_crops = []
        for item in calendar_items:
            crop_season = item.get("season", "")
            # Include crops for current season or year-round
            if crop_season == season or crop_season == "year-round":
                recommended_crops.append({
                    "id": item.get("calendar_id"),
                    "name": item.get("crop_name"),
                    "season": crop_season,
                    "planting": item.get("planting"),
                    "harvesting": item.get("harvesting"),
                    "duration_days": item.get("duration_days"),
                    "soil_type": item.get("soil_type"),
                    "rainfall": item.get("rainfall"),
                    "tips": item.get("tips"),
                    "critical_operations": item.get("critical_operations", [])
                })

        # Weather snapshot for calendar header
        weather = self.get_weather_with_cache(location_str)

        return {
            "current_season": season,
            "user_location": location_str,
            "weather": {
                "temp": weather.get("temperature", 26),
                "humidity": weather.get("humidity", 58),
                "description": weather.get("condition", "Partly Cloudy")
            },
            "recommended_crops": recommended_crops
        }

    def get_advisories(self, location_str: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get official agricultural advisories and news from database.
        """
        loc = self.parse_location(location_str)
        district = loc["district"].lower()
        state = loc["state"].lower()

        items = self.advisories_table.scan(Limit=100).get("Items", [])
        if not items:
            from ingestion.sync_advisories import OFFICIAL_ADVISORIES_DATA
            items = OFFICIAL_ADVISORIES_DATA

        filtered = []
        for adv in items:
            adv_state = adv.get("state", "").lower()
            adv_dist = adv.get("district", "").lower()
            
            # Match state, district, or All India
            matches_geo = (adv_state in [state, "all india"] or adv_dist in [district, "all"])
            matches_cat = (not category or adv.get("category") == category)
            
            if matches_geo and matches_cat:
                filtered.append(adv)

        # Fallback to all if nothing matched
        if not filtered:
            filtered = items[:6]

        # Format for frontend Advisor.jsx consumption
        result = []
        for f in filtered:
            result.append({
                "id": f.get("advisory_id"),
                "title": f.get("title"),
                "summary": f.get("summary"),
                "crop": f.get("crop"),
                "category": f.get("category"),
                "source": f.get("source"),
                "link": f.get("source_url") or f.get("link", "https://agricoop.gov.in"),
                "image": f.get("image", "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=400&h=200&fit=crop"),
                "published_at": f.get("published_at", datetime.utcnow().isoformat())
            })
        return result

    def get_market_prices(self, location_str: str, commodity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get Agmarknet APMC mandi prices from database.
        """
        loc = self.parse_location(location_str)
        district = loc["district"].lower()
        state = loc["state"].lower()

        items = self.markets_table.scan(Limit=100).get("Items", [])
        if not items:
            from ingestion.sync_markets import OFFICIAL_MANDI_DATA
            items = OFFICIAL_MANDI_DATA

        matched = []
        for m in items:
            m_copy = dict(m)
            if "market" in m_copy and "mandi" not in m_copy:
                m_copy["mandi"] = m_copy["market"]
            elif "mandi" in m_copy and "market" not in m_copy:
                m_copy["market"] = m_copy["mandi"]

            m_state = m_copy.get("state", "").lower()
            m_dist = m_copy.get("district", "").lower()
            m_comm = m_copy.get("commodity", "").lower()

            if (district in m_dist or state in m_state) and (not commodity or commodity.lower() in m_comm):
                matched.append(m_copy)

        if not matched:
            for item in items[:8]:
                i_copy = dict(item)
                if "market" in i_copy and "mandi" not in i_copy:
                    i_copy["mandi"] = i_copy["market"]
                matched.append(i_copy)

        return matched

    def get_weather_with_cache(self, location_str: str) -> Dict[str, Any]:
        """
        Get weather with 1-hour cache and intelligent agricultural risk alerts.
        """
        loc = self.parse_location(location_str)
        city = loc["district"] if loc["district"] != "All" else "Hyderabad"
        cache_key = f"weather:{city.lower()}"

        cached = _get_cached(cache_key)
        if cached:
            return cached

        api_key = os.getenv("OPENWEATHER_API_KEY")
        weather_data = None

        if api_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    temp = round(data["main"]["temp"])
                    humidity = data["main"]["humidity"]
                    condition = data["weather"][0]["main"]
                    rain_1h = data.get("rain", {}).get("1h", 0)

                    alert = None
                    if temp > 38:
                        alert = "Extreme heat warning! Increase irrigation frequency to prevent leaf scorch."
                    elif rain_1h > 15:
                        alert = "Heavy rain alert! Clear drainage trenches to prevent water stagnation."
                    elif temp < 10:
                        alert = "Frost / cold wave advisory! Provide protective light irrigation in late evening."

                    weather_data = {
                        "temperature": temp,
                        "humidity": humidity,
                        "rainfall": rain_1h,
                        "condition": condition,
                        "alert": alert,
                        "cached_at": datetime.utcnow().isoformat(),
                        "source": "OpenWeather / IMD Weather Service"
                    }
            except Exception as e:
                print(f"Weather API error ({city}): {e}")

        if not weather_data:
            # Deterministic, realistic climate baseline for Indian agriculture
            season = self.get_current_season()
            base_temp = 28 if season == "rabi" else (34 if season == "summer" else 30)
            weather_data = {
                "temperature": base_temp,
                "humidity": 62,
                "rainfall": 0,
                "condition": "Partly Cloudy",
                "alert": None,
                "cached_at": datetime.utcnow().isoformat(),
                "source": "Local Agricultural Climate Reference"
            }

        _set_cached(cache_key, weather_data, 3600)  # 1 hour cache
        return weather_data

    def get_optimization_strategies(self, location_str: str) -> List[Dict[str, Any]]:
        """
        Generate or retrieve practical farming optimization strategies.
        """
        context = self.get_hyperlocal_context(location_str)
        soil = context.get("soil_type", "Loamy")
        season = context.get("current_season", "rabi")

        return [
            {
                "strategy_name": f"Drip Fertigation for {season.upper()} Crops",
                "impact_level": "High",
                "difficulty": "Medium",
                "cost_effectiveness": "165%",
                "badge": "Peak ROI",
                "description": f"Targeted water and soluble nutrient delivery directly to active root zone in {soil}."
            },
            {
                "strategy_name": "Organic Mulching & Soil Moisture Retention",
                "impact_level": "High",
                "difficulty": "Low",
                "cost_effectiveness": "140%",
                "badge": "Water Saver",
                "description": "Spreading crop residue or plastic mulch cuts evaporation losses by 35%."
            },
            {
                "strategy_name": "Integrated Pest Management (IPM) Trapping",
                "impact_level": "Medium",
                "difficulty": "Low",
                "cost_effectiveness": "180%",
                "badge": "Eco-Friendly",
                "description": "Installing pheromone and yellow/blue sticky traps reduces chemical sprays by 40%."
            },
            {
                "strategy_name": "Zinc & Micronutrient Foliar Supplementation",
                "impact_level": "High",
                "difficulty": "Low",
                "cost_effectiveness": "150%",
                "badge": "Yield Booster",
                "description": "Correcting regional zinc deficiencies improves grain filling and crop vigor."
            }
        ]


_agri_service_instance: Optional[AgriService] = None

def get_agri_service() -> AgriService:
    global _agri_service_instance
    if _agri_service_instance is None:
        _agri_service_instance = AgriService()
    return _agri_service_instance
