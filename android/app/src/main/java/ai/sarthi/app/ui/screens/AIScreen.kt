package ai.sarthi.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.data.model.CropRecommendationItem
import ai.sarthi.app.data.model.MemorySummaryResponse
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.ButtonKind
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiAmberBg
import ai.sarthi.app.ui.theme.SarthiAmberText
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun AIScreen(
    user: UserProfile,
    cropRecs: List<CropRecommendationItem>,
    memorySummary: MemorySummaryResponse,
    onAskAI: (String, String) -> Unit,
    onNavigate: (String) -> Unit
) {
    var queryText by remember {
        mutableStateOf("What crop should I grow this season given my farm constraints?")
    }
    var selectedCrop by remember {
        mutableStateOf(cropRecs.firstOrNull()?.cropName ?: "Groundnut")
    }
    var feedbackGiven by remember { mutableStateOf(false) }

    val memoriesCount = memorySummary.memoryCount

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Sarthi AI Agronomist",
            onNotificationClick = { onNavigate("notifications") }
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            // Intro
            Text(
                text = "Adaptive Agronomy Intelligence",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Personalized using Hindsight Vectorize Memory Graph. Sarthi recalls your borewell hours, past crop failures, and soil conditions.",
                fontSize = 11.5.sp,
                color = SarthiMuted,
                lineHeight = 16.sp
            )

            Spacer(modifier = Modifier.height(16.dp))

            // ================= QUERY INPUT CARD =================
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "ASK SPECIFIC ADVICE",
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold,
                            color = SarthiMuted,
                            letterSpacing = 0.5.sp
                        )
                        SarthiBadge(text = "$memoriesCount Farm Memories", tone = BadgeTone.Green)
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedTextField(
                        value = queryText,
                        onValueChange = { queryText = it },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = SarthiGreen,
                            unfocusedBorderColor = SarthiLine,
                            focusedContainerColor = SarthiSurface,
                            unfocusedContainerColor = SarthiSurface
                        ),
                        minLines = 2,
                        maxLines = 4
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    SarthiButton(
                        text = "Consult Sarthi AI",
                        icon = "spark",
                        onClick = { onAskAI(queryText, selectedCrop) },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // ================= COMPARATIVE ANALYSIS CARD =================
            SarthiSectionTitle(title = "Hindsight Memory Impact Comparison")
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "WITHOUT FARM MEMORY (GENERIC)",
                        fontSize = 8.5.sp,
                        fontWeight = FontWeight.Bold,
                        color = SarthiMuted,
                        letterSpacing = 0.5.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(SarthiAmberBg, RoundedCornerShape(10.dp))
                            .padding(10.dp)
                    ) {
                        Text(
                            text = "Generic regional advisory: Recommends High-Yield Tomato or BPT Paddy based solely on state weather tables. Fails to account for 1-hour borewell water limit.",
                            color = SarthiAmberText,
                            fontSize = 11.sp,
                            lineHeight = 15.sp
                        )
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "WITH SARTHI HINDSIGHT RETENTION (PERSONALIZED)",
                        fontSize = 8.5.sp,
                        fontWeight = FontWeight.Bold,
                        color = SarthiGreen,
                        letterSpacing = 0.5.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(SarthiMint, RoundedCornerShape(10.dp))
                            .padding(10.dp)
                    ) {
                        Text(
                            text = "Sarthi recalled: \"1-hour borewell capacity\", \"Past tomato leaf curl loss\". Filtered out water-heavy crops. Recommends Black Gram (Urad) or Groundnut with drought-tolerant seed treatment.",
                            color = SarthiGreen,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold,
                            lineHeight = 15.sp
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            SarthiIcon(name = "check", size = 14.dp, tint = SarthiGreen)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "Water availability constraint prioritized (1 hr/day limit)",
                                fontSize = 10.sp,
                                color = SarthiText
                            )
                        }
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            SarthiIcon(name = "check", size = 14.dp, tint = SarthiGreen)
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "Past crop failure risk avoided (leaf curl recurrence)",
                                fontSize = 10.sp,
                                color = SarthiText
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    // Feedback row
                    if (!feedbackGiven) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Was this advice accurate for your farm?",
                                fontSize = 11.sp,
                                color = SarthiMuted
                            )
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                SarthiButton(
                                    text = "Helpful",
                                    icon = "thumbup",
                                    kind = ButtonKind.Soft,
                                    onClick = { feedbackGiven = true },
                                    modifier = Modifier.height(36.dp)
                                )
                                SarthiButton(
                                    text = "Not fit",
                                    icon = "thumbdown",
                                    kind = ButtonKind.Ghost,
                                    onClick = { feedbackGiven = true },
                                    modifier = Modifier.height(36.dp)
                                )
                            }
                        }
                    } else {
                        Text(
                            text = "✓ Feedback retained in Sarthi Memory Graph!",
                            color = SarthiGreen,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Action button to teach Sarthi
            SarthiButton(
                text = "Teach Sarthi New Farm Memory",
                icon = "brain",
                kind = ButtonKind.Soft,
                onClick = { onNavigate("memory") },
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
