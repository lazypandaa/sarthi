package ai.sarthi.app.data.model

import com.google.gson.annotations.SerializedName

data class HindsightMemoryItem(
    @SerializedName("id")
    val id: String? = null,
    @SerializedName("text")
    val text: String,
    @SerializedName("type")
    val type: String,
    @SerializedName("source")
    val source: String? = "Farmer Query",
    @SerializedName("crop")
    val crop: String? = null,
    @SerializedName("reason")
    val reason: String? = null
)

data class MemorySections(
    @SerializedName("past_experience")
    val pastExperience: List<HindsightMemoryItem> = emptyList(),
    @SerializedName("learned_from_you")
    val learnedFromYou: List<HindsightMemoryItem> = emptyList()
)

data class WhatChangedItem(
    @SerializedName("trigger")
    val trigger: String,
    @SerializedName("summary")
    val summary: String,
    @SerializedName("impact")
    val impact: String
)

data class MemorySummaryResponse(
    @SerializedName("farmer_id")
    val farmerId: String = "",
    @SerializedName("memory_count")
    val memoryCount: Int = 4,
    @SerializedName("sections")
    val sections: MemorySections = MemorySections(),
    @SerializedName("what_changed")
    val whatChanged: List<WhatChangedItem> = emptyList()
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
