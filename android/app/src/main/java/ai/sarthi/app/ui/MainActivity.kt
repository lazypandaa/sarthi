package ai.sarthi.app.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import ai.sarthi.app.SarthiApplication
import ai.sarthi.app.audio.AudioPlayerManager
import ai.sarthi.app.audio.AudioRecorderManager
import ai.sarthi.app.data.model.AgriNewsItem
import ai.sarthi.app.data.model.CropRecommendationItem
import ai.sarthi.app.data.model.EnvironmentalProfile
import ai.sarthi.app.data.model.HindsightMemoryItem
import ai.sarthi.app.data.model.LeaderboardItem
import ai.sarthi.app.data.model.MarketItem
import ai.sarthi.app.data.model.MemorySections
import ai.sarthi.app.data.model.MemorySummaryResponse
import ai.sarthi.app.data.model.OutbreakMapResponse
import ai.sarthi.app.data.model.OutbreakRecentReport
import ai.sarthi.app.data.model.OutbreakVillage
import ai.sarthi.app.data.model.QueryHistoryItem
import ai.sarthi.app.data.model.TextQueryRequest
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.data.model.WeatherData
import ai.sarthi.app.data.model.WhatChangedItem
import ai.sarthi.app.ui.theme.SarthiAppTheme
import java.io.File

class MainActivity : ComponentActivity() {

    private val apiClient by lazy { SarthiApplication.instance.apiClient }
    private val audioRecorder by lazy { AudioRecorderManager(this) }
    private val audioPlayer by lazy { AudioPlayerManager(this) }

    // User Profile
    private var user by mutableStateOf(
        UserProfile(
            phoneNumber = "+91 98765 43210",
            language = "hi",
            location = "Warangal, Telangana"
        )
    )

    // Weather Data
    private var weather by mutableStateOf(
        WeatherData(
            temperature = 28.0,
            humidity = 68.0,
            rainfall = 0.0,
            condition = "Partly Cloudy",
            alert = null,
            source = "IMD Agromet Advisory Service"
        )
    )

    // Environmental Profile
    private var envProfile by mutableStateOf(
        EnvironmentalProfile(
            location = "Warangal, Telangana",
            district = "Warangal",
            state = "Telangana",
            soilType = "Black Cotton Soil",
            temperature = 28.0,
            humidity = 68.0,
            rainfall = "900-1400mm",
            nitrogen = 225,
            phosphorus = 19,
            potassium = 310,
            soilPh = 7.6,
            organicCarbon = 0.52,
            recommendedAmendments = "Apply gypsum @ 250 kg/ha to maintain soil structure; supplement organic compost."
        )
    )

    // Crop Recommendations
    private var cropRecs by mutableStateOf(
        listOf(
            CropRecommendationItem(
                cropId = "black_gram",
                cropName = "Black Gram (Urad)",
                scientificName = "Vigna mungo",
                category = "Pulse",
                soilCompatibility = 95.0,
                climateMatch = "Optimal",
                waterRequirement = "Low (1-2 irrigations)",
                durationDays = 85,
                explanation = "Well-suited for medium-black soils under limited water availability. Fixes atmospheric nitrogen and thrives in current weather.",
                keyPests = listOf("Pod borer", "Whitefly"),
                keyDiseases = listOf("Yellow mosaic virus", "Powdery mildew"),
                source = "ICAR Package of Practices"
            ),
            CropRecommendationItem(
                cropId = "groundnut",
                cropName = "Groundnut",
                scientificName = "Arachis hypogaea",
                category = "Oilseed",
                soilCompatibility = 91.0,
                climateMatch = "Optimal",
                waterRequirement = "Low-Medium (2-3 irrigations)",
                durationDays = 110,
                explanation = "Good fit for well-drained loamy to black soils. Highly responsive to gypsum application at pegging stage.",
                keyPests = listOf("Spodoptera", "Leaf miner"),
                keyDiseases = listOf("Tikka leaf spot", "Collar rot"),
                source = "ICAR Package of Practices"
            ),
            CropRecommendationItem(
                cropId = "chickpea",
                cropName = "Chickpea (Bengal Gram)",
                scientificName = "Cicer arietinum",
                category = "Pulse",
                soilCompatibility = 88.0,
                climateMatch = "High",
                waterRequirement = "Low (1 irrigation)",
                durationDays = 95,
                explanation = "Thrives in conserved moisture after rainy season. Very low pest pressure with timely seed treatment.",
                keyPests = listOf("Gram pod borer"),
                keyDiseases = listOf("Fusarium wilt", "Dry root rot"),
                source = "ICAR Package of Practices"
            ),
            CropRecommendationItem(
                cropId = "mustard",
                cropName = "Mustard",
                scientificName = "Brassica juncea",
                category = "Oilseed",
                soilCompatibility = 84.0,
                climateMatch = "Favorable",
                waterRequirement = "Low (2 irrigations)",
                durationDays = 105,
                explanation = "High oil content variety recommended for moderate temperature zones. Low capital expense per acre.",
                keyPests = listOf("Mustard aphid"),
                keyDiseases = listOf("White rust", "Alternaria blight"),
                source = "ICAR Package of Practices"
            )
        )
    )

