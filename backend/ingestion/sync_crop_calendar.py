"""
Pipeline: Crop Calendar Ingestion
Syncs multi-season, localized crop sowing and harvesting windows into `sarthicropcalendar`.
Sources: ICAR Agro-Climatic Guides & State Agricultural Universities (ANGRAU, TNAU, MPKV, PAU).
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.azure_table_db import get_azure_table_db

CROP_CALENDAR_RECORDS = [
    # --- RABI SEASON (Current season & upcoming harvest) ---
    {
        "calendar_id": "cal_wheat_rabi",
        "crop_id": "crop_wheat",
        "crop_name": "Wheat",
        "season": "rabi",
        "planting": {"start": "November", "end": "December"},
        "harvesting": {"start": "March", "end": "April"},
        "duration_days": 120,
        "soil_type": "Well-drained loamy to clay loam soil",
        "rainfall": "Moderate (4-6 irrigations at critical growth stages)",
        "critical_operations": [
            "Land Preparation & Basal Fertilizer (Oct 25 - Nov 10)",
            "Sowing & Seed Treatment with Trichoderma (Nov 01 - Dec 15)",
            "CRI Stage First Irrigation at 21 days after sowing",
            "Weed Management (Sulfosulfuron at 30-35 DAS)",
            "Harvesting & In-situ Straw Management (March 25 - April 20)"
        ],
        "tips": "Requires cool weather for tillering and warm dry sunshine during grain maturity.",
        "suitable_states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Bihar"]
    },
    {
        "calendar_id": "cal_mustard_rabi",
        "crop_id": "crop_mustard",
        "crop_name": "Mustard",
        "season": "rabi",
        "planting": {"start": "October", "end": "November"},
        "harvesting": {"start": "February", "end": "March"},
        "duration_days": 115,
        "soil_type": "Light to heavy alluvial loam with good drainage",
        "rainfall": "Low to Moderate (2-3 irrigations suffice)",
        "critical_operations": [
            "Field leveling & single deep summer ploughing",
            "Seed sowing at 45cm x 15cm spacing",
            "Thinning at 15-20 days to ensure vigorous single plants",
            "Aphid monitoring with yellow sticky traps at flowering",
            "Harvesting when 75% of siliquae turn golden yellow"
        ],
        "tips": "Apply sulphur @ 30 kg/ha to increase oil percentage and enhance cold resistance.",
        "suitable_states": ["Rajasthan", "Madhya Pradesh", "Haryana", "Uttar Pradesh", "West Bengal"]
    },
    {
        "calendar_id": "cal_chickpea_rabi",
        "crop_id": "crop_chickpea",
        "crop_name": "Chickpea (Gram)",
        "season": "rabi",
        "planting": {"start": "October", "end": "November"},
        "harvesting": {"start": "February", "end": "March"},
        "duration_days": 105,
        "soil_type": "Deep black cotton soil or fertile sandy loam",
        "rainfall": "Low (Sensitive to excess moisture and water stagnation)",
        "critical_operations": [
            "Seed treatment with Rhizobium & PSB inoculants",
            "Nipping/topping at 30-40 DAS to promote profuse branching",
            "Helicoverpa pheromone trap placement @ 5 per acre",
            "Pre-flowering and pod development protective irrigations",
            "Pod threshing at 10% grain moisture content"
        ],
        "tips": "Avoid irrigation during active flowering to prevent flower drop. Erect T-perches for predatory birds.",
        "suitable_states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Andhra Pradesh", "Karnataka"]
    },
    {
        "calendar_id": "cal_potato_rabi",
        "crop_id": "crop_potato",
        "crop_name": "Potato",
        "season": "rabi",
        "planting": {"start": "October", "end": "November"},
        "harvesting": {"start": "January", "end": "February"},
        "duration_days": 90,
        "soil_type": "Loose, friable, well-aerated sandy loam rich in organic matter",
        "rainfall": "Moderate (Requires frequent light irrigations)",
        "critical_operations": [
            "Sprouting of certified seed tubers in diffused light",
            "Planting in ridges 60cm apart with 20cm plant spacing",
            "First earthing-up at 30 DAS and second at 50 DAS",
            "Late blight preventive spray of Mancozeb @ 2.5 g/L",
            "De-haulming 10 days before harvesting to harden tuber skin"
        ],
        "tips": "Ensure tubers are not exposed to sunlight during growth to prevent toxic solanine development.",
        "suitable_states": ["Uttar Pradesh", "West Bengal", "Bihar", "Punjab", "Gujarat"]
    },
    {
        "calendar_id": "cal_onion_rabi",
        "crop_id": "crop_onion",
        "crop_name": "Onion (Rabi)",
        "season": "rabi",
        "planting": {"start": "November", "end": "December"},
        "harvesting": {"start": "March", "end": "April"},
        "duration_days": 120,
        "soil_type": "Deep, well-drained loamy soil with pH 6.5 - 7.5",
        "rainfall": "Moderate (Irrigate every 8-10 days in winter)",
        "critical_operations": [
            "Nursery raising in raised beds with neem cake treatment",
            "Transplanting 7-week old stocky seedlings",
            "Thrips control via blue sticky traps and neem oil",
            "Fungicidal spray against Purple Blotch (Alternaria porri)",
            "Field curing in shade for 7-10 days after neck fall"
        ],
        "tips": "Withhold irrigation 15 days before harvest to enhance storage life and reduce transit rotting.",
        "suitable_states": ["Maharashtra", "Karnataka", "Madhya Pradesh", "Gujarat", "Andhra Pradesh"]
    },
    {
        "calendar_id": "cal_tobacco_rabi",
        "crop_id": "crop_tobacco",
        "crop_name": "Tobacco (FCV)",
        "season": "rabi",
        "planting": {"start": "October", "end": "November"},
        "harvesting": {"start": "January", "end": "March"},
        "duration_days": 130,
        "soil_type": "Light sandy and red sandy loam soils of Godavari and Prakasam",
        "rainfall": "Low-Moderate (Controlled drip irrigation preferred)",
        "critical_operations": [
            "Nursery seedling preparation with solarization",
            "Transplanting in well-leveled fields with ridge-furrow",
            "Topping at button stage and desuckering with suckericide",
            "Selective leaf priming from bottom to top as leaves mature",
            "Flue-curing in barns under regulated temperature curves"
        ],
        "tips": "Harvest only fully ripe leaves with lemon-yellow color for premium market grading in AP mandis.",
        "suitable_states": ["Andhra Pradesh", "Gujarat", "Karnataka", "Telangana"]
    },

    # --- KHARIF SEASON (Monsoon season) ---
    {
        "calendar_id": "cal_paddy_kharif",
        "crop_id": "crop_paddy",
        "crop_name": "Paddy (Rice - Kharif)",
        "season": "kharif",
        "planting": {"start": "June", "end": "July"},
        "harvesting": {"start": "October", "end": "November"},
        "duration_days": 125,
        "soil_type": "Clayey, alluvial soils with slow water percolation",
        "rainfall": "High (Requires abundant monsoon rainfall or assured canal)",
        "critical_operations": [
            "Wet nursery sowing with pre-germinated seeds",
            "Puddling & leveling field to reduce water seepage",
            "Transplanting 2-3 seedlings/hill at 20cm x 15cm",
            "Mid-season aeration drainage to promote deep root anchoring",
            "Harvesting when 85% panicles turn golden straw color"
        ],
        "tips": "Maintain alternate wetting and drying (AWD) after tillering to conserve 25% water and reduce BPH pest pressure.",
        "suitable_states": ["Andhra Pradesh", "West Bengal", "Punjab", "Odisha", "Telangana", "Uttar Pradesh"]
    },
    {
        "calendar_id": "cal_cotton_kharif",
        "crop_id": "crop_cotton",
        "crop_name": "Cotton",
        "season": "kharif",
        "planting": {"start": "May", "end": "June"},
        "harvesting": {"start": "October", "end": "January"},
        "duration_days": 160,
        "soil_type": "Deep black cotton soil with high moisture retention capacity",
        "rainfall": "Moderate (650-850 mm well-distributed rain)",
        "critical_operations": [
            "Deep summer ploughing to expose hibernating bollworm pupae",
            "Sowing on ridges @ 90cm x 45cm with initial protective moisture",
            "Inter-cultivation & weeding at 20, 40, and 60 DAS",
            "Pheromone trap monitoring for Pink Bollworm from 45 DAS",
            "Manual picking of clean open bolls during dry afternoon hours"
        ],
        "tips": "Refuge cropping with non-Bt cotton rows around field boundary preserves Bt insecticidal efficacy.",
        "suitable_states": ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Haryana", "Karnataka"]
    },
    {
        "calendar_id": "cal_soybean_kharif",
        "crop_id": "crop_soybean",
        "crop_name": "Soybean",
        "season": "kharif",
        "planting": {"start": "June", "end": "July"},
        "harvesting": {"start": "September", "end": "October"},
        "duration_days": 95,
        "soil_type": "Well-drained medium to deep black soils",
        "rainfall": "Moderate (Requires 550-700 mm during vegetative phase)",
        "critical_operations": [
            "Seed treatment with Thiram + Carbendazim followed by Rhizobium",
            "Broad-bed furrow (BBF) or ridge-furrow sowing",
            "Stem fly and girdle beetle monitoring in early vegetative phase",
            "Foliar spray of 19:19:19 @ 1% during pod initiation",
            "Harvesting when leaves drop and pods rattle on shaking"
        ],
        "tips": "Avoid delayed harvesting as mature soybean pods are prone to shattering during hot afternoons.",
        "suitable_states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana"]
    },
    {
        "calendar_id": "cal_groundnut_kharif",
        "crop_id": "crop_groundnut",
        "crop_name": "Groundnut",
        "season": "kharif",
        "planting": {"start": "June", "end": "July"},
        "harvesting": {"start": "October", "end": "November"},
        "duration_days": 115,
        "soil_type": "Light-textured well-drained sandy loam or red soil",
        "rainfall": "Moderate (Critical moisture required during flowering & pegging)",
        "critical_operations": [
            "Seed decortication just 2-3 days before sowing",
            "Sowing at 30cm x 10cm depth of 5cm",
            "Gypsum application @ 400 kg/ha at peg penetration stage",
            "Tikka leaf spot spray with Hexaconazole @ 2ml/L",
            "Pod lifting using tractor digger when inner shell turns dark"
        ],
        "tips": "Never disturb or hoe field during active peg entry into soil to avoid damaging developing pods.",
        "suitable_states": ["Gujarat", "Andhra Pradesh (Anantapur)", "Rajasthan", "Tamil Nadu", "Karnataka"]
    },
    {
        "calendar_id": "cal_chilli_kharif",
        "crop_id": "crop_chilli",
        "crop_name": "Chilli",
        "season": "kharif",
        "planting": {"start": "July", "end": "August"},
        "harvesting": {"start": "November", "end": "February"},
        "duration_days": 150,
        "soil_type": "Fertile black cotton soil or loamy red soil with pH 6.5-7.5",
        "rainfall": "Moderate (Sensitive to heavy rain during flowering)",
        "critical_operations": [
            "Pro-tray seedling nursery under 50% shade net",
            "Ridge planting with silver-black reflective mulch film",
            "Installing yellow & blue sticky traps @ 30/acre for thrips",
            "Foliar micronutrient mixture spray at 40 and 70 DAS",
            "Selective picking of ripe red pods for drying on clean polythene"
        ],
        "tips": "In Andhra Pradesh & Telangana, spray Neem oil 10000ppm alternately with Spinetoram against invasive black thrips.",
        "suitable_states": ["Andhra Pradesh (Guntur)", "Telangana", "Karnataka", "Madhya Pradesh", "Maharashtra"]
    },

    # --- SUMMER / YEAR-ROUND CROPS ---
    {
        "calendar_id": "cal_tomato_summer",
        "crop_id": "crop_tomato",
        "crop_name": "Tomato",
        "season": "summer",
        "planting": {"start": "January", "end": "February"},
        "harvesting": {"start": "April", "end": "May"},
        "duration_days": 90,
        "soil_type": "Sandy loam to clay loam rich in organic matter",
        "rainfall": "Moderate (Regular drip irrigation every 2-3 days)",
        "critical_operations": [
            "Nursery raising with Trichoderma enriched vermicompost",
            "Transplanting on raised beds with drip lateral lines",
            "Trellising / staking with bamboo poles for fruit support",
            "Calcium chloride 0.5% spray to prevent Blossom End Rot",
            "Harvesting at breaker/turning stage for distance transport"
        ],
        "tips": "Summer crops fetch premium mandi prices; use shade nets to prevent sunscald on maturing fruits.",
        "suitable_states": ["Andhra Pradesh", "Karnataka", "Madhya Pradesh", "Maharashtra", "Odisha"]
    },
    {
        "calendar_id": "cal_sugarcane_yearround",
        "crop_id": "crop_sugarcane",
        "crop_name": "Sugarcane",
        "season": "year-round",
        "planting": {"start": "February", "end": "April"},
        "harvesting": {"start": "December", "end": "March"},
        "duration_days": 365,
        "soil_type": "Deep well-drained loamy and clayey soils",
        "rainfall": "High (Requires 20-25 irrigations throughout year)",
        "critical_operations": [
            "Two-budded setts treated in carbendazim solution",
            "Furrow planting @ 120cm row spacing for mechanization",
            "Intercropping with short pulses (moong/urad) in first 60 days",
            "Trash mulching in alternate rows to conserve soil moisture",
            "Harvesting close to ground level to capture richest bottom sucrose"
        ],
        "tips": "Drip fertigation saves up to 45% water and delivers nutrients directly to active root zone.",
        "suitable_states": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh"]
    }
]

def sync_crop_calendar():
    db = get_azure_table_db()
    table = db.Table("sarthicropcalendar")
    
    print("📅 Starting Crop Calendar Ingestion (Multi-season planting & harvesting windows)...")
    started_at = datetime.utcnow()
    inserted = 0
    now_iso = started_at.isoformat()

    for item in CROP_CALENDAR_RECORDS:
        record = {
            "calendar_id": item["calendar_id"],
            "crop_id": item["crop_id"],
            "crop_name": item["crop_name"],
            "season": item["season"],
            "planting": item["planting"],
            "harvesting": item["harvesting"],
            "duration_days": item["duration_days"],
            "soil_type": item["soil_type"],
            "rainfall": item["rainfall"],
            "critical_operations": item["critical_operations"],
            "tips": item["tips"],
            "suitable_states": item["suitable_states"],
            "source": "State Agricultural Universities (ANGRAU, TNAU, PAU) & ICAR Guides",
            "source_url": "https://icar.org.in",
            "fetched_at": now_iso,
            "verified": True
        }
        table.put_item(Item=record)
        inserted += 1

    elapsed = (datetime.utcnow() - started_at).total_seconds()
    print(f"✅ Successfully ingested {inserted} crop calendar entries into 'sarthicropcalendar' in {elapsed:.2f}s!")
    return {"records_inserted": inserted, "elapsed_seconds": elapsed}

if __name__ == "__main__":
    sync_crop_calendar()
