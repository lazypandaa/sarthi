package ai.sarthi.app.data.remote

import ai.sarthi.app.data.model.AdvisoryItem
import ai.sarthi.app.data.model.CommunityReport
import ai.sarthi.app.data.model.CropCalendarEntry
import ai.sarthi.app.data.model.CropRecommendationsResponse
import ai.sarthi.app.data.model.EnvironmentalProfile
import ai.sarthi.app.data.model.FeedbackRequest
import ai.sarthi.app.data.model.HealthResponse
import ai.sarthi.app.data.model.MarketItem
import ai.sarthi.app.data.model.VillageLeaderboardEntry
import ai.sarthi.app.data.model.WeatherInfo
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface AgriDataApi {

    @GET("health")
    suspend fun checkHealth(): Response<HealthResponse>

    @GET("api/weather")
    suspend fun getWeather(
        @Query("location") location: String? = null
    ): Response<WeatherInfo>

    @GET("api/environmental-profile")
    suspend fun getEnvironmentalProfile(
        @Query("location") location: String? = null
    ): Response<EnvironmentalProfile>

    @GET("api/crop-recommendations")
    suspend fun getCropRecommendations(
        @Query("location") location: String? = null
    ): Response<CropRecommendationsResponse>

    @GET("api/crop-calendar")
    suspend fun getCropCalendar(
        @Query("district") district: String? = null,
        @Query("season") season: String? = null
    ): Response<List<CropCalendarEntry>>

    @GET("api/markets")
    suspend fun getMarketPrices(
        @Query("district") district: String? = null
    ): Response<List<MarketItem>>

    @GET("api/agriculture-news")
    suspend fun getAdvisories(): Response<List<AdvisoryItem>>

    @GET("api/community-reports")
    suspend fun getCommunityReports(): Response<List<CommunityReport>>

    @POST("api/community-reports")
    suspend fun submitCommunityReport(
        @Body report: CommunityReport
    ): Response<Map<String, Any>>

    @GET("api/village-leaderboard")
    suspend fun getVillageLeaderboard(): Response<List<VillageLeaderboardEntry>>

    @POST("api/feedback")
    suspend fun submitFeedback(
        @Body feedback: FeedbackRequest
    ): Response<Map<String, Any>>
}
