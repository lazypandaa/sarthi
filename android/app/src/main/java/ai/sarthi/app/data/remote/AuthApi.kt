package ai.sarthi.app.data.remote

import ai.sarthi.app.data.model.AuthResponse
import ai.sarthi.app.data.model.LoginRequest
import ai.sarthi.app.data.model.SignupRequest
import ai.sarthi.app.data.model.UserProfile
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface AuthApi {

    @POST("api/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>

    @POST("api/signup")
    suspend fun signup(@Body request: SignupRequest): Response<AuthResponse>

    @GET("api/me")
    suspend fun getProfile(): Response<UserProfile>
}
