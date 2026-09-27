"""
Test Suite for Agricultural Data Recovery & Restoration
Tests: Location parsing, Hyperlocal Context (Soil, Weather, Season, Advisories, Mandi),
Crop Recommendations, Crop Calendar, Advisories, Market Prices, Strategies, and Outbreak Aggregation.
"""

import pytest
from services.agri_service import get_agri_service
from services.azure_table_db import AzureTableWrapper

@pytest.fixture
def agri():
    return get_agri_service()

# --- 1. LOCATION TESTS ---
def test_location_parsing(agri):
    guntur = agri.parse_location("Guntur, Andhra Pradesh")
    assert guntur["district"] == "Guntur"
    assert guntur["state"] == "Andhra Pradesh"

    sehore = agri.parse_location("Sehore, Madhya Pradesh")
    assert sehore["district"] == "Sehore"
    assert sehore["state"] == "Madhya Pradesh"

    default_loc = agri.parse_location("Unknown Location")
    assert default_loc["district"] is not None
    assert default_loc["state"] is not None

# --- 2. HYPERLOCAL CONTEXT (SOIL, LOCATION, SEASON) ---
def test_hyperlocal_context(agri):
    ctx = agri.get_hyperlocal_context("Guntur, Andhra Pradesh")
    assert ctx["district"] == "Guntur"
    assert ctx["state"] == "Andhra Pradesh"
    assert ctx["soil_type"] is not None
    assert ctx["current_season"] in ("kharif", "rabi", "summer")

    # Soil Ground Truth
    assert "soil_parameters" in ctx
    soil = ctx["soil_parameters"]
    assert soil["ph"] > 0
    assert soil["organic_carbon"] > 0
    assert soil["nitrogen_kg_ha"] > 0
    assert soil["phosphorus_kg_ha"] > 0
    assert soil["potassium_kg_ha"] > 0

    assert ctx["verified"] is True
    assert "source" in ctx

# --- 3. CROP RECOMMENDATIONS ENGINE ---
def test_crop_recommendations(agri):
    crops_guntur = agri.get_crop_recommendations("Guntur, Andhra Pradesh")
    assert len(crops_guntur) >= 3
    for crop in crops_guntur:
        assert "crop_name" in crop
        assert "soil_compatibility" in crop
        assert "water_requirement" in crop
        assert "duration_days" in crop
        assert "climate_match" in crop

    # Verify crops present
    names = [c["crop_name"] for c in crops_guntur]
    assert any("Chilli" in n or "Cotton" in n or "Paddy" in n or "Sorghum" in n for n in names)

def test_crop_recommendations_sehore(agri):
    crops_sehore = agri.get_crop_recommendations("Sehore, Madhya Pradesh")
    assert len(crops_sehore) >= 3
    names = [c["crop_name"] for c in crops_sehore]
    assert any("Wheat" in n or "Soybean" in n or "Gram" in n or "Mustard" in n or "Sorghum" in n for n in names)

# --- 4. CROP CALENDAR ---
def test_crop_calendar(agri):
    cal = agri.get_crop_calendar("Guntur, Andhra Pradesh", language="en")
    assert "current_season" in cal
    assert len(cal["recommended_crops"]) > 0
    first = cal["recommended_crops"][0]
    assert "name" in first
    assert "planting" in first
    assert "harvesting" in first
    assert "duration_days" in first

def test_crop_calendar_multilingual(agri):
    cal_hi = agri.get_crop_calendar("Sehore, Madhya Pradesh", language="hi")
    assert len(cal_hi["recommended_crops"]) > 0
    first = cal_hi["recommended_crops"][0]
    assert first["planting"]["start"] != ""

# --- 5. WEATHER & AGROMET WITH CACHING ---
def test_weather_with_cache(agri):
    w = agri.get_weather_with_cache("Guntur, Andhra Pradesh")
    assert "temperature" in w
    assert "humidity" in w
    assert "rainfall" in w
    assert "condition" in w
    assert "source" in w
    assert "cached_at" in w

# --- 6. ADVISORIES & SCHEMES ---
def test_advisories(agri):
    adv_list = agri.get_advisories("Guntur, Andhra Pradesh")
    assert len(adv_list) > 0
    for adv in adv_list:
        assert "title" in adv
        assert "summary" in adv
        assert "source" in adv

# --- 7. MARKET / MANDI PRICES ---
def test_market_prices_guntur(agri):
    prices = agri.get_market_prices("Guntur, Andhra Pradesh", commodity="Chilli")
    assert len(prices) > 0
    assert "Chilli" in prices[0]["commodity"]
    assert prices[0]["modal_price"] > 0
    assert prices[0]["mandi"] == "Guntur APMC"

def test_market_prices_all(agri):
    prices = agri.get_market_prices("India")
    assert len(prices) >= 5

# --- 8. OPTIMIZATION STRATEGIES ---
def test_optimization_strategies(agri):
    strat = agri.get_optimization_strategies("Guntur, Andhra Pradesh")
    assert len(strat) >= 3
    for s in strat:
        assert "strategy_name" in s
        assert "impact_level" in s
        assert "cost_effectiveness" in s

# --- 9. OUTBREAK AGGREGATION & COMMUNITY DATA ---
def test_community_outbreaks_clustering():
    table = AzureTableWrapper("sarthicommunityreports")
    reports = table.scan().get("Items", [])
    assert len(reports) >= 20
    
    # Check aggregation by village
    villages = {}
    for r in reports:
        v = r.get("village_id")
        villages[v] = villages.get(v, 0) + 1
    
    assert "Sehore" in villages
    assert villages["Sehore"] >= 2
    assert "Guntur" in villages
    assert villages["Guntur"] >= 2
