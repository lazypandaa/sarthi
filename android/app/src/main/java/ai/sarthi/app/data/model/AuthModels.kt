package ai.sarthi.app.data.model

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("password")
    val password: String
)

data class SignupRequest(
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("password")
    val password: String,
    @SerializedName("language")
    val language: String = "hi",
    @SerializedName("location")
    val location: String
)

data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String = "bearer"
)

data class UserProfile(
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("language")
    val language: String,
    @SerializedName("location")
    val location: String,
    @SerializedName("created_at")
    val createdAt: String? = null
)
