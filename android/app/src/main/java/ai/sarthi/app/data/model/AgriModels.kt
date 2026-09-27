package ai.sarthi.app.data.model

import com.google.gson.annotations.SerializedName

data class HealthResponse(
    @SerializedName("status")
    val status: String,
    @SerializedName("database")
    val database: String? = null
)

data class WeatherInfo(
    @SerializedName("temperature")
    val temperature: Double? = null,
    @SerializedName("humidity")
    val humidity: Double? = null,
    @SerializedName("condition")
    val condition: String? = null,
    @SerializedName("rainfall")
    val rainfall: Double? = null,
    @SerializedName("advisory")
    val advisory: String? = null
)

data class EnvironmentalProfile(
    @SerializedName("soil_type")
    val soilType: String? = null,
    @SerializedName("ph")
    val ph: Double? = null,
    @SerializedName("nitrogen")
    val nitrogen: String? = null,
    @SerializedName("phosphorus")
    val phosphorus: String? = null,
    @SerializedName("potassium")
    val potassium: String? = null,
    @SerializedName("organic_carbon")
    val organicCarbon: String? = null,
    @SerializedName("rainfall_zone")
    val rainfallZone: String? = null
)

data class CropRecommendation(
    @SerializedName("crop")
    val crop: String,
    @SerializedName("suitability_score")
    val suitabilityScore: Double? = null,
    @SerializedName("confidence")
    val confidence: String? = null,
    @SerializedName("reason")
    val reason: String? = null,
    @SerializedName("soil_match")
    val soilMatch: Boolean = true,
    @SerializedName("water_requirement")
    val waterRequirement: String? = null,
    @SerializedName("duration_days")
    val durationDays: Int? = null
)

data class CropRecommendationsResponse(
    @SerializedName("recommendations")
    val recommendations: List<CropRecommendation> = emptyList(),
    @SerializedName("district")
    val district: String? = null,
    @SerializedName("season")
    val season: String? = null
)

data class CropCalendarStage(
    @SerializedName("stage")
    val stage: String,
    @SerializedName("timing")
    val timing: String,
    @SerializedName("advisory")
    val advisory: String
)

data class CropCalendarEntry(
    @SerializedName("crop")
    val crop: String,
    @SerializedName("season")
    val season: String,
    @SerializedName("sowing_window")
    val sowingWindow: String,
    @SerializedName("harvesting_window")
    val harvestingWindow: String,
    @SerializedName("critical_operations")
    val criticalOperations: List<CropCalendarStage> = emptyList()
)

data class MarketItem(
    @SerializedName("commodity")
    val commodity: String,
    @SerializedName("market")
    val market: String,
    @SerializedName("district")
    val district: String? = null,
    @SerializedName("modal_price")
    val modalPrice: Double? = null,
    @SerializedName("min_price")
    val minPrice: Double? = null,
    @SerializedName("max_price")
    val maxPrice: Double? = null,
    @SerializedName("date")
    val date: String? = null
)

data class AdvisoryItem(
    @SerializedName("id")
    val id: String? = null,
    @SerializedName("title")
    val title: String,
    @SerializedName("date")
    val date: String? = null,
    @SerializedName("category")
    val category: String? = null,
    @SerializedName("summary")
    val summary: String,
    @SerializedName("severity")
    val severity: String = "info",
    @SerializedName("photo_url")
    val photoUrl: String? = null,
    @SerializedName("source")
    val source: String? = null
)

data class CommunityReport(
    @SerializedName("report_id")
    val reportId: String? = null,
    @SerializedName("farmer_name")
    val farmerName: String? = null,
    @SerializedName("village")
    val village: String,
    @SerializedName("crop")
    val crop: String,
    @SerializedName("issue")
    val issue: String,
    @SerializedName("status")
    val status: String = "reported",
    @SerializedName("upvotes")
    val upvotes: Int = 0,
    @SerializedName("created_at")
    val createdAt: String? = null
)

data class VillageLeaderboardEntry(
    @SerializedName("village")
    val village: String,
    @SerializedName("trust_score")
    val trustScore: Double,
    @SerializedName("verified_reports")
    val verifiedReports: Int
)

data class FeedbackRequest(
    @SerializedName("query_id")
    val queryId: String,
    @SerializedName("helpful")
    val helpful: Boolean,
    @SerializedName("feedback_text")
    val feedbackText: String? = null,
    @SerializedName("feedback_type")
    val feedbackType: String? = null,
    @SerializedName("crop")
    val crop: String? = null,
    @SerializedName("outcome_result")
    val outcomeResult: String? = null,
    @SerializedName("outcome_reason")
    val outcomeReason: String? = null
)
