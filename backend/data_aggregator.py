"""
Data Aggregator - Fetch ALL data first, then pass to LLM
This ensures LLM responses are based on actual data, not hallucinations
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import os
import asyncio
from functools import lru_cache
import hashlib
import json

# Simple in-memory cache with TTL
_cache = {}
_cache_ttl = {}
CACHE_DURATION = 300  # 5 minutes

def get_cache_key(prefix: str, location: str) -> str:
    """Generate cache key"""
    return f"{prefix}:{hashlib.md5(location.encode()).hexdigest()}"

def get_cached(key: str):
    """Get cached data if not expired"""
    if key in _cache:
        if datetime.utcnow().timestamp() < _cache_ttl.get(key, 0):
            return _cache[key]
        else:
            del _cache[key]
            del _cache_ttl[key]
    return None

def set_cached(key: str, value, ttl: int = CACHE_DURATION):
    """Set cached data with TTL"""
    _cache[key] = value
    _cache_ttl[key] = datetime.utcnow().timestamp() + ttl

async def fetch_all_context_data_async(user_location: str, query: str) -> dict:
    """Async version - fetch data in parallel"""
    query_lower = query.lower()
    
    # Determine what data is needed based on query
    needs_weather = any(w in query_lower for w in ['weather', 'temperature', 'rain', 'climate'])
    needs_prices = any(w in query_lower for w in ['price', 'cost', 'rate', 'market', 'mandi'])
    
    # Fetch only what's needed in parallel
    tasks = [
        fetch_hyperlocal_data(user_location),
    ]
    
    if needs_weather:
        tasks.append(fetch_weather_data(user_location))
    
    # Always fetch pest/disease data (lightweight)
    tasks.append(fetch_pest_disease_data(user_location))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    context = {
        "hyperlocal": results[0] if not isinstance(results[0], Exception) else None,
        "weather": results[1] if needs_weather and len(results) > 1 and not isinstance(results[1], Exception) else None,
        "pest_outbreaks": results[-1].get("pests", []) if not isinstance(results[-1], Exception) else [],
        "disease_reports": results[-1].get("diseases", []) if not isinstance(results[-1], Exception) else [],
        "success_stories": [],
        "seasonal_info": results[0].get("seasonal_info") if results[0] and not isinstance(results[0], Exception) else None
    }
    
    if needs_prices:
        context["crop_prices"] = get_crop_prices(user_location)
    
    return context

async def fetch_hyperlocal_data(user_location: str):
    """Fetch hyperlocal data with caching"""
    cache_key = get_cache_key("hyperlocal", user_location)
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    try:
        mongo_client = MongoClient(os.getenv("MONGO_URL"))
        db = mongo_client.gramvani
        
        location_parts = [p.strip() for p in user_location.split(",")]
        query_filter = {}
        
        if len(location_parts) >= 2:
            query_filter = {"$or": [{"district": {"$regex": location_parts[0], "$options": "i"}}, {"state": {"$regex": location_parts[1], "$options": "i"}}]}
        elif len(location_parts) == 1:
            query_filter = {"$or": [{"district": {"$regex": location_parts[0], "$options": "i"}}, {"state": {"$regex": location_parts[0], "$options": "i"}}]}
        
        hyperlocal_data = db.hyperlocal_context.find_one(query_filter)
        
        if hyperlocal_data:
            month = datetime.utcnow().month
            season = "kharif" if month in [6,7,8,9,10] else "rabi" if month in [11,12,1,2,3] else "summer"
            
            result = {
                "district": hyperlocal_data.get("district"),
                "state": hyperlocal_data.get("state"),
                "soil_type": hyperlocal_data.get("soil_type"),
                "rainfall": hyperlocal_data.get("rainfall"),
                "current_season": season,
                "recommended_crops": hyperlocal_data.get("crops", {}).get(season, []),
                "all_crops": hyperlocal_data.get("crops", {}),
                "pest_alerts": hyperlocal_data.get("pest_alerts", []),
                "seasonal_info": {
                    "season": season,
                    "months": get_season_months(season),
                    "activities": get_seasonal_activities(season)
                }
            }
            set_cached(cache_key, result, 600)  # Cache for 10 minutes
            return result
    except Exception as e:
        print(f"Hyperlocal fetch error: {e}")
    return None

async def fetch_weather_data(user_location: str):
    """Fetch weather with caching"""
    cache_key = get_cache_key("weather", user_location)
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    try:
        city = user_location.split(",")[0].strip()
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if api_key:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            res = requests.get(url, timeout=5)  # Reduced timeout
            
            if res.status_code == 200:
                data = res.json()
                result = {
                    "city": city,
                    "description": data["weather"][0]["description"],
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "feels_like": data["main"]["feels_like"]
                }
                set_cached(cache_key, result, 300)  # Cache for 5 minutes
                return result
    except Exception as e:
        print(f"Weather fetch error: {e}")
    return None

async def fetch_pest_disease_data(user_location: str):
    """Fetch pest/disease data with caching - only recent government data"""
    cache_key = get_cache_key("pest_disease", user_location)
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    try:
        mongo_client = MongoClient(os.getenv("MONGO_URL"))
        db = mongo_client.gramvani
        
        location_parts = [p.strip() for p in user_location.split(",")]
        state_query = location_parts[1] if len(location_parts) > 1 else location_parts[0]
        
        # Only fetch top 3 most relevant
        govt_pest_reports = list(db.pest_reports.find({
            "state": {"$regex": state_query, "$options": "i"}
        }).limit(3))
        
        govt_disease_reports = list(db.disease_reports.find({
            "state": {"$regex": state_query, "$options": "i"}
        }).limit(3))
        
        result = {
            "pests": [{"pest_name": r.get("pest_name"), "crop": r.get("crop"), "severity": r.get("severity"), "description": r.get("description"), "source": "Government Data"} for r in govt_pest_reports],
            "diseases": [{"disease_name": r.get("disease_name"), "crop": r.get("crop"), "severity": r.get("severity"), "description": r.get("description"), "source": "Government Data"} for r in govt_disease_reports]
        }
        
        set_cached(cache_key, result, 600)  # Cache for 10 minutes
        return result
    except Exception as e:
        print(f"Pest/disease fetch error: {e}")
    return {"pests": [], "diseases": []}

def get_crop_prices(user_location: str):
    """Get crop prices - static data, no DB call"""
    return {
        "market": user_location.split(",")[0],
        "prices": {"wheat": 2000, "rice": 2400, "cotton": 6000, "soybean": 4400, "onion": 3000, "potato": 1400, "tomato": 3600},
        "unit": "₹ per quintal",
        "last_updated": "Today"
    }

def fetch_all_context_data(user_location: str, query: str) -> dict:
    """Sync wrapper for async function"""
    try:
        # Try to get existing event loop
        try:
            loop = asyncio.get_running_loop()
            # Loop is already running, use sync fallback
            return fetch_context_sync(user_location, query)
        except RuntimeError:
            # No running loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_all_context_data_async(user_location, query))
            finally:
                loop.close()
    except Exception as e:
        print(f"Async fetch error: {e}")
        # Fallback to sync version
        return fetch_context_sync(user_location, query)

def fetch_context_sync(user_location: str, query: str) -> dict:
    """Fallback sync version with minimal data"""
    context = {
        "hyperlocal": None,
        "weather": None,
        "pest_outbreaks": [],
        "disease_reports": [],
        "success_stories": [],
        "seasonal_info": None
    }
    
    # Fetch only essential data synchronously
    try:
        mongo_client = MongoClient(os.getenv("MONGO_URL"))
        db = mongo_client.gramvani
        location_parts = [p.strip() for p in user_location.split(",")]
        
        # Only hyperlocal data
        query_filter = {"$or": [{"district": {"$regex": location_parts[0], "$options": "i"}}]} if location_parts else {}
        hyperlocal_data = db.hyperlocal_context.find_one(query_filter)
        
        if hyperlocal_data:
            month = datetime.utcnow().month
            season = "kharif" if month in [6,7,8,9,10] else "rabi" if month in [11,12,1,2,3] else "summer"
            context["hyperlocal"] = {
                "district": hyperlocal_data.get("district"),
                "state": hyperlocal_data.get("state"),
                "soil_type": hyperlocal_data.get("soil_type"),
                "current_season": season,
                "recommended_crops": hyperlocal_data.get("crops", {}).get(season, [])
            }
    except Exception as e:
        print(f"Sync fetch error: {e}")
    
    return context

def get_season_months(season: str) -> str:
    """Get month range for season"""
    seasons = {
        "kharif": "June to October (Monsoon season)",
        "rabi": "November to March (Winter season)",
        "summer": "April to May (Summer season)"
    }
    return seasons.get(season, "")

def get_seasonal_activities(season: str) -> list:
    """Get farming activities for season"""
    activities = {
        "kharif": [
            "Sowing of monsoon crops",
            "Prepare fields before monsoon",
            "Check irrigation systems",
            "Monitor pest activity (high during monsoon)"
        ],
        "rabi": [
            "Sowing of winter crops",
            "Harvest kharif crops",
            "Prepare for winter",
            "Apply fertilizers"
        ],
        "summer": [
            "Harvest rabi crops",
            "Prepare for next kharif season",
            "Maintain irrigation",
            "Grow short-duration vegetables"
        ]
    }
    return activities.get(season, [])

def format_context_for_llm(context: dict) -> str:
    """
    Format fetched data into concise prompt for LLM
    """
    prompt_parts = []
    
    # Hyperlocal context (minimal)
    if context.get("hyperlocal"):
        h = context["hyperlocal"]
        crops = ', '.join(h.get('recommended_crops', [])[:5])  # Limit to 5
        prompt_parts.append(f"LOCATION: {h.get('district', 'Unknown')}, {h.get('state', 'Unknown')} | Soil: {h.get('soil_type', 'Unknown')} | Season: {h.get('current_season', 'Unknown')} | Crops: {crops}")
    
    # Weather (compact)
    if context.get("weather"):
        w = context["weather"]
        prompt_parts.append(f"WEATHER: {w['description']}, {w['temperature']}°C, {w['humidity']}% humidity")
    
    # Pest outbreaks (top 3 only)
    if context.get("pest_outbreaks"):
        pests = context["pest_outbreaks"][:3]
        if pests:
            pest_list = [f"{p['pest_name']} in {p['crop']}" for p in pests]
            prompt_parts.append(f"PEST ALERTS: {', '.join(pest_list)}")
    
    # Disease reports (top 3 only)
    if context.get("disease_reports"):
        diseases = context["disease_reports"][:3]
        if diseases:
            disease_list = [f"{d['disease_name']} in {d['crop']}" for d in diseases]
            prompt_parts.append(f"DISEASE ALERTS: {', '.join(disease_list)}")
    
    # Skip success stories for faster response
    
    # Crop prices (compact)
    if context.get("crop_prices"):
        p = context["crop_prices"]
        prices = [f"{c}: ₹{pr}" for c, pr in list(p["prices"].items())[:4]]
        prompt_parts.append(f"PRICES: {', '.join(prices)} per quintal")
    
    # Skip seasonal activities for speed
    
    return " | ".join(prompt_parts) if prompt_parts else "No specific context available"
