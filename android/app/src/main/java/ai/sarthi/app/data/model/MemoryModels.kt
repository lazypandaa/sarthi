package ai.sarthi.app.data.model

import com.google.gson.annotations.SerializedName

data class MemorySummaryResponse(
    @SerializedName("farmer_id")
    val farmerId: String,
    @SerializedName("total_memories")
    val totalMemories: Int = 0,
    @SerializedName("categories")
    val categories: Map<String, Int> = emptyMap(),
    @SerializedName("hindsight_status")
    val hindsightStatus: String = "online"
)

data class TeachMemoryRequest(
    @SerializedName("farmer_id")
    val farmerId: String,
    @SerializedName("type")
    val type: String,
    @SerializedName("content")
    val content: String,
    @SerializedName("crop")
    val crop: String? = null
)

data class TeachMemoryResponse(
    @SerializedName("status")
    val status: String,
    @SerializedName("memory_id")
    val memoryId: String? = null,
    @SerializedName("message")
    val message: String
)
