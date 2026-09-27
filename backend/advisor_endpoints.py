# Add these endpoints to your main.py backend file

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict
import os

router = APIRouter()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.gramvani

# Environmental Profile Endpoint
@router.get("/api/environmental-profile")
async def get_environmental_profile(current_user: dict = Depends(get_current_user)):
    """Get environmental profile for current user location"""
    try:
        profile = await db.environmental_profiles.find_one(
            {"user_id": current_user["_id"]}
        )
        
        if not profile:
            # Create default profile if not exists
            profile = {
                "user_id": current_user["_id"],
                "location": current_user.get("location", "Unknown"),
                "temperature": 12,
                "humidity": 37,
                "rainfall": 100,
                "nitrogen": 50,
                "phosphorus": 50,
                "potassium": 50,
                "soil_ph": 8.5,
                "soil_temperature": 12,
                "soil_humidity": 37,
                "rainfall_annual": 100
            }
            await db.environmental_profiles.insert_one(profile)
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Crop Recommendations Endpoint
@router.get("/api/crop-recommendations")
async def get_crop_recommendations(current_user: dict = Depends(get_current_user)):
    """Get AI-powered crop recommendations"""
    try:
        # Get user's environmental profile
        env_profile = await db.environmental_profiles.find_one(
            {"user_id": current_user["_id"]}
        )
        
        if not env_profile:
            env_profile = {
                "nitrogen": 50,
                "phosphorus": 50,
                "potassium": 50,
                "temperature": 12,
                "humidity": 37,
                "soil_ph": 8.5,
                "rainfall": 100
            }
        
        # Get all crops and calculate compatibility
        crops = await db.crop_recommendations.find().to_list(length=100)
        
        # Calculate compatibility score for each crop
        for crop in crops:
            score = calculate_crop_compatibility(env_profile, crop)
            crop["soil_compatibility"] = score
        
        # Sort by compatibility
        crops.sort(key=lambda x: x["soil_compatibility"], reverse=True)
        
        return crops[:10]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Optimization Strategies Endpoint
@router.get("/api/optimization-strategies")
async def get_optimization_strategies(current_user: dict = Depends(get_current_user)):
    """Get farming optimization strategies"""
    try:
        strategies = await db.optimization_strategies.find().to_list(length=100)
        return strategies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Farm Intelligence Analytics Endpoint
@router.get("/api/farm-intelligence")
async def get_farm_intelligence(current_user: dict = Depends(get_current_user)):
    """Get farm intelligence analytics"""
    try:
        analytics = await db.farm_intelligence_analytics.find_one(
            {"user_id": current_user["_id"]}
        )
        
        if not analytics:
            # Create default analytics
            analytics = {
                "user_id": current_user["_id"],
                "location": current_user.get("location", "Unknown"),
                "load_predictions": 3,
                "top_crop": "mango",
                "soil_stability": 86,
                "climate_risk": "Low",
                "feature_importance": {
                    "nitrogen": 20,
                    "phosphorus": 15,
                    "potassium": 15,
                    "temperature": 18,
                    "humidity": 12,
                    "ph": 10,
                    "rainfall": 10
                }
            }
            await db.farm_intelligence_analytics.insert_one(analytics)
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Crop Recommendation with Custom Parameters
@router.post("/api/get-crop-recommendation")
async def get_crop_recommendation(
    params: Dict,
    current_user: dict = Depends(get_current_user)
):
    """Get crop recommendation based on custom soil parameters"""
    try:
        # Update user's environmental profile
        await db.environmental_profiles.update_one(
            {"user_id": current_user["_id"]},
            {"$set": params},
            upsert=True
        )
        
        # Get all crops
        crops = await db.crop_recommendations.find().to_list(length=100)
        
        # Calculate compatibility for each crop
        recommendations = []
        for crop in crops:
            score = calculate_crop_compatibility(params, crop)
            crop["soil_compatibility"] = score
            recommendations.append(crop)
        
        # Sort by compatibility
        recommendations.sort(key=lambda x: x["soil_compatibility"], reverse=True)
        
        return {"recommendations": recommendations[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper function to calculate crop compatibility
def calculate_crop_compatibility(env_profile: dict, crop: dict) -> int:
    """Calculate compatibility score between environment and crop"""
    try:
        optimal = crop.get("optimal_conditions", {})
        score = 0
        total_checks = 0
        
        # Check temperature
        if "temperature_min" in optimal and "temperature_max" in optimal:
            temp = env_profile.get("temperature", 0)
            if optimal["temperature_min"] <= temp <= optimal["temperature_max"]:
                score += 15
            total_checks += 15
        
        # Check humidity
        if "humidity_min" in optimal and "humidity_max" in optimal:
            humidity = env_profile.get("humidity", 0)
            if optimal["humidity_min"] <= humidity <= optimal["humidity_max"]:
                score += 15
            total_checks += 15
        
        # Check rainfall
        if "rainfall_min" in optimal and "rainfall_max" in optimal:
            rainfall = env_profile.get("rainfall", 0)
            if optimal["rainfall_min"] <= rainfall <= optimal["rainfall_max"]:
                score += 15
            total_checks += 15
        
        # Check nitrogen
        if "nitrogen_min" in optimal and "nitrogen_max" in optimal:
            nitrogen = env_profile.get("nitrogen", 0)
            if optimal["nitrogen_min"] <= nitrogen <= optimal["nitrogen_max"]:
                score += 15
            total_checks += 15
        
        # Check phosphorus
        if "phosphorus_min" in optimal and "phosphorus_max" in optimal:
            phosphorus = env_profile.get("phosphorus", 0)
            if optimal["phosphorus_min"] <= phosphorus <= optimal["phosphorus_max"]:
                score += 15
            total_checks += 15
        
        # Check potassium
        if "potassium_min" in optimal and "potassium_max" in optimal:
            potassium = env_profile.get("potassium", 0)
            if optimal["potassium_min"] <= potassium <= optimal["potassium_max"]:
                score += 15
            total_checks += 15
        
        # Check pH
        if "ph_min" in optimal and "ph_max" in optimal:
            ph = env_profile.get("soil_ph", 0)
            if optimal["ph_min"] <= ph <= optimal["ph_max"]:
                score += 10
            total_checks += 10
        
        # Calculate percentage
        if total_checks > 0:
            return int((score / total_checks) * 100)
        return 0
        
    except Exception as e:
        print(f"Error calculating compatibility: {e}")
        return 0


# Add router to main app
# app.include_router(router)