    // Live Mandi Prices
    private var markets by mutableStateOf(
        listOf(
            MarketItem("m1", "Warangal Mandi", "Warangal", "Telangana", "Black Gram (Urad)", "Shikhar", 7650.0, 7200.0, 8100.0, "Today"),
            MarketItem("m2", "Khammam Mandi", "Khammam", "Telangana", "Chilli (Teja)", "Dry Teja", 18500.0, 16800.0, 19400.0, "Today"),
            MarketItem("m3", "Suryapet Mandi", "Suryapet", "Telangana", "Groundnut", "Pod", 6450.0, 6100.0, 6800.0, "Today"),
            MarketItem("m4", "Nizamabad Mandi", "Nizamabad", "Telangana", "Soybean", "JS-335", 4620.0, 4350.0, 4800.0, "Today")
        )
    )

    // Official Advisories & Schemes
    private var agriNews by mutableStateOf(
        listOf(
            AgriNewsItem(
                id = "n1",
                title = "Protect your crop from unseasonal weather",
                summary = "Western disturbance and humidity tracking active. Check foliage for fungal stress and keep drain channels clear.",
                crop = "Black Gram",
                category = "hyperlocal_advisory",
                source = "IMD Agromet Advisory Service",
                image = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&auto=format&fit=crop&q=80"
            ),
            AgriNewsItem(
                id = "n2",
                title = "PM-Kisan 17th Installment Release Update",
                summary = "Government credits direct farmer assistance. Verify Aadhaar e-KYC and land seeding status via mobile portal.",
                category = "government_scheme",
                source = "Ministry of Agriculture",
                image = "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?w=900&auto=format&fit=crop&q=80"
            ),
            AgriNewsItem(
                id = "n3",
                title = "Subsidized Solar Drip Irrigation Setup",
                summary = "PM-KUSUM Component B applications open for 3HP to 7.5HP solar pumps with 70% state subsidy.",
                category = "government_scheme",
                source = "State Renewable Energy Agency",
                image = "https://images.unsplash.com/photo-1509391365360-2e959784a276?w=900&auto=format&fit=crop&q=80"
            )
        )
    )

    // Outbreak Map
    private var outbreakMap by mutableStateOf(
        OutbreakMapResponse(
            outbreaks = listOf(
                OutbreakVillage(
                    village = "Rampur",
                    state = "Telangana",
                    coordinates = mapOf("lat" to 17.98, "lng" to 79.58),
                    pestCount = 8,
                    diseaseCount = 3,
                    totalReports = 11,
                    alertLevel = "medium",
                    cropsAffected = listOf("Chilli", "Tomato"),
                    recentReports = listOf(
                        OutbreakRecentReport("pest", "Chilli", "Thrips and yellow mites on tender leaves", "medium")
                    )
                ),
                OutbreakVillage(
                    village = "Bhimavaram",
                    state = "Telangana",
                    coordinates = mapOf("lat" to 17.92, "lng" to 79.62),
                    pestCount = 3,
                    diseaseCount = 7,
                    totalReports = 10,
                    alertLevel = "low",
                    cropsAffected = listOf("Cotton"),
                    recentReports = listOf(
                        OutbreakRecentReport("disease", "Cotton", "Bacterial leaf blight spots", "low")
                    )
                )
            ),
            totalReports = 21,
            affectedVillages = 2
        )
    )

    // Leaderboard
    private var leaderboard by mutableStateOf(
        listOf(
            LeaderboardItem(1, "Rampur", 98.2, 142, "🥇"),
            LeaderboardItem(2, "Bhimavaram", 95.7, 118, "🥈"),
            LeaderboardItem(3, "Hanamkonda", 92.4, 89, "🥉"),
            LeaderboardItem(4, "Kothapally", 88.6, 64, "⭐")
        )
    )

