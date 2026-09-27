package ai.sarthi.app.data.remote

import ai.sarthi.app.data.model.AgriNewsItem
import ai.sarthi.app.data.model.CropRecommendationItem
import ai.sarthi.app.data.model.EnvironmentalProfile
import ai.sarthi.app.data.model.LeaderboardItem
import ai.sarthi.app.data.model.MarketItem
import ai.sarthi.app.data.model.OutbreakMapResponse
import ai.sarthi.app.data.model.WeatherData
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface AgriDataApi {

    @GET("api/weather")
    suspend fun getWeather(
        @Query("location") location: String? = null
    ): Response<WeatherData>

    @GET("api/environmental-profile")
    suspend fun getEnvironmentalProfile(
        @Query("location") location: String? = null
    ): Response<EnvironmentalProfile>

    @GET("api/crop-recommendations")
    suspend fun getCropRecommendations(
        @Query("location") location: String? = null
    ): Response<List<CropRecommendationItem>>

    @GET("api/markets")
    suspend fun getMarketPrices(
        @Query("district") district: String? = null
    ): Response<List<MarketItem>>

    @GET("api/agriculture-news")
    suspend fun getAdvisories(): Response<List<AgriNewsItem>>

    @GET("api/village-leaderboard")
    suspend fun getVillageLeaderboard(): Response<List<LeaderboardItem>>

    @GET("api/outbreak-radar")
    suspend fun getOutbreakMap(): Response<OutbreakMapResponse>
}
