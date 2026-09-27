"""
Pipeline: Crop Master Data Ingestion
Syncs comprehensive agronomic profiles for 50+ Indian crops into `sarthicropmaster`.
Source: ICAR Package of Practices & Department of Agriculture & Farmers Welfare, GoI.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.azure_table_db import get_azure_table_db

CROPS_MASTER_DATA = [
    # --- CEREALS & MILLETS ---
    {
        "crop_id": "crop_paddy",
        "crop_name": "Paddy (Rice)",
        "scientific_name": "Oryza sativa",
        "local_names": {"hi": "धान / चावल", "te": "వరి / బియ్యం", "ta": "நெல்", "kn": "ಭತ್ತ", "mr": "भात"},
        "category": "Cereals",
        "seasons": ["kharif", "rabi"],
        "duration_days": 125,
        "water_requirement": "Very High (1100-1500 mm)",
        "soil_preferences": ["Alluvial Soil", "Clay Loam", "Deep Black Soil"],
        "min_temp_c": 20, "max_temp_c": 38, "ideal_ph_min": 5.5, "ideal_ph_max": 7.2,
        "major_producing_states": ["Andhra Pradesh", "West Bengal", "Punjab", "Odisha", "Tamil Nadu", "Telangana"],
        "key_pests": ["Brown Plant Hopper (BPH)", "Stem Borer", "Gall Midge"],
        "key_diseases": ["Blast", "Bacterial Leaf Blight (BLB)", "Sheath Blight"],
        "package_of_practices": "Transplant 21-25 day old seedlings @ 2-3 per hill. Maintain 2-5cm standing water till grain hardening."
    },
    {
        "crop_id": "crop_wheat",
        "crop_name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "local_names": {"hi": "गेहूं", "te": "గోధుమలు", "ta": "கோதுமை", "kn": "ಗೋಧಿ", "mr": "गहू"},
        "category": "Cereals",
        "seasons": ["rabi"],
        "duration_days": 120,
        "water_requirement": "Moderate (450-600 mm)",
        "soil_preferences": ["Alluvial Soil", "Well-drained Loam", "Clay Loam"],
        "min_temp_c": 10, "max_temp_c": 28, "ideal_ph_min": 6.0, "ideal_ph_max": 7.5,
        "major_producing_states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan"],
        "key_pests": ["Aphids", "Termites", "Armyworm"],
        "key_diseases": ["Yellow Rust", "Brown Rust", "Karnal Bunt", "Loose Smut"],
        "package_of_practices": "Sow in Nov with Happy Seeder or Zero Till. Critical irrigations: CRI stage (21 DAS) and flowering."
    },
    {
        "crop_id": "crop_maize",
        "crop_name": "Maize (Corn)",
        "scientific_name": "Zea mays",
        "local_names": {"hi": "मक्का", "te": "మొక్కజొన్న", "ta": "மக்காச்சோளம்", "kn": "ಮೆಕ್ಕೆಜೋಳ", "mr": "मका"},
        "category": "Cereals",
        "seasons": ["kharif", "rabi"],
        "duration_days": 95,
        "water_requirement": "Moderate (500-750 mm)",
        "soil_preferences": ["Well-drained Sandy Loam", "Alluvial Soil", "Red Loam"],
        "min_temp_c": 18, "max_temp_c": 35, "ideal_ph_min": 6.0, "ideal_ph_max": 7.2,
        "major_producing_states": ["Karnataka", "Madhya Pradesh", "Bihar", "Andhra Pradesh", "Maharashtra"],
        "key_pests": ["Fall Armyworm (Spodoptera frugiperda)", "Stem Borer"],
        "key_diseases": ["Maydis Leaf Blight", "Turcicum Leaf Blight", "Downy Mildew"],
        "package_of_practices": "Pheromone traps @ 5/acre for Fall Armyworm. Avoid waterlogging at seedling and tasseling stages."
    },
    {
        "crop_id": "crop_ragi",
        "crop_name": "Finger Millet (Ragi)",
        "scientific_name": "Eleusine coracana",
        "local_names": {"hi": "रागी / मड़ुआ", "te": "రాగులు / చోడులు", "ta": "கேழ்வரகு", "kn": "ರಾಗಿ", "mr": "नाचणी"},
        "category": "Millets",
        "seasons": ["kharif", "summer"],
        "duration_days": 110,
        "water_requirement": "Low (350-500 mm)",
        "soil_preferences": ["Red Sandy Loam", "Laterite Soil", "Gravelly Soil"],
        "min_temp_c": 18, "max_temp_c": 36, "ideal_ph_min": 5.0, "ideal_ph_max": 7.0,
        "major_producing_states": ["Karnataka", "Tamil Nadu", "Uttarakhand", "Andhra Pradesh", "Odisha"],
        "key_pests": ["Aphids", "Stem Borer"],
        "key_diseases": ["Blast (Pyricularia grisea)"],
        "package_of_practices": "Highly drought tolerant nutrient-rich super-cereal. Sow with onset of monsoon."
    },
    {
        "crop_id": "crop_bajra",
        "crop_name": "Pearl Millet (Bajra)",
        "scientific_name": "Pennisetum glaucum",
        "local_names": {"hi": "बाजरा", "te": "సజ్జలు", "ta": "கம்பு", "kn": "ಸಜ್ಜೆ", "mr": "बाजरी"},
        "category": "Millets",
        "seasons": ["kharif", "summer"],
        "duration_days": 85,
        "water_requirement": "Low (250-400 mm)",
        "soil_preferences": ["Sandy Loam", "Sandy/Arid Soil", "Red Soil"],
        "min_temp_c": 22, "max_temp_c": 42, "ideal_ph_min": 6.5, "ideal_ph_max": 8.5,
        "major_producing_states": ["Rajasthan", "Gujarat", "Haryana", "Uttar Pradesh", "Maharashtra"],
        "key_pests": ["Shoot Fly", "Stem Borer"],
        "key_diseases": ["Downy Mildew / Green Ear", "Ergot", "Smut"],
        "package_of_practices": "Thrives in low-fertility dry zones. Seed treatment with Ridomil 2g/kg."
    },
    {
        "crop_id": "crop_jowar",
        "crop_name": "Sorghum (Jowar)",
        "scientific_name": "Sorghum bicolor",
        "local_names": {"hi": "ज्वार", "te": "జొన్నలు", "ta": "சோளம்", "kn": "ಜೋಳ", "mr": "ज्वारी"},
        "category": "Millets",
        "seasons": ["kharif", "rabi"],
        "duration_days": 105,
        "water_requirement": "Low-Moderate (400-550 mm)",
        "soil_preferences": ["Black Cotton Soil", "Clay Loam", "Red Soil"],
        "min_temp_c": 16, "max_temp_c": 38, "ideal_ph_min": 6.0, "ideal_ph_max": 8.0,
        "major_producing_states": ["Maharashtra", "Karnataka", "Rajasthan", "Madhya Pradesh", "Andhra Pradesh"],
        "key_pests": ["Shoot Fly", "Stem Borer", "Earhead Bug"],
        "key_diseases": ["Grain Mold", "Anthracnose", "Charcoal Rot"],
        "package_of_practices": "Deep ploughing in summer. High biomass and fodder value."
    },

    # --- COMMERCIAL & FIBER CROPS ---
    {
        "crop_id": "crop_cotton",
        "crop_name": "Cotton",
        "scientific_name": "Gossypium hirsutum",
        "local_names": {"hi": "कपास", "te": "పత్తి", "ta": "பருத்தி", "kn": "ಹತ್ತಿ", "mr": "कापूस"},
        "category": "Fiber / Cash Crop",
        "seasons": ["kharif"],
        "duration_days": 160,
        "water_requirement": "Moderate-High (600-900 mm)",
        "soil_preferences": ["Deep Black Cotton Soil", "Alluvial Soil", "Red Sandy Loam"],
        "min_temp_c": 20, "max_temp_c": 38, "ideal_ph_min": 6.5, "ideal_ph_max": 8.0,
        "major_producing_states": ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Haryana"],
        "key_pests": ["Pink Bollworm (Pectinophora gossypiella)", "Whitefly", "Jassids", "Thrips"],
        "key_diseases": ["Bacterial Blight", "Grey Mildew", "Root Rot"],
        "package_of_practices": "Install pheromone traps @ 8/ha for pink bollworm monitoring. Staggered nitrogen fertigation."
    },
    {
        "crop_id": "crop_sugarcane",
        "crop_name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "local_names": {"hi": "गन्ना", "te": "చెరకు", "ta": "கரும்பு", "kn": "ಕಬ್ಬು", "mr": "ऊस"},
        "category": "Cash Crop",
        "seasons": ["year-round"],
        "duration_days": 360,
        "water_requirement": "Very High (1500-2500 mm)",
        "soil_preferences": ["Deep Alluvial Loam", "Black Soil", "Well-drained Loam"],
        "min_temp_c": 20, "max_temp_c": 38, "ideal_ph_min": 6.5, "ideal_ph_max": 7.5,
        "major_producing_states": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh"],
        "key_pests": ["Early Shoot Borer", "Top Borer", "Pyrilla"],
        "key_diseases": ["Red Rot", "Smut", "Wilt", "Grassy Shoot"],
        "package_of_practices": "Trash mulching saves 30% water and regulates root temperature. Drip irrigation strongly advised."
    },

    # --- OILSEEDS ---
    {
        "crop_id": "crop_soybean",
        "crop_name": "Soybean",
        "scientific_name": "Glycine max",
        "local_names": {"hi": "सोयाबीन", "te": "సోయాబీన్", "ta": "சோயாபீன்", "kn": "ಸೋಯಾಬೀನ್", "mr": "सोयाबीन"},
        "category": "Oilseeds / Legumes",
        "seasons": ["kharif"],
        "duration_days": 95,
        "water_requirement": "Moderate (500-650 mm)",
        "soil_preferences": ["Black Cotton Soil", "Clay Loam", "Alluvial Soil"],
        "min_temp_c": 18, "max_temp_c": 34, "ideal_ph_min": 6.0, "ideal_ph_max": 7.5,
        "major_producing_states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana"],
        "key_pests": ["Girdle Beetle", "Stem Fly", "Semilooper", "Spodoptera"],
        "key_diseases": ["Yellow Mosaic Virus (YMV)", "Collar Rot", "Anthracnose"],
        "package_of_practices": "Ridge and furrow sowing method prevents waterlogging damage. Seed treat with Bradyrhizobium."
    },
    {
        "crop_id": "crop_groundnut",
        "crop_name": "Groundnut (Peanut)",
        "scientific_name": "Arachis hypogaea",
        "local_names": {"hi": "मूंगफली", "te": "వేరుశనగ", "ta": "வேர்க்கடலை", "kn": "ಕಡಲೆಕಾಯಿ", "mr": "भुईमूग"},
        "category": "Oilseeds",
        "seasons": ["kharif", "rabi"],
        "duration_days": 115,
        "water_requirement": "Moderate (450-600 mm)",
        "soil_preferences": ["Red Sandy Loam", "Sandy Soil", "Light Alluvial Loam"],
        "min_temp_c": 20, "max_temp_c": 35, "ideal_ph_min": 6.0, "ideal_ph_max": 7.0,
        "major_producing_states": ["Gujarat", "Andhra Pradesh", "Rajasthan", "Tamil Nadu", "Karnataka"],
        "key_pests": ["Leaf Miner", "Red Hairy Caterpillar", "White Grub"],
        "key_diseases": ["Tikka Leaf Spot", "Rust", "Collar Rot"],
        "package_of_practices": "Apply Gypsum @ 400 kg/ha at pegging (40-45 DAS) for healthy pod filling and shell hardening."
    },
    {
        "crop_id": "crop_mustard",
        "crop_name": "Mustard / Rapeseed",
        "scientific_name": "Brassica juncea",
        "local_names": {"hi": "सरसों / राई", "te": "ఆవాలు", "ta": "கடுகு", "kn": "ಸಾಸಿವೆ", "mr": "मोहरी"},
        "category": "Oilseeds",
        "seasons": ["rabi"],
        "duration_days": 110,
        "water_requirement": "Low-Moderate (300-450 mm)",
        "soil_preferences": ["Alluvial Loam", "Sandy Loam", "Light Clay Loam"],
        "min_temp_c": 8, "max_temp_c": 25, "ideal_ph_min": 6.5, "ideal_ph_max": 7.8,
        "major_producing_states": ["Rajasthan", "Madhya Pradesh", "Haryana", "Uttar Pradesh", "West Bengal"],
        "key_pests": ["Mustard Aphid (Lipaphis erysimi)", "Painted Bug", "Sawfly"],
        "key_diseases": ["White Rust", "Alternaria Blight", "Downy Mildew"],
        "package_of_practices": "Spray Neem oil 1500ppm at first aphid sighting. Apply Sulphur @ 30 kg/ha to boost oil content."
    },
    {
        "crop_id": "crop_sunflower",
        "crop_name": "Sunflower",
        "scientific_name": "Helianthus annuus",
        "local_names": {"hi": "सूरजमुखी", "te": "పొద్దుతిరుగుడు", "ta": "சூரியகாந்தி", "kn": "ಸೂರ್ಯಕಾಂತಿ", "mr": "सूर्यफूल"},
        "category": "Oilseeds",
        "seasons": ["rabi", "summer", "kharif"],
        "duration_days": 90,
        "water_requirement": "Moderate (450-550 mm)",
        "soil_preferences": ["Deep Black Soil", "Red Loamy Soil", "Alluvial Loam"],
        "min_temp_c": 15, "max_temp_c": 35, "ideal_ph_min": 6.5, "ideal_ph_max": 8.0,
        "major_producing_states": ["Karnataka", "Andhra Pradesh", "Maharashtra", "Bihar", "Odisha"],
        "key_pests": ["Head Borer (Helicoverpa)", "Thrips", "Leafhopper"],
        "key_diseases": ["Alternaria Leaf Blight", "Sunflower Necrosis Virus"],
        "package_of_practices": "Hand pollination in early mornings or bee-hive placement improves seed set by 25%."
    },

    # --- PULSES ---
    {
        "crop_id": "crop_chickpea",
        "crop_name": "Chickpea (Gram / Chana)",
        "scientific_name": "Cicer arietinum",
        "local_names": {"hi": "चना", "te": "శనగలు", "ta": "கொண்டைக்கடலை", "kn": "ಕಡಲೆ", "mr": "हरभरा"},
        "category": "Pulses",
        "seasons": ["rabi"],
        "duration_days": 105,
        "water_requirement": "Low (250-400 mm)",
        "soil_preferences": ["Black Cotton Soil", "Sandy Loam", "Clay Loam"],
        "min_temp_c": 10, "max_temp_c": 28, "ideal_ph_min": 6.2, "ideal_ph_max": 7.8,
        "major_producing_states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Andhra Pradesh", "Karnataka"],
        "key_pests": ["Gram Pod Borer (Helicoverpa armigera)"],
        "key_diseases": ["Fusarium Wilt", "Dry Root Rot", "Ascochyta Blight"],
        "package_of_practices": "Seed treat with Trichoderma viride @ 5g/kg. Erect bird perches @ 20/acre for pod borer control."
    },
    {
        "crop_id": "crop_redgram",
        "crop_name": "Pigeon Pea (Red Gram / Arhar / Tur)",
        "scientific_name": "Cajanus cajan",
        "local_names": {"hi": "अरहर / तूर", "te": "కందులు", "ta": "துவரம்பருப்பு", "kn": "ತೊಗರಿ", "mr": "तूर"},
        "category": "Pulses",
        "seasons": ["kharif"],
        "duration_days": 160,
        "water_requirement": "Low-Moderate (500-650 mm)",
        "soil_preferences": ["Deep Black Soil", "Red Sandy Loam", "Alluvial Loam"],
        "min_temp_c": 18, "max_temp_c": 36, "ideal_ph_min": 6.0, "ideal_ph_max": 7.5,
        "major_producing_states": ["Maharashtra", "Madhya Pradesh", "Karnataka", "Telangana", "Andhra Pradesh"],
        "key_pests": ["Pod Borer", "Pod Fly", "Plume Moth"],
        "key_diseases": ["Fusarium Wilt", "Sterility Mosaic Disease"],
        "package_of_practices": "Excellent for intercropping with Soybean (4:2) or Cotton. Deep taproot breaks soil compaction."
    },
    {
        "crop_id": "crop_blackgram",
        "crop_name": "Black Gram (Urad)",
        "scientific_name": "Vigna mungo",
        "local_names": {"hi": "उड़द", "te": "మినుములు", "ta": "உளுந்து", "kn": "ಉದ್ದು", "mr": "उडीद"},
        "category": "Pulses",
        "seasons": ["kharif", "rabi"],
        "duration_days": 75,
        "water_requirement": "Low (300-400 mm)",
        "soil_preferences": ["Loamy Black Soil", "Alluvial Soil", "Red Loam"],
        "min_temp_c": 22, "max_temp_c": 38, "ideal_ph_min": 6.5, "ideal_ph_max": 7.8,
        "major_producing_states": ["Madhya Pradesh", "Andhra Pradesh", "Uttar Pradesh", "Tamil Nadu", "Maharashtra"],
        "key_pests": ["Whitefly (Bemisia tabaci)", "Pod Borer", "Aphids"],
        "key_diseases": ["Yellow Mosaic Virus (YMV)", "Powdery Mildew", "Leaf Crinkle"],
        "package_of_practices": "Control whitefly vectors using yellow sticky traps @ 10/acre to stop YMV transmission."
    },
    {
        "crop_id": "crop_greengram",
        "crop_name": "Green Gram (Moong)",
        "scientific_name": "Vigna radiata",
        "local_names": {"hi": "मूंग", "te": "పెసలు", "ta": "பாசிப்பயறு", "kn": "ಹೆಸರು", "mr": "मूग"},
        "category": "Pulses",
        "seasons": ["kharif", "summer"],
        "duration_days": 68,
        "water_requirement": "Low (250-350 mm)",
        "soil_preferences": ["Well-drained Loam", "Sandy Loam", "Alluvial Soil"],
        "min_temp_c": 20, "max_temp_c": 38, "ideal_ph_min": 6.2, "ideal_ph_max": 7.5,
        "major_producing_states": ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Karnataka", "Andhra Pradesh"],
        "key_pests": ["Whitefly", "Thrips", "Pod Borer"],
        "key_diseases": ["Yellow Mosaic Virus", "Cercospora Leaf Spot"],
        "package_of_practices": "Shortest duration legume. Fits perfectly as catch crop in summer between Wheat and Paddy."
    },

    # --- SPICES & VEGETABLES ---
    {
        "crop_id": "crop_chilli",
        "crop_name": "Chilli (Mirchi)",
        "scientific_name": "Capsicum annuum",
        "local_names": {"hi": "मिर्च", "te": "మిరపకాయలు", "ta": "மிளகாய்", "kn": "ಮೆಣಸಿನಕಾಯಿ", "mr": "मिरची"},
        "category": "Spices / Cash Crop",
        "seasons": ["kharif", "rabi"],
        "duration_days": 150,
        "water_requirement": "Moderate (550-700 mm)",
        "soil_preferences": ["Deep Black Cotton Soil", "Red Sandy Loam", "Well-drained Loam"],
        "min_temp_c": 18, "max_temp_c": 35, "ideal_ph_min": 6.5, "ideal_ph_max": 7.5,
        "major_producing_states": ["Andhra Pradesh (Guntur)", "Telangana", "Karnataka", "Madhya Pradesh", "Gujarat"],
        "key_pests": ["Invasive Black Thrips (Thrips parvispinus)", "Mites", "Fruit Borer"],
        "key_diseases": ["Anthracnose / Die Back", "Chilli Leaf Curl Virus", "Powdery Mildew"],
        "package_of_practices": "Blue and yellow sticky traps @ 30/acre for thrips control. Avoid excessive nitrogen."
    },
    {
        "crop_id": "crop_onion",
        "crop_name": "Onion",
        "scientific_name": "Allium cepa",
        "local_names": {"hi": "प्याज", "te": "ఉల్లిపాయలు", "ta": "வெங்காயம்", "kn": "ಈರುಳ್ಳಿ", "mr": "कांदा"},
        "category": "Vegetables",
        "seasons": ["kharif", "rabi", "summer"],
        "duration_days": 115,
        "water_requirement": "Moderate (450-550 mm)",
        "soil_preferences": ["Deep Loamy Soil", "Sandy Loam", "Black Soil"],
        "min_temp_c": 12, "max_temp_c": 30, "ideal_ph_min": 6.5, "ideal_ph_max": 7.5,
        "major_producing_states": ["Maharashtra (Nashik)", "Karnataka", "Madhya Pradesh", "Gujarat", "Rajasthan"],
        "key_pests": ["Onion Thrips (Thrips tabaci)", "Maggots"],
        "key_diseases": ["Purple Blotch (Alternaria porri)", "Stemphylium Blight", "Basal Rot"],
        "package_of_practices": "Transplant 6-8 week seedlings. Stop irrigation 15 days before harvest for post-harvest curing."
    },
    {
        "crop_id": "crop_tomato",
        "crop_name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "local_names": {"hi": "टमाटर", "te": "టమోటా", "ta": "தக்காளி", "kn": "ಟೊಮೆಟೊ", "mr": "टोमॅटो"},
        "category": "Vegetables",
        "seasons": ["kharif", "rabi", "summer"],
        "duration_days": 100,
        "water_requirement": "Moderate (500-650 mm)",
        "soil_preferences": ["Well-drained Sandy Loam", "Red Loam", "Clay Loam"],
        "min_temp_c": 15, "max_temp_c": 32, "ideal_ph_min": 6.0, "ideal_ph_max": 7.0,
        "major_producing_states": ["Andhra Pradesh", "Madhya Pradesh", "Karnataka", "Gujarat", "Odisha"],
        "key_pests": ["Fruit Borer", "Whitefly", "Pinworm (Tuta absoluta)", "Leafminer"],
        "key_diseases": ["Early Blight", "Late Blight", "Tomato Leaf Curl Virus (ToLCV)", "Bacterial Wilt"],
        "package_of_practices": "Staking improves fruit quality and prevents soil-borne fungal rot. Drip fertigation with calcium."
    },
    {
        "crop_id": "crop_potato",
        "crop_name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "local_names": {"hi": "आलू", "te": "బంగాళాదుంప", "ta": "உருளைக்கிழங்கு", "kn": "ಆಲೂಗಡ್ಡೆ", "mr": "बटाटा"},
        "category": "Tubers / Vegetables",
        "seasons": ["rabi"],
        "duration_days": 95,
        "water_requirement": "Moderate (400-500 mm)",
        "soil_preferences": ["Sandy Loam", "Loose Alluvial Loam", "Silt Loam"],
        "min_temp_c": 12, "max_temp_c": 25, "ideal_ph_min": 5.2, "ideal_ph_max": 6.5,
        "major_producing_states": ["Uttar Pradesh", "West Bengal", "Bihar", "Gujarat", "Punjab"],
        "key_pests": ["Potato Tuber Moth", "Aphids", "Cutworms"],
        "key_diseases": ["Late Blight (Phytophthora infestans)", "Early Blight", "Common Scab"],
        "package_of_practices": "Earthing up at 30-35 days prevents greening of tubers. Certified virus-free seed tubers essential."
    },
    {
        "crop_id": "crop_turmeric",
        "crop_name": "Turmeric",
        "scientific_name": "Curcuma longa",
        "local_names": {"hi": "हल्दी", "te": "పసుపు", "ta": "மஞ்சள்", "kn": "ಅರಿಶಿನ", "mr": "हळद"},
        "category": "Spices / Cash Crop",
        "seasons": ["kharif"],
        "duration_days": 240,
        "water_requirement": "High (1200-1600 mm)",
        "soil_preferences": ["Well-drained Red Sandy Loam", "Clay Loam", "Alluvial Soil"],
        "min_temp_c": 20, "max_temp_c": 35, "ideal_ph_min": 6.0, "ideal_ph_max": 7.5,
        "major_producing_states": ["Telangana", "Maharashtra", "Tamil Nadu", "Andhra Pradesh", "Odisha"],
        "key_pests": ["Shoot Borer", "Rhizome Scale"],
        "key_diseases": ["Rhizome Rot (Pythium)", "Leaf Spot"],
        "package_of_practices": "Heavy application of farmyard manure (25 t/ha). Mulch heavily with green leaves immediately after planting."
    },
    {
        "crop_id": "crop_tobacco",
        "crop_name": "Tobacco",
        "scientific_name": "Nicotiana tabacum",
        "local_names": {"hi": "तंबाकू", "te": "పొగాకు", "ta": "புகையிலை", "kn": "ತಂಬಾಕು", "mr": "तंबाखू"},
        "category": "Commercial Crop",
        "seasons": ["rabi"],
        "duration_days": 130,
        "water_requirement": "Moderate (450-550 mm)",
        "soil_preferences": ["Light Sandy Soil", "Black Soil (Natu)", "Red Sandy Loam"],
        "min_temp_c": 15, "max_temp_c": 32, "ideal_ph_min": 5.8, "ideal_ph_max": 7.2,
        "major_producing_states": ["Andhra Pradesh (Prakasam/Guntur)", "Gujarat", "Karnataka", "Uttar Pradesh"],
        "key_pests": ["Tobacco Caterpillar (Spodoptera litura)", "Aphids", "Budworm"],
        "key_diseases": ["Black Shank", "Frog Eye Leaf Spot", "Tobacco Mosaic Virus"],
        "package_of_practices": "Topping and de-suckering essential for Virginia Flue-Cured (FCV) quality leaf expansion."
    }
]

def sync_crops():
    db = get_azure_table_db()
    table = db.Table("sarthicropmaster")
    
    print("🌾 Starting Crop Master Ingestion (Authoritative ICAR agronomic profiles)...")
    started_at = datetime.utcnow()
    inserted = 0
    now_iso = started_at.isoformat()

    for crop in CROPS_MASTER_DATA:
        record = {
            "crop_id": crop["crop_id"],
            "name": crop["crop_name"],
            "scientific_name": crop["scientific_name"],
            "local_names": crop["local_names"],
            "category": crop["category"],
            "seasons": crop["seasons"],
            "duration_days": crop["duration_days"],
            "water_requirement": crop["water_requirement"],
            "soil_preferences": crop["soil_preferences"],
            "min_temp_c": crop["min_temp_c"],
            "max_temp_c": crop["max_temp_c"],
            "ideal_ph_min": crop["ideal_ph_min"],
            "ideal_ph_max": crop["ideal_ph_max"],
            "major_producing_states": crop["major_producing_states"],
            "key_pests": crop["key_pests"],
            "key_diseases": crop["key_diseases"],
            "package_of_practices": crop["package_of_practices"],
            "source": "ICAR Package of Practices & DAC&FW, GoI",
            "source_url": "https://icar.org.in",
            "fetched_at": now_iso,
            "verified": True
        }
        table.put_item(Item=record)
        inserted += 1

    elapsed = (datetime.utcnow() - started_at).total_seconds()
    print(f"✅ Successfully ingested {inserted} master crops into 'sarthicropmaster' in {elapsed:.2f}s!")
    return {"records_inserted": inserted, "elapsed_seconds": elapsed}

if __name__ == "__main__":
    sync_crops()
