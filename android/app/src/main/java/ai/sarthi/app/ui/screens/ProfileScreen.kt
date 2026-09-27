package ai.sarthi.app.ui.screens

import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.data.model.EnvironmentalProfile
import ai.sarthi.app.data.model.QueryHistoryItem
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.ButtonKind
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiIconButton
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun ProfileScreen(
    user: UserProfile,
    envProfile: EnvironmentalProfile,
    memoriesCount: Int,
    queryHistory: List<QueryHistoryItem>,
    onLogout: () -> Unit,
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
            title = "Farmer Profile",
            onNotificationClick = { onNavigate("notifications") }
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            // Profile Card
            SarthiCard {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(54.dp)
                            .clip(CircleShape)
                            .background(SarthiMint),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "FM",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = SarthiGreen
                        )
                    }
                    Spacer(modifier = Modifier.width(14.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = user.phoneNumber,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = SarthiText
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            SarthiIcon(name = "pin", size = 13.dp, tint = SarthiMuted)
                            Spacer(modifier = Modifier.width(3.dp))
                            Text(
                                text = user.location,
                                fontSize = 11.5.sp,
                                color = SarthiMuted
                            )
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            SarthiBadge(text = "Verified Account", tone = BadgeTone.Green)
                            SarthiBadge(text = envProfile.soilType, tone = BadgeTone.Neutral)
                        }
                    }

                    SarthiIconButton(icon = "spark", onClick = { onNavigate("ai") })
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Stats row (3 cards)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                ProfileStatCard(
                    value = "${envProfile.nitrogen}",
                    label = "Soil N (kg/ha)",
                    modifier = Modifier.weight(1f)
                )
                ProfileStatCard(
                    value = "$memoriesCount",
                    label = "Memories",
                    modifier = Modifier.weight(1f),
                    onClick = { onNavigate("memory") }
                )
                ProfileStatCard(
                    value = "${envProfile.soilPh}",
                    label = "Soil pH",
                    modifier = Modifier.weight(1f),
                    onClick = { onNavigate("calendar") }
                )
            }

            // My Farm Details & Telemetry
            SarthiSectionTitle(title = "My Farm Details & Telemetry")
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("SOIL TYPE:", fontSize = 9.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(envProfile.soilType, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("NORMAL RAINFALL:", fontSize = 9.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(envProfile.rainfall, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("PHOSPHORUS (P):", fontSize = 9.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text("${envProfile.phosphorus} kg/ha", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("POTASSIUM (K):", fontSize = 9.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text("${envProfile.potassium} kg/ha", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(SarthiMint, RoundedCornerShape(8.dp))
                            .padding(10.dp)
                    ) {
                        Column {
                            Text(
                                text = "SOIL AMENDMENT NOTE:",
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                color = SarthiGreen
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = envProfile.recommendedAmendments,
                                fontSize = 10.5.sp,
                                color = SarthiText,
                                lineHeight = 14.sp
                            )
                        }
                    }
                }
            }

            // Query History
            SarthiSectionTitle(title = "Your Sarthi Query History")
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                val queries = queryHistory.ifEmpty {
                    listOf(
                        QueryHistoryItem("q1", "What crop should I grow with my 1 hour borewell limit?", "Black Gram or Groundnut is recommended. Replaces water-heavy paddy to guarantee crop yield.", "Today"),
                        QueryHistoryItem("q2", "How to manage leaf curl in chilli?", "Spray neem oil @ 3ml/L water and yellow sticky traps for whitefly management.", "Yesterday")
                    )
                }

                for (q in queries) {
                    SarthiCard {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "“${q.query}”",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = SarthiText,
                                    modifier = Modifier.weight(1f)
                                )
                                Text(
                                    text = q.timestamp ?: "Recent",
                                    fontSize = 9.sp,
                                    color = SarthiMuted
                                )
                            }
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = q.response,
                                fontSize = 11.sp,
                                color = SarthiMuted,
                                lineHeight = 15.sp
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                SarthiButton(
                    text = "Sign out (${user.phoneNumber})",
                    kind = ButtonKind.Ghost,
                    onClick = onLogout
                )
            }
        }
    }
}

@Composable
fun ProfileStatCard(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null
) {
    SarthiCard(
        modifier = modifier,
        onClick = onClick
    ) {
        Column(
            modifier = Modifier.padding(vertical = 12.dp, horizontal = 8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = value, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = SarthiText)
            Spacer(modifier = Modifier.height(2.dp))
            Text(text = label, fontSize = 9.sp, color = SarthiMuted, textAlign = TextAlign.Center)
        }
    }
}
