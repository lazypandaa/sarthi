package ai.sarthi.app.data.remote

import ai.sarthi.app.data.model.QueryHistoryItem
import ai.sarthi.app.data.model.TextQueryRequest
import ai.sarthi.app.data.model.VoiceAssistantResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Query

interface VoiceAssistantApi {

    /**
     * Send text query to Sarthi backend.
     * Backend generates response with agricultural ground truth + Hindsight memory context,
     * and synthesizes Indic voice audio via Sarvam Bulbul TTS.
     */
    @POST("process-text")
    suspend fun processText(
        @Body request: TextQueryRequest
    ): Response<VoiceAssistantResponse>

    /**
     * Send audio recording (WAV) to Sarthi backend.
     * Backend transcribes using Sarvam Saaras STT, reasons with agricultural context,
     * and synthesizes regional voice playback via Sarvam Bulbul TTS.
     */
    @Multipart
    @POST("process-audio")
    suspend fun processAudio(
        @Part file: MultipartBody.Part,
        @Part("language") language: RequestBody
    ): Response<VoiceAssistantResponse>

    /**
     * Retrieve past voice/text queries.
     */
    @GET("api/query-history")
    suspend fun getQueryHistory(): Response<List<QueryHistoryItem>>
}
