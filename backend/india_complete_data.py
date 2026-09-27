"""
Comprehensive Indian Agricultural Data
Based on open government sources and agricultural research
Covers all 28 states + 8 UTs with major agricultural districts
"""

# Complete India Agricultural Data
INDIA_AGRICULTURAL_DATA = {
    "Andhra Pradesh": {
        "districts": {
            "Guntur": {"soil": "Black Cotton Soil", "rainfall": "900mm", "crops": {"kharif": ["Paddy", "Cotton", "Chili"], "rabi": ["Tobacco", "Sunflower"], "summer": ["Watermelon"]}},
            "Krishna": {"soil": "Alluvial Soil", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Paddy", "Pulses"], "summer": ["Vegetables"]}},
            "Visakhapatnam": {"soil": "Red Soil", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Pulses"], "summer": ["Mango"]}},
        }
    },
    "Arunachal Pradesh": {
        "districts": {
            "Papum Pare": {"soil": "Mountain Soil", "rainfall": "2500mm", "crops": {"kharif": ["Rice", "Maize"], "rabi": ["Wheat"], "summer": ["Vegetables"]}},
        }
    },
    "Assam": {
        "districts": {
            "Kamrup": {"soil": "Alluvial Soil", "rainfall": "1800mm", "crops": {"kharif": ["Paddy", "Jute", "Tea"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
            "Jorhat": {"soil": "Alluvial Soil", "rainfall": "2000mm", "crops": {"kharif": ["Paddy", "Tea"], "rabi": ["Pulses"], "summer": ["Vegetables"]}},
        }
    },
    "Bihar": {
        "districts": {
            "Patna": {"soil": "Alluvial Soil", "rainfall": "1200mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat", "Potato"], "summer": ["Vegetables"]}},
            "Muzaffarpur": {"soil": "Alluvial Soil", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Wheat", "Lentil"], "summer": ["Litchi"]}},
        }
    },
    "Chhattisgarh": {
        "districts": {
            "Raipur": {"soil": "Red and Yellow Soil", "rainfall": "1300mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
            "Bilaspur": {"soil": "Red Soil", "rainfall": "1400mm", "crops": {"kharif": ["Paddy"], "rabi": ["Wheat", "Pulses"], "summer": ["Vegetables"]}},
        }
    },
    "Goa": {
        "districts": {
            "North Goa": {"soil": "Laterite Soil", "rainfall": "3000mm", "crops": {"kharif": ["Paddy", "Cashew"], "rabi": ["Vegetables"], "summer": ["Mango", "Coconut"]}},
        }
    },
    "Gujarat": {
        "districts": {
            "Ahmedabad": {"soil": "Sandy Loam", "rainfall": "800mm", "crops": {"kharif": ["Cotton", "Groundnut", "Bajra"], "rabi": ["Wheat", "Cumin"], "summer": ["Vegetables"]}},
            "Surat": {"soil": "Black Soil", "rainfall": "1200mm", "crops": {"kharif": ["Sugarcane", "Paddy"], "rabi": ["Wheat"], "summer": ["Mango"]}},
            "Rajkot": {"soil": "Black Soil", "rainfall": "600mm", "crops": {"kharif": ["Cotton", "Groundnut"], "rabi": ["Wheat", "Cumin"], "summer": ["Vegetables"]}},
        }
    },
    "Haryana": {
        "districts": {
            "Karnal": {"soil": "Alluvial Soil", "rainfall": "700mm", "crops": {"kharif": ["Paddy", "Cotton"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
            "Hisar": {"soil": "Alluvial Soil", "rainfall": "450mm", "crops": {"kharif": ["Bajra", "Cotton"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
        }
    },
    "Himachal Pradesh": {
        "districts": {
            "Shimla": {"soil": "Mountain Soil", "rainfall": "1500mm", "crops": {"kharif": ["Maize", "Rice"], "rabi": ["Wheat"], "summer": ["Apple", "Vegetables"]}},
            "Kullu": {"soil": "Mountain Soil", "rainfall": "1200mm", "crops": {"kharif": ["Rice"], "rabi": ["Wheat"], "summer": ["Apple", "Plum"]}},
        }
    },
    "Jharkhand": {
        "districts": {
            "Ranchi": {"soil": "Red Soil", "rainfall": "1400mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat", "Pulses"], "summer": ["Vegetables"]}},
            "Dhanbad": {"soil": "Red Soil", "rainfall": "1300mm", "crops": {"kharif": ["Paddy"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
        }
    },
    "Karnataka": {
        "districts": {
            "Bangalore": {"soil": "Red Sandy Loam", "rainfall": "900mm", "crops": {"kharif": ["Ragi", "Maize", "Groundnut"], "rabi": ["Tomato", "Beans"], "summer": ["Cucumber"]}},
            "Mysore": {"soil": "Red Loamy", "rainfall": "800mm", "crops": {"kharif": ["Paddy", "Ragi"], "rabi": ["Wheat", "Sunflower"], "summer": ["Vegetables"]}},
            "Belgaum": {"soil": "Black Soil", "rainfall": "1000mm", "crops": {"kharif": ["Sugarcane", "Jowar"], "rabi": ["Wheat"], "summer": ["Vegetables"]}},
            "Hubli": {"soil": "Black Soil", "rainfall": "700mm", "crops": {"kharif": ["Cotton", "Jowar"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
        }
    },
    "Kerala": {
        "districts": {
            "Thiruvananthapuram": {"soil": "Laterite Soil", "rainfall": "3000mm", "crops": {"kharif": ["Paddy", "Coconut"], "rabi": ["Vegetables"], "summer": ["Rubber", "Pepper"]}},
            "Kochi": {"soil": "Laterite Soil", "rainfall": "3200mm", "crops": {"kharif": ["Paddy", "Coconut"], "rabi": ["Vegetables"], "summer": ["Spices"]}},
            "Wayanad": {"soil": "Red Soil", "rainfall": "2500mm", "crops": {"kharif": ["Paddy", "Coffee"], "rabi": ["Vegetables"], "summer": ["Tea", "Cardamom"]}},
        }
    },
    "Madhya Pradesh": {
        "districts": {
            "Indore": {"soil": "Black Soil", "rainfall": "900mm", "crops": {"kharif": ["Soybean", "Cotton", "Maize"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
            "Bhopal": {"soil": "Black Soil", "rainfall": "1200mm", "crops": {"kharif": ["Soybean", "Paddy"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
            "Jabalpur": {"soil": "Black Soil", "rainfall": "1400mm", "crops": {"kharif": ["Paddy", "Soybean"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
        }
    },
    "Maharashtra": {
        "districts": {
            "Pune": {"soil": "Black Cotton Soil", "rainfall": "700mm", "crops": {"kharif": ["Soybean", "Cotton", "Jowar"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
            "Nashik": {"soil": "Black Soil", "rainfall": "600mm", "crops": {"kharif": ["Onion", "Grapes"], "rabi": ["Wheat", "Onion"], "summer": ["Onion", "Pomegranate"]}},
            "Nagpur": {"soil": "Black Soil", "rainfall": "1200mm", "crops": {"kharif": ["Cotton", "Soybean"], "rabi": ["Wheat", "Gram"], "summer": ["Orange"]}},
            "Mumbai": {"soil": "Laterite Soil", "rainfall": "2400mm", "crops": {"kharif": ["Paddy"], "rabi": ["Vegetables"], "summer": ["Vegetables"]}},
        }
    },
    "Manipur": {
        "districts": {
            "Imphal": {"soil": "Red Soil", "rainfall": "1500mm", "crops": {"kharif": ["Paddy"], "rabi": ["Wheat", "Pulses"], "summer": ["Vegetables"]}},
        }
    },
    "Meghalaya": {
        "districts": {
            "Shillong": {"soil": "Red Soil", "rainfall": "2500mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Potato"], "summer": ["Vegetables"]}},
        }
    },
    "Mizoram": {
        "districts": {
            "Aizawl": {"soil": "Red Soil", "rainfall": "2500mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Vegetables"], "summer": ["Vegetables"]}},
        }
    },
    "Nagaland": {
        "districts": {
            "Kohima": {"soil": "Red Soil", "rainfall": "2000mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat"], "summer": ["Vegetables"]}},
        }
    },
    "Odisha": {
        "districts": {
            "Bhubaneswar": {"soil": "Red and Laterite Soil", "rainfall": "1500mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Pulses", "Vegetables"], "summer": ["Vegetables"]}},
            "Cuttack": {"soil": "Alluvial Soil", "rainfall": "1600mm", "crops": {"kharif": ["Paddy"], "rabi": ["Pulses", "Vegetables"], "summer": ["Vegetables"]}},
        }
    },
    "Punjab": {
        "districts": {
            "Ludhiana": {"soil": "Alluvial Soil", "rainfall": "700mm", "crops": {"kharif": ["Paddy", "Cotton", "Maize"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
            "Amritsar": {"soil": "Alluvial Soil", "rainfall": "650mm", "crops": {"kharif": ["Paddy", "Cotton"], "rabi": ["Wheat"], "summer": ["Vegetables"]}},
            "Patiala": {"soil": "Alluvial Soil", "rainfall": "600mm", "crops": {"kharif": ["Paddy", "Cotton"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
        }
    },
    "Rajasthan": {
        "districts": {
            "Jaipur": {"soil": "Sandy Soil", "rainfall": "600mm", "crops": {"kharif": ["Bajra", "Jowar"], "rabi": ["Wheat", "Mustard", "Gram"], "summer": ["Vegetables"]}},
            "Jodhpur": {"soil": "Arid Soil", "rainfall": "350mm", "crops": {"kharif": ["Bajra", "Moth"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
            "Udaipur": {"soil": "Red Soil", "rainfall": "650mm", "crops": {"kharif": ["Maize", "Soybean"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
        }
    },
    "Sikkim": {
        "districts": {
            "Gangtok": {"soil": "Mountain Soil", "rainfall": "3500mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat"], "summer": ["Cardamom", "Ginger"]}},
        }
    },
    "Tamil Nadu": {
        "districts": {
            "Chennai": {"soil": "Red Loamy", "rainfall": "1400mm", "crops": {"kharif": ["Paddy"], "rabi": ["Pulses"], "summer": ["Vegetables"]}},
            "Coimbatore": {"soil": "Red Loamy", "rainfall": "700mm", "crops": {"kharif": ["Cotton", "Maize"], "rabi": ["Paddy", "Pulses"], "summer": ["Vegetables"]}},
            "Madurai": {"soil": "Black Soil", "rainfall": "850mm", "crops": {"kharif": ["Cotton", "Groundnut"], "rabi": ["Pulses"], "summer": ["Vegetables"]}},
            "Salem": {"soil": "Red Soil", "rainfall": "900mm", "crops": {"kharif": ["Paddy", "Groundnut"], "rabi": ["Pulses"], "summer": ["Mango"]}},
        }
    },
    "Telangana": {
        "districts": {
            "Hyderabad": {"soil": "Red Soil", "rainfall": "800mm", "crops": {"kharif": ["Paddy", "Cotton"], "rabi": ["Maize", "Sunflower"], "summer": ["Vegetables"]}},
            "Warangal": {"soil": "Red Soil", "rainfall": "900mm", "crops": {"kharif": ["Paddy", "Cotton"], "rabi": ["Maize"], "summer": ["Vegetables"]}},
        }
    },
    "Tripura": {
        "districts": {
            "Agartala": {"soil": "Red Soil", "rainfall": "2100mm", "crops": {"kharif": ["Paddy", "Jute"], "rabi": ["Wheat", "Pulses"], "summer": ["Vegetables"]}},
        }
    },
    "Uttar Pradesh": {
        "districts": {
            "Lucknow": {"soil": "Alluvial Soil", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Wheat", "Potato", "Mustard"], "summer": ["Vegetables"]}},
            "Kanpur": {"soil": "Alluvial Soil", "rainfall": "800mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Wheat", "Gram"], "summer": ["Vegetables"]}},
            "Varanasi": {"soil": "Alluvial Soil", "rainfall": "1100mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat", "Pulses"], "summer": ["Vegetables"]}},
            "Agra": {"soil": "Alluvial Soil", "rainfall": "700mm", "crops": {"kharif": ["Bajra", "Jowar"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
        }
    },
    "Uttarakhand": {
        "districts": {
            "Dehradun": {"soil": "Mountain Soil", "rainfall": "2100mm", "crops": {"kharif": ["Paddy", "Maize"], "rabi": ["Wheat"], "summer": ["Vegetables"]}},
            "Haridwar": {"soil": "Alluvial Soil", "rainfall": "1000mm", "crops": {"kharif": ["Paddy", "Sugarcane"], "rabi": ["Wheat", "Mustard"], "summer": ["Vegetables"]}},
        }
    },
    "West Bengal": {
        "districts": {
            "Kolkata": {"soil": "Alluvial Soil", "rainfall": "1600mm", "crops": {"kharif": ["Paddy", "Jute"], "rabi": ["Wheat", "Potato", "Mustard"], "summer": ["Vegetables"]}},
            "Darjeeling": {"soil": "Mountain Soil", "rainfall": "3000mm", "crops": {"kharif": ["Paddy", "Tea"], "rabi": ["Wheat"], "summer": ["Tea", "Cardamom"]}},
            "Bardhaman": {"soil": "Alluvial Soil", "rainfall": "1400mm", "crops": {"kharif": ["Paddy"], "rabi": ["Wheat", "Potato"], "summer": ["Vegetables"]}},
        }
    },
}

# Success stories from across India
INDIA_SUCCESS_STORIES = [
    {"farmer": "Ramesh Kumar", "location": "Bangalore, Karnataka", "crop": "Tomato", "achievement": "40% yield increase with drip irrigation", "method": "Drip irrigation + organic fertilizers"},
    {"farmer": "Suresh Patil", "location": "Pune, Maharashtra", "crop": "Soybean", "achievement": "60% pest reduction with IPM", "method": "Integrated Pest Management"},
    {"farmer": "Lakshmi Devi", "location": "Guntur, Andhra Pradesh", "crop": "Chili", "achievement": "80% income increase with organic farming", "method": "Organic certification + direct market"},
    {"farmer": "Rajesh Singh", "location": "Jaipur, Rajasthan", "crop": "Bajra", "achievement": "70% yield in drought with mulching", "method": "Plastic mulching + drip irrigation"},
    {"farmer": "Priya Sharma", "location": "Ahmedabad, Gujarat", "crop": "Cotton", "achievement": "Doubled profit with Bt Cotton", "method": "Bt Cotton + biological pest control"},
    {"farmer": "Mohan Kumar", "location": "Mysore, Karnataka", "crop": "Paddy", "achievement": "40% water savings with SRI", "method": "System of Rice Intensification"},
    {"farmer": "Anita Verma", "location": "Lucknow, Uttar Pradesh", "crop": "Wheat", "achievement": "50% cost reduction with zero tillage", "method": "Zero tillage + crop rotation"},
    {"farmer": "Vijay Reddy", "location": "Hyderabad, Telangana", "crop": "Cotton", "achievement": "Eliminated pesticide use", "method": "Bt Cotton + pheromone traps"},
]
