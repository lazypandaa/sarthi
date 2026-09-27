package ai.sarthi.app.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import kotlinx.coroutines.launch
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
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.data.model.WeatherData
import ai.sarthi.app.ui.components.SarthiBottomNav
import ai.sarthi.app.ui.screens.AIScreen
import ai.sarthi.app.ui.screens.AdviceScreen
import ai.sarthi.app.ui.screens.CommunityScreen
import ai.sarthi.app.ui.screens.CropCalendarScreen
import ai.sarthi.app.ui.screens.CropDetailScreen
import ai.sarthi.app.ui.screens.HomeScreen
import ai.sarthi.app.ui.screens.MemoryScreen
import ai.sarthi.app.ui.screens.NotificationsScreen
import ai.sarthi.app.ui.screens.ProfileScreen
import ai.sarthi.app.ui.screens.VoiceScreen
import ai.sarthi.app.ui.screens.WeatherDetailScreen
import ai.sarthi.app.ui.theme.SarthiBg

@Composable
fun SarthiMainApp(
    user: UserProfile,
    weather: WeatherData,
    cropRecs: List<CropRecommendationItem>,
    markets: List<MarketItem>,
    agriNews: List<AgriNewsItem>,
    outbreakMap: OutbreakMapResponse,
    leaderboard: List<LeaderboardItem>,
    memorySummary: MemorySummaryResponse,
    queryHistory: List<QueryHistoryItem>,
    envProfile: EnvironmentalProfile,
    isRecordingVoice: Boolean,
    recordingDurationSec: Int,
    voiceQuestion: String,
    voiceAnswer: String,
    isPlayingAudio: Boolean,
    onToggleVoiceRecord: () -> Unit,
    onSendVoiceText: (String) -> Unit,
    onTogglePlayVoiceAudio: () -> Unit,
    onAskAI: (String, String) -> Unit,
    onRefreshTelemetry: () -> Unit,
    onResetDemoMemories: () -> Unit,
    onLogout: () -> Unit
) {
    var currentPage by remember { mutableStateOf("home") }
    var activeTab by remember { mutableStateOf("home") }
    val pageHistory = remember { mutableStateListOf<String>() }
    var selectedCropItem by remember { mutableStateOf(cropRecs.firstOrNull()) }

    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    fun navigate(to: String) {
        if (to in listOf("home", "advice", "ai", "community", "profile")) {
            activeTab = to
        }
        pageHistory.add(currentPage)
        currentPage = to
    }

    fun goBack() {
        if (pageHistory.isNotEmpty()) {
            val prev = pageHistory.removeAt(pageHistory.lastIndex)
            currentPage = prev
            if (prev in listOf("home", "advice", "ai", "community", "profile")) {
                activeTab = prev
            }
        } else {
            currentPage = "home"
            activeTab = "home"
        }
    }

    BackHandler(enabled = currentPage != "home") {
        goBack()
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = SarthiBg,
        snackbarHost = { SnackbarHost(snackbarHostState) },
        bottomBar = {
            // Permanently anchored Bottom Nav across main and sub tabs
            SarthiBottomNav(
                activeTab = activeTab,
                onTabSelected = { tab ->
                    activeTab = tab
                    currentPage = tab
                },
                modifier = Modifier.navigationBarsPadding()
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .background(SarthiBg)
        ) {
            when (currentPage) {
                "home" -> HomeScreen(
                    user = user,
                    weather = weather,
                    cropRecs = cropRecs,
                    agriNews = agriNews,
                    outbreakMap = outbreakMap,
                    memoriesCount = memorySummary.memoryCount,
                    onNavigate = { navigate(it) }
                )

                "advice" -> AdviceScreen(
                    cropRecs = cropRecs,
                    markets = markets,
                    agriNews = agriNews,
                    onSelectCrop = { crop ->
                        selectedCropItem = crop
                        navigate("crop")
                    },
                    onNavigate = { navigate(it) }
                )

                "ai" -> AIScreen(
                    user = user,
                    cropRecs = cropRecs,
                    memorySummary = memorySummary,
                    onAskAI = onAskAI,
                    onNavigate = { navigate(it) }
                )

                "community" -> CommunityScreen(
                    outbreakMap = outbreakMap,
                    leaderboard = leaderboard,
                    onNavigate = { navigate(it) }
                )

                "profile" -> ProfileScreen(
                    user = user,
                    envProfile = envProfile,
                    memoriesCount = memorySummary.memoryCount,
                    queryHistory = queryHistory,
                    onLogout = onLogout,
                    onNavigate = { navigate(it) }
                )

                "weather" -> WeatherDetailScreen(
                    user = user,
                    weather = weather,
                    envProfile = envProfile,
                    onRefresh = onRefreshTelemetry,
                    onBack = { goBack() }
                )

                "calendar" -> CropCalendarScreen(
                    onBack = { goBack() }
                )

                "crop" -> CropDetailScreen(
                    crop = selectedCropItem ?: cropRecs.first(),
                    onBack = { goBack() }
                )

                "memory" -> MemoryScreen(
                    memorySummary = memorySummary,
                    onTeachMemory = {
                        scope.launch {
                            snackbarHostState.showSnackbar("Recorded new hindsight farm constraint.")
                        }
                    },
                    onResetDemo = onResetDemoMemories,
                    onBack = { goBack() }
                )

                "voice" -> VoiceScreen(
                    user = user,
                    isRecording = isRecordingVoice,
                    recordingDurationSec = recordingDurationSec,
                    question = voiceQuestion,
                    answer = voiceAnswer,
                    isPlayingAudio = isPlayingAudio,
                    onToggleRecord = onToggleVoiceRecord,
                    onSendText = onSendVoiceText,
                    onTogglePlayAudio = onTogglePlayVoiceAudio,
                    onBack = { goBack() }
                )

                "notifications" -> NotificationsScreen(
                    onBack = { goBack() }
                )

                else -> HomeScreen(
                    user = user,
                    weather = weather,
                    cropRecs = cropRecs,
                    agriNews = agriNews,
                    outbreakMap = outbreakMap,
                    memoriesCount = memorySummary.memoryCount,
                    onNavigate = { navigate(it) }
                )
            }
        }
    }
}
