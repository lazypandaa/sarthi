# Hyperlocal Context Data for Indian Agriculture
# Soil types, seasonal calendars, and crop recommendations by region

HYPERLOCAL_DATA = {
    "Karnataka": {
        "districts": {
            "Bangalore": {
                "soil_type": "Red Sandy Loam",
                "rainfall": "900mm",
                "crops": {
                    "kharif": ["Ragi", "Maize", "Groundnut"],
                    "rabi": ["Tomato", "Beans", "Cabbage"],
                    "summer": ["Cucumber", "Ridge Gourd"]
                },
                "pest_alerts": ["Fall Armyworm in Maize", "Aphids in Vegetables"]
            },
            "Mysore": {
                "soil_type": "Red Loamy",
                "rainfall": "800mm",
                "crops": {
                    "kharif": ["Paddy", "Ragi", "Sugarcane"],
                    "rabi": ["Wheat", "Sunflower"],
                    "summer": ["Vegetables"]
                }
            }
        }
    },
    "Maharashtra": {
        "districts": {
            "Pune": {
                "soil_type": "Black Cotton Soil",
                "rainfall": "700mm",
                "crops": {
                    "kharif": ["Soybean", "Cotton", "Jowar"],
                    "rabi": ["Wheat", "Gram"],
                    "summer": ["Vegetables"]
                },
                "pest_alerts": ["Pink Bollworm in Cotton"]
            },
            "Nashik": {
                "soil_type": "Black Soil",
                "rainfall": "600mm",
                "crops": {
                    "kharif": ["Onion", "Grapes", "Pomegranate"],
                    "rabi": ["Wheat", "Onion"],
                    "summer": ["Onion"]
                }
            }
        }
    },
    "Punjab": {
        "districts": {
            "Ludhiana": {
                "soil_type": "Alluvial Soil",
                "rainfall": "700mm",
                "crops": {
                    "kharif": ["Paddy", "Cotton", "Maize"],
                    "rabi": ["Wheat", "Mustard"],
                    "summer": ["Vegetables"]
                }
            }
        }
    },
    "Tamil Nadu": {
        "districts": {
            "Coimbatore": {
                "soil_type": "Red Loamy",
                "rainfall": "700mm",
                "crops": {
                    "kharif": ["Cotton", "Maize", "Groundnut"],
                    "rabi": ["Paddy", "Pulses"],
                    "summer": ["Vegetables"]
                }
            }
        }
    },
    "Uttar Pradesh": {
        "districts": {
            "Lucknow": {
                "soil_type": "Alluvial Soil",
                "rainfall": "1000mm",
                "crops": {
                    "kharif": ["Paddy", "Sugarcane", "Maize"],
                    "rabi": ["Wheat", "Potato", "Mustard"],
                    "summer": ["Vegetables"]
                }
            }
        }
    }
}

SUCCESS_STORIES = [
    {
        "farmer": "Ramesh Kumar",
        "location": "Bangalore, Karnataka",
        "crop": "Tomato",
        "achievement": "Increased yield by 40% using drip irrigation",
        "method": "Drip irrigation + organic fertilizers"
    },
    {
        "farmer": "Suresh Patil",
        "location": "Pune, Maharashtra",
        "crop": "Soybean",
        "achievement": "Reduced pest damage by 60% using IPM",
        "method": "Integrated Pest Management"
    }
]
