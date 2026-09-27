package ai.sarthi.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.data.model.LeaderboardItem
import ai.sarthi.app.data.model.OutbreakMapResponse
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun CommunityScreen(
    outbreakMap: OutbreakMapResponse,
    leaderboard: List<LeaderboardItem>,
    onNavigate: (String) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Community Network & Outbreaks",
            onNotificationClick = { onNavigate("notifications") }
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            // Intro
            Text(
                text = "Village Outbreak Radar",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Real-time farmer pest reports, geographic outbreak clusters, and trust index.",
                fontSize = 11.5.sp,
                color = SarthiMuted,
                lineHeight = 16.sp
            )

            // ================= 1. OUTBREAK CLUSTERS =================
            SarthiSectionTitle(title = "Geographic Outbreak Clusters")
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                if (outbreakMap.outbreaks.isNotEmpty()) {
                    for (ob in outbreakMap.outbreaks) {
                        val tone = when (ob.alertLevel.lowercase()) {
                            "high" -> BadgeTone.Danger
                            "medium" -> BadgeTone.Amber
                            else -> BadgeTone.Green
                        }

                        val lat = ob.coordinates["lat"] ?: 17.96
                        val lng = ob.coordinates["lng"] ?: 79.59

                        SarthiCard {
                            Column(modifier = Modifier.padding(14.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            SarthiIcon(name = "pin", size = 14.dp, tint = SarthiGreen)
                                            Spacer(modifier = Modifier.width(4.dp))
                                            Text(
                                                text = "${ob.village}, ${ob.state}",
                                                fontSize = 13.5.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = SarthiText
                                            )
                                        }
                                        Text(
                                            text = "Coordinates: ${String.format("%.2f", lat)}°N, ${String.format("%.2f", lng)}°E",
                                            fontSize = 9.sp,
                                            color = SarthiMuted
                                        )
                                    }
                                    SarthiBadge(
                                        text = "${ob.alertLevel.uppercase()} ALERT",
                                        tone = tone
                                    )
                                }

                                Spacer(modifier = Modifier.height(8.dp))

                                Text(
                                    text = "Crops Affected: ${ob.cropsAffected.joinToString(", ").ifEmpty { "General crops" }}",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = SarthiText
                                )

                                Spacer(modifier = Modifier.height(6.dp))

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                                ) {
                                    Text("🐛 ${ob.pestCount} Pest Reports", fontSize = 10.sp, color = SarthiMuted)
                                    Text("🦠 ${ob.diseaseCount} Disease", fontSize = 10.sp, color = SarthiMuted)
                                    Text("📋 ${ob.totalReports} Incidents", fontSize = 10.sp, color = SarthiMuted)
                                }
                            }
                        }
                    }
                } else {
                    SarthiCard {
                        Text(
                            text = "Scanning regional telemetry for outbreak clusters...",
                            fontSize = 11.sp,
                            color = SarthiMuted,
                            textAlign = TextAlign.Center,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        )
                    }
                }
            }

            // ================= 2. VILLAGE TRUST LEADERBOARD =================
            Spacer(modifier = Modifier.height(10.dp))
            SarthiSectionTitle(title = "Village Trust Index & Leaderboard")
            SarthiCard {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(bottom = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("RANK", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1f))
                        Text("VILLAGE", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(2f))
                        Text("TRUST SCORE", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1.2f))
                        Text("RESPONSES", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1f), textAlign = TextAlign.End)
                    }

                    val board = leaderboard.ifEmpty {
                        listOf(
                            LeaderboardItem(1, "Rampur", 98.2, 142, "🥇"),
                            LeaderboardItem(2, "Bhimavaram", 95.7, 118, "🥈"),
                            LeaderboardItem(3, "Hanamkonda", 92.4, 89, "🥉"),
                            LeaderboardItem(4, "Kothapally", 88.6, 64, "⭐")
                        )
                    }

                    for (item in board) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 6.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("${item.tierIcon} #${item.rank}", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiText, modifier = Modifier.weight(1f))
                            Text(item.villageId, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiText, modifier = Modifier.weight(2f))
                            Text("${item.trustScore}%", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiGreen, modifier = Modifier.weight(1.2f))
                            Text("${item.totalResponses}", fontSize = 11.sp, color = SarthiMuted, modifier = Modifier.weight(1f), textAlign = TextAlign.End)
                        }
                    }
                }
            }
        }
    }
}
