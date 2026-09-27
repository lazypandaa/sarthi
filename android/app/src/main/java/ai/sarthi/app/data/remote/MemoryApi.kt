package ai.sarthi.app.data.remote

import ai.sarthi.app.data.model.HealthResponse
import ai.sarthi.app.data.model.MemorySummaryResponse
import ai.sarthi.app.data.model.TeachMemoryRequest
import ai.sarthi.app.data.model.TeachMemoryResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

interface MemoryApi {

    @GET("api/memory/health")
    suspend fun checkMemoryHealth(): Response<HealthResponse>

    @GET("api/memory/summary")
    suspend fun getMemorySummary(
        @Query("farmer_id") farmerId: String
    ): Response<MemorySummaryResponse>

    @POST("api/memory/teach")
    suspend fun teachMemory(
        @Body request: TeachMemoryRequest
    ): Response<TeachMemoryResponse>
}