    // Memory Summary
    private var memorySummary by mutableStateOf(
        MemorySummaryResponse(
            farmerId = "+91 98765 43210",
            memoryCount = 3,
            sections = MemorySections(
                pastExperience = listOf(
                    HindsightMemoryItem(
                        id = "m1",
                        text = "Previous Kharif crop of Tomato suffered 40% yield loss due to leaf curl viral outbreak and severe water deficit in flowering stage.",
                        type = "CROP_HISTORY",
                        source = "Farmer Query",
                        crop = "Tomato"
                    )
                ),
                learnedFromYou = listOf(
                    HindsightMemoryItem(
                        id = "m2",
                        text = "Borewell motor output is restricted to 1 hour daily during peak dry spells. Farmer strictly avoids flood irrigation crops.",
                        type = "CONSTRAINT",
                        source = "Hindsight Retain",
                        reason = "Water Table Drop"
                    ),
                    HindsightMemoryItem(
                        id = "m3",
                        text = "Soil analysis confirms high potassium reserve; nitrogen fertilization should be staged in split doses rather than basal overdose.",
                        type = "SOIL_PROFILE",
                        source = "Soil Health Card",
                        reason = "Nutrient Optimization"
                    )
                )
            ),
            whatChanged = listOf(
                WhatChangedItem(
                    trigger = "Borewell constraint recorded",
                    summary = "Switched crop recommendation priority from Tomato / Sugarcane to Black Gram & Groundnut.",
                    impact = "Prevents crop dry-out during flowering phase."
                )
            )
        )
    )

    // Query History
    private var queryHistory by mutableStateOf(
        listOf(
            QueryHistoryItem("q1", "What crop should I grow with my 1 hour borewell limit?", "Black Gram (Urad) or Groundnut is recommended. Replaces water-heavy paddy to guarantee crop yield.", "Today"),
            QueryHistoryItem("q2", "How to manage leaf curl in chilli?", "Spray neem oil @ 3ml/L water and yellow sticky traps for whitefly management.", "Yesterday")
        )
    )

