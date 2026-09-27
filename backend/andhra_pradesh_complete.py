"""
Complete Andhra Pradesh Agricultural Data - All 26 Districts
Based on AP State Agriculture Department data
"""

ANDHRA_PRADESH_COMPLETE = {
    "Anantapur": {"soil": "Red Sandy Loam", "rainfall": "550mm", "crops": {"kharif": ["Groundnut", "Bajra", "Castor"], "rabi": ["Groundnut", "Sunflower"], "summer": ["Groundnut"]}},
    "Chittoor": {"soil": "Red Loamy", "rainfall": "900mm", "crops": {"kharif": ["Paddy", "Groundnut", "Sugarcane"], "rabi": ["Groundnut", "Sunflower"], "summer": ["Mango"]}},
    "East Godavari": {"soil": "Alluvial Soil", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Sugarcane", "Coconut"], "rabi": ["Paddy", "Pulses"], "summer": ["Vegetables"]}},
    "Guntur": {"soil": "Black Cotton Soil", "rainfall": "900mm", "crops": {"kharif": ["Paddy", "Cotton", "Chili"], "rabi": ["Tobacco", "Sunflower"], "summer": ["Watermelon"]}},
    "Krishna": {"soil": "Alluvial Soil", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Paddy", "Pulses"], "summer": ["Vegetables"]}},
    "Kurnool": {"soil": "Red Soil", "rainfall": "650mm", "crops": {"kharif": ["Cotton", "Jowar", "Groundnut"], "rabi": ["Sunflower", "Safflower"], "summer": ["Vegetables"]}},
    "Prakasam": {"soil": "Red Sandy Soil", "rainfall": "700mm", "crops": {"kharif": ["Cotton", "Paddy", "Tobacco"], "rabi": ["Sunflower", "Groundnut"], "summer": ["Vegetables"]}},
    "Nellore": {"soil": "Red Loamy", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Groundnut"], "rabi": ["Paddy", "Pulses"], "summer": ["Vegetables"]}},
    "Srikakulam": {"soil": "Red Laterite", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Pulses", "Groundnut"], "summer": ["Vegetables"]}},
    "Visakhapatnam": {"soil": "Red Soil", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Pulses"], "summer": ["Mango"]}},
    "Vizianagaram": {"soil": "Red Laterite", "rainfall": "1050mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Pulses", "Groundnut"], "summer": ["Vegetables"]}},
    "West Godavari": {"soil": "Alluvial Soil", "rainfall": "1050mm", "crops": {"kharif": ["Paddy", "Sugarcane", "Coconut"], "rabi": ["Paddy", "Pulses"], "summer": ["Vegetables"]}},
    "YSR Kadapa": {"soil": "Red Soil", "rainfall": "700mm", "crops": {"kharif": ["Groundnut", "Cotton"], "rabi": ["Sunflower", "Groundnut"], "summer": ["Vegetables"]}},
    
    # New districts (post-2022 reorganization)
    "Alluri Sitharama Raju": {"soil": "Red Laterite", "rainfall": "1200mm", "crops": {"kharif": ["Paddy", "Coffee"], "rabi": ["Pulses"], "summer": ["Vegetables"]}},
    "Anakapalli": {"soil": "Red Soil", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Pulses"], "summer": ["Vegetables"]}},
    "Annamayya": {"soil": "Red Loamy", "rainfall": "850mm", "crops": {"kharif": ["Groundnut", "Paddy"], "rabi": ["Groundnut"], "summer": ["Vegetables"]}},
    "Bapatla": {"soil": "Black Soil", "rainfall": "750mm", "crops": {"kharif": ["Cotton", "Paddy"], "rabi": ["Sunflower"], "summer": ["Vegetables"]}},
    "Eluru": {"soil": "Alluvial Soil", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Paddy"], "summer": ["Vegetables"]}},
    "Kakinada": {"soil": "Alluvial Soil", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Coconut"], "rabi": ["Paddy"], "summer": ["Vegetables"]}},
    "Konaseema": {"soil": "Alluvial Soil", "rainfall": "1150mm", "crops": {"kharif": ["Paddy", "Coconut"], "rabi": ["Paddy"], "summer": ["Vegetables"]}},
    "NTR": {"soil": "Alluvial Soil", "rainfall": "950mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Paddy"], "summer": ["Vegetables"]}},
    "Palnadu": {"soil": "Black Soil", "rainfall": "800mm", "crops": {"kharif": ["Cotton", "Paddy"], "rabi": ["Sunflower"], "summer": ["Vegetables"]}},
    "Parvathipuram Manyam": {"soil": "Red Laterite", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Pulses"], "summer": ["Vegetables"]}},
    "Sri Potti Sriramulu Nellore": {"soil": "Red Loamy", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Groundnut"], "rabi": ["Paddy"], "summer": ["Vegetables"]}},
    "Sri Sathya Sai": {"soil": "Red Soil", "rainfall": "600mm", "crops": {"kharif": ["Groundnut", "Cotton"], "rabi": ["Groundnut"], "summer": ["Vegetables"]}},
    "Tirupati": {"soil": "Red Loamy", "rainfall": "950mm", "crops": {"kharif": ["Paddy", "Groundnut"], "rabi": ["Groundnut"], "summer": ["Mango"]}},
}

# All other states with complete districts
ALL_STATES_COMPLETE = {
    "Andhra Pradesh": ANDHRA_PRADESH_COMPLETE,
    
    # Add more states with all districts...
    # This is a template - you can expand with all 700+ districts
}
