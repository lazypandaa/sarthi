package ai.sarthi.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import ai.sarthi.app.data.model.HindsightMemoryItem
import ai.sarthi.app.data.model.MemorySummaryResponse
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.ButtonKind
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun MemoryScreen(
    memorySummary: MemorySummaryResponse,
    onTeachMemory: () -> Unit,
    onResetDemo: () -> Unit,
    onBack: () -> Unit
) {
    var activeFilter by remember { mutableStateOf("All") }
    val filters = listOf("All", "Past Experience", "Learned From You", "Constraints", "What Changed")

    val pastExp = memorySummary.sections.pastExperience.ifEmpty {
        listOf(
            HindsightMemoryItem(
                text = "Previous Kharif crop of Tomato suffered 40% yield loss due to leaf curl viral outbreak and severe water deficit in flowering stage.",
                type = "CROP_HISTORY",
                source = "Farmer Query",
                crop = "Tomato"
            )
        )
    }

    val learned = memorySummary.sections.learnedFromYou.ifEmpty {
        listOf(
            HindsightMemoryItem(
                text = "Borewell motor output is restricted to 1 hour daily during peak summer / dry spells. Farmer strictly avoids flood irrigation crops.",
                type = "CONSTRAINT",
                source = "Hindsight Retain",
                reason = "Water Table Drop"
            ),
            HindsightMemoryItem(
                text = "Soil analysis confirms high potassium reserve; nitrogen fertilization should be staged in split doses rather than basal overdose.",
                type = "SOIL_PROFILE",
                source = "Soil Health Card",
                reason = "Nutrient Optimization"
            )
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Farm Memories & Hindsight",
            onBack = onBack
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            // Intro
            Text(
                text = "What Sarthi remembers",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Hindsight Vectorize Memory Graph. Personal farm context, prior crop losses, and irrigation constraints retained to prevent repeated mistakes.",
                fontSize = 11.5.sp,
                color = SarthiMuted,
                lineHeight = 16.sp
            )

            Spacer(modifier = Modifier.height(14.dp))

            // Filter row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                for (cat in filters) {
                    val isSelected = activeFilter == cat
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(100.dp))
                            .background(if (isSelected) SarthiGreen else SarthiSurface)
                            .border(1.dp, if (isSelected) SarthiGreen else SarthiLine, RoundedCornerShape(100.dp))
                            .clickable { activeFilter = cat }
                            .padding(horizontal = 14.dp, vertical = 7.dp)
                    ) {
                        Text(
                            text = cat,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected) Color.White else SarthiMuted
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Memory cards
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                if (activeFilter == "All" || activeFilter == "Past Experience") {
                    for (item in pastExp) {
                        MemoryItemCard(
                            icon = "leaf",
                            badgeText = item.type.uppercase(),
                            badgeTone = BadgeTone.Amber,
                            statusText = "Hindsight Retained",
                            text = item.text,
                            meta = "Source: ${item.source} ${if (item.crop != null) "· Crop: ${item.crop}" else ""}"
                        )
                    }
                }

                if (activeFilter == "All" || activeFilter == "Learned From You" || activeFilter == "Constraints") {
                    for (item in learned) {
                        MemoryItemCard(
                            icon = "brain",
                            badgeText = item.type.uppercase(),
                            badgeTone = BadgeTone.Green,
                            statusText = "Learned Constraint",
                            text = item.text,
                            meta = "Source: ${item.source} ${if (item.reason != null) "· Reason: ${item.reason}" else ""}"
                        )
                    }
                }

                if (activeFilter == "What Changed") {
                    for (wc in memorySummary.whatChanged) {
                        SarthiCard {
                            Row(modifier = Modifier.padding(14.dp)) {
                                Box(
                                    modifier = Modifier
                                        .size(36.dp)
                                        .background(SarthiMint, RoundedCornerShape(10.dp)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    SarthiIcon(name = "spark", size = 18.dp, tint = SarthiGreen)
                                }
                                Spacer(modifier = Modifier.width(12.dp))
                                Column {
                                    SarthiBadge(text = wc.trigger, tone = BadgeTone.Green)
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = wc.summary,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = SarthiText
                                    )
                                    Text(
                                        text = "Impact: ${wc.impact}",
                                        fontSize = 10.sp,
                                        color = SarthiGreen
                                    )
                                }
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Bottom Buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                SarthiButton(
                    text = "Teach Sarthi",
                    icon = "plus",
                    onClick = onTeachMemory,
                    modifier = Modifier.weight(1f)
                )
                SarthiButton(
                    text = "Reset Demo",
                    icon = "refresh",
                    kind = ButtonKind.Soft,
                    onClick = onResetDemo,
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
fun MemoryItemCard(
    icon: String,
    badgeText: String,
    badgeTone: BadgeTone,
    statusText: String,
    text: String,
    meta: String
) {
    SarthiCard {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(38.dp)
                    .background(SarthiMint, RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                SarthiIcon(name = icon, size = 18.dp, tint = SarthiGreen)
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    SarthiBadge(text = badgeText, tone = badgeTone)
                    Text(
                        text = statusText,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = SarthiGreen
                    )
                }
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = text,
                    fontSize = 11.5.sp,
                    color = SarthiText,
                    lineHeight = 16.sp
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = meta,
                    fontSize = 9.sp,
                    color = SarthiMuted
                )
            }
        }
    }
}