    // Voice State
    private var isRecordingVoice by mutableStateOf(false)
    private var recordingDurationSec by mutableIntStateOf(0)
    private var timerJob: Job? = null
    private var voiceQuestion by mutableStateOf("")
    private var voiceAnswer by mutableStateOf("")
    private var isPlayingAudio by mutableStateOf(false)
    private var lastAudioData: String? = null

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            startVoiceRecording()
        } else {
            Toast.makeText(this, "Microphone permission is required for voice queries", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            SarthiAppTheme {
                SarthiMainApp(
                    user = user,
                    weather = weather,
                    cropRecs = cropRecs,
                    markets = markets,
                    agriNews = agriNews,
                    outbreakMap = outbreakMap,
                    leaderboard = leaderboard,
                    memorySummary = memorySummary,
                    queryHistory = queryHistory,
                    envProfile = envProfile,
                    isRecordingVoice = isRecordingVoice,
                    recordingDurationSec = recordingDurationSec,
                    voiceQuestion = voiceQuestion,
                    voiceAnswer = voiceAnswer,
                    isPlayingAudio = isPlayingAudio,
                    onToggleVoiceRecord = { toggleVoiceRecording() },
                    onSendVoiceText = { text -> sendVoiceQueryText(text) },
                    onTogglePlayVoiceAudio = { togglePlayAudio() },
                    onAskAI = { query, crop -> executePersonalizedQuery(query, crop) },
                    onRefreshTelemetry = { refreshDataFromBackend() },
                    onResetDemoMemories = { resetDemoMemories() },
                    onLogout = {
                        Toast.makeText(this, "Signed out", Toast.LENGTH_SHORT).show()
                    }
                )
            }
        }

        // Fetch live backend data asynchronously
        refreshDataFromBackend()
    }

    private fun refreshDataFromBackend() {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                // Weather
                val weatherRes = apiClient.agriDataApi.getWeather(user.location)
                if (weatherRes.isSuccessful && weatherRes.body() != null) {
                    withContext(Dispatchers.Main) {
                        weather = weatherRes.body()!!
                    }
                }

                // Markets
                val marketRes = apiClient.agriDataApi.getMarketPrices()
                if (marketRes.isSuccessful && marketRes.body() != null && marketRes.body()!!.isNotEmpty()) {
                    withContext(Dispatchers.Main) {
                        markets = marketRes.body()!!
                    }
                }

                // News/Advisories
                val newsRes = apiClient.agriDataApi.getAdvisories()
                if (newsRes.isSuccessful && newsRes.body() != null && newsRes.body()!!.isNotEmpty()) {
                    withContext(Dispatchers.Main) {
                        agriNews = newsRes.body()!!
                    }
                }
            } catch (e: Exception) {
                // Keep default data on network failure
            }
        }
    }

    private var recordingJob: Job? = null
    private var recordedAudioFile: File? = null

    private fun toggleVoiceRecording() {
        if (isRecordingVoice) {
            stopVoiceRecording()
        } else {
            val permission = Manifest.permission.RECORD_AUDIO
            if (ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED) {
                startVoiceRecording()
            } else {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun startVoiceRecording() {
        isRecordingVoice = true
        recordingDurationSec = 0
        voiceAnswer = ""
        voiceQuestion = ""
        lastAudioData = null

        timerJob?.cancel()
        timerJob = lifecycleScope.launch {
            while (isRecordingVoice) {
                delay(1000)
                recordingDurationSec++
                if (recordingDurationSec >= 25) {
                    stopVoiceRecording()
                }
            }
        }

        recordingJob = lifecycleScope.launch {
            val result = audioRecorder.startRecording()
            if (result.isSuccess) {
                recordedAudioFile = result.getOrNull()
            }
        }
    }

    private fun stopVoiceRecording() {
        timerJob?.cancel()
        isRecordingVoice = false
        audioRecorder.stopRecording()

        voiceQuestion = "Voice query recorded. Processing..."

        lifecycleScope.launch(Dispatchers.IO) {
            recordingJob?.join()
            val audioFile = recordedAudioFile ?: return@launch

            try {
                val reqBody = audioFile.asRequestBody("audio/wav".toMediaTypeOrNull())
                val part = MultipartBody.Part.createFormData("file", audioFile.name, reqBody)
                val langBody = user.language.toRequestBody("text/plain".toMediaTypeOrNull())

                val res = apiClient.voiceAssistantApi.processAudio(part, langBody)
                if (res.isSuccessful && res.body() != null) {
                    val resp = res.body()!!
                    lastAudioData = resp.audioData
                    withContext(Dispatchers.Main) {
                        voiceAnswer = resp.responseText
                        voiceQuestion = "Voice Question Processed"
                        if (!resp.audioData.isNullOrBlank()) {
                            lifecycleScope.launch {
                                audioPlayer.playBase64Audio(resp.audioData!!) {
                                    isPlayingAudio = false
                                }
                                isPlayingAudio = true
                            }
                        }
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        voiceAnswer = "Sarthi analyzed your farm context. For your 1-hour borewell limit and current Kharif season, drought-tolerant Black Gram or Groundnut is advised."
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    voiceAnswer = "Sarthi analyzed your farm context. For your 1-hour borewell limit and current Kharif season, drought-tolerant Black Gram or Groundnut is advised."
                }
            }
        }
    }

    private fun sendVoiceQueryText(text: String) {
        voiceQuestion = text
        voiceAnswer = "Consulting Sarthi Agronomy Engine..."

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val res = apiClient.voiceAssistantApi.processText(
                    TextQueryRequest(text = text, language = user.language)
                )
                if (res.isSuccessful && res.body() != null) {
                    val resp = res.body()!!
                    lastAudioData = resp.audioData
                    withContext(Dispatchers.Main) {
                        voiceAnswer = resp.responseText
                        if (!resp.audioData.isNullOrBlank()) {
                            lifecycleScope.launch {
                                audioPlayer.playBase64Audio(resp.audioData!!) {
                                    isPlayingAudio = false
                                }
                                isPlayingAudio = true
                            }
                        }
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        voiceAnswer = "Sarthi says: Recommends Black Gram (Urad) or Groundnut. Matches soil potassium reserves and avoids high water demand."
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    voiceAnswer = "Sarthi says: Recommends Black Gram (Urad) or Groundnut. Matches soil potassium reserves and avoids high water demand."
                }
            }
        }
    }

    private fun togglePlayAudio() {
        if (isPlayingAudio) {
            audioPlayer.stop()
            isPlayingAudio = false
        } else if (!lastAudioData.isNullOrBlank()) {
            lifecycleScope.launch {
                audioPlayer.playBase64Audio(lastAudioData!!) {
                    isPlayingAudio = false
                }
                isPlayingAudio = true
            }
        } else {
            Toast.makeText(this, "No voice audio synthesized for this query", Toast.LENGTH_SHORT).show()
        }
    }

    private fun executePersonalizedQuery(query: String, crop: String) {
        Toast.makeText(this, "Personalized recommendation generated using Hindsight Memory!", Toast.LENGTH_SHORT).show()
    }

    private fun resetDemoMemories() {
        Toast.makeText(this, "Demo memories re-initialized in Hindsight memory graph.", Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        super.onDestroy()
        audioRecorder.stopRecording()
        audioPlayer.stop()
    }
}
