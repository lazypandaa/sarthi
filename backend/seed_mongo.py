#!/usr/bin/env python3
"""
Seed MongoDB database for Gram Vaani
Populates:
1. hyperlocal_context (from hyperlocal_data.py and india_complete_data.py)
2. success_stories (from hyperlocal_data.py)
3. indexes
"""
import os
import pymongo
from dotenv import dotenv_values

# Load environment
env = {}
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

mongo_url = env.get("MONGO_URL", os.getenv("MONGO_URL"))

if not mongo_url:
    print("❌ MONGO_URL not found in .env or environment")
    exit(1)

print(f"Connecting to MongoDB...")
client = pymongo.MongoClient(mongo_url, serverSelectionTimeoutMS=8000)

try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n👉 Please check:")
    print("1. MongoDB Atlas -> 'Database Access': Ensure username and password match MONGO_URL.")
    print("2. MongoDB Atlas -> 'Network Access': Ensure your current IP or 0.0.0.0/0 is allowed.")
    exit(1)

# Gram Vaani uses db 'gramvani'
db = client.gramvani

# 1. Seed Hyperlocal Context
print("\n📦 Seeding 'hyperlocal_context' collection...")
from hyperlocal_data import HYPERLOCAL_DATA, SUCCESS_STORIES
from india_complete_data import INDIA_AGRICULTURAL_DATA

hyperlocal_docs = []

# Process HYPERLOCAL_DATA
for state, state_data in HYPERLOCAL_DATA.items():
    districts = state_data.get("districts", {})
    for district, dist_data in districts.items():
        doc = {
            "state": state,
            "district": district,
            "soil_type": dist_data.get("soil_type", "Loamy Soil"),
            "rainfall": dist_data.get("rainfall", "800mm"),
            "crops": dist_data.get("crops", {}),
            "pest_alerts": dist_data.get("pest_alerts", [])
        }
        hyperlocal_docs.append(doc)

# Process INDIA_AGRICULTURAL_DATA
for state, state_data in INDIA_AGRICULTURAL_DATA.items():
    districts = state_data.get("districts", {})
    for district, dist_data in districts.items():
        # Check if already present
        exists = any(d["state"].lower() == state.lower() and d["district"].lower() == district.lower() for d in hyperlocal_docs)
        if not exists:
            doc = {
                "state": state,
                "district": district,
                "soil_type": dist_data.get("soil", "Alluvial Soil"),
                "rainfall": dist_data.get("rainfall", "900mm"),
                "crops": dist_data.get("crops", {}),
                "pest_alerts": []
            }
            hyperlocal_docs.append(doc)

# Clear and insert
db.hyperlocal_context.drop()
if hyperlocal_docs:
    db.hyperlocal_context.insert_many(hyperlocal_docs)
    db.hyperlocal_context.create_index([("district", pymongo.ASCENDING)])
    db.hyperlocal_context.create_index([("state", pymongo.ASCENDING)])
    print(f"  ✓ Inserted {len(hyperlocal_docs)} regional agricultural context records into 'hyperlocal_context'")

# 2. Seed Success Stories
print("\n🌟 Seeding 'success_stories' collection...")
db.success_stories.drop()
if SUCCESS_STORIES:
    db.success_stories.insert_many(SUCCESS_STORIES)
    db.success_stories.create_index([("location", pymongo.ASCENDING)])
    print(f"  ✓ Inserted {len(SUCCESS_STORIES)} stories into 'success_stories'")

# 3. Create indexes for pest_outbreaks and environmental_profiles
print("\n🛡️ Setting up 'pest_outbreaks' & 'environmental_profiles' collections...")
db.pest_outbreaks.create_index([("location", pymongo.ASCENDING)])
db.pest_outbreaks.create_index([("timestamp", pymongo.DESCENDING)])
db.environmental_profiles.create_index([("user_id", pymongo.ASCENDING)])
print("  ✓ Indexes initialized")

print("\n🎉 Seeding complete! The database 'gramvani' is now fully ready for the project.")
