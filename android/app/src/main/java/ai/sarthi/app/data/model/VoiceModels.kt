package ai.sarthi.app.data.model

import com.google.gson.annotations.SerializedName

data class TextQueryRequest(
    @SerializedName("text")
    val text: String,
    @SerializedName("language")
    val language: String = "hi"
)

data class MemoryItem(
    @SerializedName("id")
    val id: String? = null,
    @SerializedName("category")
    val category: String? = null,
    @SerializedName("type")
    val type: String? = null,
    @SerializedName("summary")
    val summary: String? = null,
    @SerializedName("crop")
    val crop: String? = null
)

data class MemoryContextInfo(
    @SerializedName("used")
    val used: Boolean = false,
    @SerializedName("memory_count")
    val memoryCount: Int = 0,
    @SerializedName("types")
    val types: List<String> = emptyList(),
    @SerializedName("items")
    val items: List<MemoryItem> = emptyList()
)

data class RetainedLearningInfo(
    @SerializedName("retained")
    val retained: Boolean = false,
    @SerializedName("fact")
    val fact: String? = null,
    @SerializedName("category")
    val category: String? = null
)

data class VoiceAssistantResponse(
    @SerializedName("query_id")
    val queryId: String,
    @SerializedName("recommendation_id")
    val recommendationId: String? = null,
    @SerializedName("transcript")
    val transcript: String? = null,
    @SerializedName("response_text")
    val responseText: String,
    @SerializedName("audio_data")
    val audioData: String? = null,
    @SerializedName("retained_learning")
    val retainedLearning: RetainedLearningInfo? = null,
    @SerializedName("memory_context")
    val memoryContext: MemoryContextInfo? = null
)

data class QueryHistoryItem(
    @SerializedName("query_id")
    val queryId: String,
    @SerializedName("query_text")
    val queryText: String,
    @SerializedName("response_text")
    val responseText: String,
    @SerializedName("language")
    val language: String,
    @SerializedName("timestamp")
    val timestamp: String
)
