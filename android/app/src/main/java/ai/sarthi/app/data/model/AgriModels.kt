package ai.sarthi.app.data.model

import com.google.gson.annotations.SerializedName

data class HealthResponse(
    @SerializedName("status")
    val status: String = "ok",
    @SerializedName("database")
    val database: String? = null
)

data class WeatherData(
    @SerializedName("temperature")
    val temperature: Double = 28.0,
    @SerializedName("humidity")
    val humidity: Double = 68.0,
    @SerializedName("rainfall")
    val rainfall: Double = 0.0,
    @SerializedName("condition")
    val condition: String = "Partly Cloudy",
    @SerializedName("alert")
    val alert: String? = null,
    @SerializedName("source")
    val source: String? = "IMD Agromet Advisory Service"
)

data class EnvironmentalProfile(
    @SerializedName("location")
    val location: String = "Warangal, Telangana",
    @SerializedName("district")
    val district: String = "Warangal",
    @SerializedName("state")
    val state: String = "Telangana",
    @SerializedName("soil_type")
    val soilType: String = "Black Cotton Soil",
    @SerializedName("temperature")
    val temperature: Double = 28.0,
    @SerializedName("humidity")
    val humidity: Double = 68.0,
    @SerializedName("rainfall")
    val rainfall: String = "900-1400mm",
    @SerializedName("nitrogen")
    val nitrogen: Int = 225,
    @SerializedName("phosphorus")
    val phosphorus: Int = 19,
    @SerializedName("potassium")
    val potassium: Int = 310,
    @SerializedName("soil_ph")
    val soilPh: Double = 7.6,
    @SerializedName("organic_carbon")
    val organicCarbon: Double = 0.52,
    @SerializedName("recommended_amendments")
    val recommendedAmendments: String = "Apply gypsum @ 250 kg/ha to maintain soil structure; supplement organic compost."
)

data class CropRecommendationItem(
    @SerializedName("crop_id")
    val cropId: String,
    @SerializedName("crop_name")
    val cropName: String,
    @SerializedName("scientific_name")
    val scientificName: String? = null,
    @SerializedName("category")
    val category: String = "Pulse",
    @SerializedName("soil_compatibility")
    val soilCompatibility: Double = 95.0,
    @SerializedName("climate_match")
    val climateMatch: String = "Optimal",
    @SerializedName("water_requirement")
    val waterRequirement: String = "Low (1-2 irrigations)",
    @SerializedName("duration_days")
    val durationDays: Int = 85,
    @SerializedName("explanation")
    val explanation: String = "Tailored for your soil nutrient status and seasonal climate.",
    @SerializedName("key_pests")
    val keyPests: List<String> = emptyList(),
    @SerializedName("key_diseases")
    val keyDiseases: List<String> = emptyList(),
    @SerializedName("source")
    val source: String = "ICAR Package of Practices"
)

data class AgriNewsItem(
    @SerializedName("id")
    val id: String,
    @SerializedName("title")
    val title: String,
    @SerializedName("summary")
    val summary: String,
    @SerializedName("crop")
    val crop: String? = null,
    @SerializedName("category")
    val category: String = "hyperlocal_advisory",
    @SerializedName("source")
    val source: String = "IMD Agromet Advisory Service",
    @SerializedName("image")
    val image: String? = null
)

data class MarketItem(
    @SerializedName("record_id")
    val recordId: String,
    @SerializedName("market")
    val market: String,
    @SerializedName("district")
    val district: String = "",
    @SerializedName("state")
    val state: String = "",
    @SerializedName("commodity")
    val commodity: String,
    @SerializedName("variety")
    val variety: String? = "Standard",
    @SerializedName("modal_price")
    val modalPrice: Double = 0.0,
    @SerializedName("min_price")
    val minPrice: Double = 0.0,
    @SerializedName("max_price")
    val maxPrice: Double = 0.0,
    @SerializedName("date")
    val date: String = ""
)

data class OutbreakRecentReport(
    @SerializedName("type")
    val type: String = "pest",
    @SerializedName("crop")
    val crop: String? = null,
    @SerializedName("description")
    val description: String = "",
    @SerializedName("severity")
    val severity: String = "medium"
)

data class OutbreakVillage(
    @SerializedName("village")
    val village: String,
    @SerializedName("state")
    val state: String = "Telangana",
    @SerializedName("coordinates")
    val coordinates: Map<String, Double> = mapOf("lat" to 17.98, "lng" to 79.58),
    @SerializedName("pest_count")
    val pestCount: Int = 0,
    @SerializedName("disease_count")
    val diseaseCount: Int = 0,
    @SerializedName("total_reports")
    val totalReports: Int = 0,
    @SerializedName("alert_level")
    val alertLevel: String = "medium",
    @SerializedName("crops_affected")
    val cropsAffected: List<String> = emptyList(),
    @SerializedName("recent_reports")
    val recentReports: List<OutbreakRecentReport> = emptyList()
)

data class OutbreakMapResponse(
    @SerializedName("outbreaks")
    val outbreaks: List<OutbreakVillage> = emptyList(),
    @SerializedName("total_reports")
    val totalReports: Int = 0,
    @SerializedName("affected_villages")
    val affectedVillages: Int = 0
)

data class LeaderboardItem(
    @SerializedName("rank")
    val rank: Int,
    @SerializedName("village_id")
    val villageId: String,
    @SerializedName("trust_score")
    val trustScore: Double = 90.0,
    @SerializedName("total_responses")
    val totalResponses: Int = 0,
    @SerializedName("tier_icon")
    val tierIcon: String = "🥇"
)

data class RecommendationResponse(
    @SerializedName("recommendation_id")
    val recommendationId: String = "",
    @SerializedName("recommendation")
    val recommendation: String = "",
    @SerializedName("relevant_memories")
    val relevantMemories: List<HindsightMemoryItem> = emptyList()
)

data class CropCalendarStage(
    val stage: String,
    val timing: String,
    val advisory: String
)

data class CropCalendarItem(
    val name: String,
    val season: String,
    val sowingWindow: String,
    val harvestingWindow: String,
    val durationDays: Int,
    val criticalOperations: List<CropCalendarStage>
)
