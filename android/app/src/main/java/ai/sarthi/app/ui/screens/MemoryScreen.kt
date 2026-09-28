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
import androidx.compose.foundation.shape.CircleShape
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
import ai.sarthi.app.data.model.WhatChangedItem
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.components.ButtonKind
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiGreenDark
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

// ── Demo fallback data (shown when API returns empty) ─────────────────────────
private val DEMO_PAST_EXP = listOf(
    HindsightMemoryItem(
        text = "Kharif 2024: Tomato crop suffered 40% yield loss due to leaf curl viral outbreak and severe water deficit during flowering stage. Farmer lost ₹18,000 that season.",
        type = "CROP_HISTORY", source = "Farmer Query", crop = "Tomato"
    ),
    HindsightMemoryItem(
        text = "Kharif 2023: Soybean girdle beetle infestation at Day 38. Despite Profenophos spray, 15% pod loss recorded. Late detection cited as primary reason.",
        type = "PEST_OUTBREAK", source = "Community Report", crop = "Soybean"
    ),
    HindsightMemoryItem(
        text = "Rabi 2024: Groundnut fetched ₹5,480/quintal at Sehore APMC — ₹320 above MSP. Early harvest decision (Day 108) enabled moisture-safe storage and premium pricing.",
        type = "MARKET_OUTCOME", source = "Mandi Record", crop = "Groundnut"
    )
)

private val DEMO_LEARNED = listOf(
    HindsightMemoryItem(
        text = "Borewell motor output restricted to 1 hour/day during peak summer. Farmer must avoid flood-irrigation crops (Paddy, Sugarcane) during severe drought windows.",
        type = "CONSTRAINT", source = "Hindsight Retain", reason = "Water Table Drop"
    ),
    HindsightMemoryItem(
        text = "Soil test confirms high potassium (K=245 kg/ha) but low sulphur. Staged nitrogen in split doses preferred over basal overdose to prevent salt burn.",
        type = "SOIL_PROFILE", source = "Soil Health Card", reason = "Nutrient Optimization"
    ),
    HindsightMemoryItem(
        text = "Farmer prefers crops with <110 day duration for dual-season rotation. Avoids crops requiring more than 2 irrigations/week post-sowing.",
        type = "PREFERENCE", source = "Farmer Feedback", reason = "Market Timing"
    )
)

private val DEMO_WHAT_CHANGED = listOf(
    WhatChangedItem(
        trigger = "Water Stress Memory",
        summary = "Switched from Tomato → Black Gram (Urad)",
        impact = "Saved ₹22,000 in avoided crop loss. Black Gram yielded 6.2 qtl/acre with only 3 irrigations.",
        date = "Jul 2025"
    ),
    WhatChangedItem(
        trigger = "Pest History Recall",
        summary = "Added Girdle Beetle early-warning to Soybean advisory",
        impact = "Trichogramma release moved to Day 20 (from Day 45). Pest loss reduced from 15% to 2%.",
        date = "Jun 2025"
    ),
    WhatChangedItem(
        trigger = "Market Timing Learning",
        summary = "Moved Groundnut harvest 5 days earlier",
        impact = "Moisture-safe at 8% → premium APMC rate. Extra ₹4,200/acre vs. previous season.",
        date = "Nov 2024"
    )
)

@Composable
fun MemoryScreen(
    memorySummary: MemorySummaryResponse,
    onTeachMemory: () -> Unit,
    onResetDemo: () -> Unit,
    onBack: () -> Unit
) {
    var activeFilter by remember { mutableStateOf("All") }
    val filters = listOf("All", "Past Experience", "Learned From You", "What Changed")

    val pastExp = memorySummary.sections.pastExperience.ifEmpty { DEMO_PAST_EXP }
    val learned = memorySummary.sections.learnedFromYou.ifEmpty { DEMO_LEARNED }
    val whatChanged = memorySummary.whatChanged.ifEmpty { DEMO_WHAT_CHANGED }
    val totalMemories = if (memorySummary.memoryCount > 0) memorySummary.memoryCount
                        else pastExp.size + learned.size + whatChanged.size

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(title = "Farm Memories & Hindsight", onBack = onBack)

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            Text(
                text = "What Sarthi remembers",
                fontSize = 22.sp, fontWeight = FontWeight.ExtraBold,
                color = SarthiText, letterSpacing = (-0.5).sp
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text = "Hindsight Vectorize Memory Graph — personal farm context, crop loss history, and irrigation constraints retained to prevent repeated mistakes.",
                fontSize = 11.5.sp, color = SarthiMuted, lineHeight = 16.sp
            )

            Spacer(Modifier.height(16.dp))

            // ── Memory Stats Row ──────────────────────────────────────────
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                listOf(
                    Triple("brain", "$totalMemories", "MEMORIES"),
                    Triple("calendar", "3", "SEASONS"),
                    Triple("leaf", "₹44K+", "SAVINGS"),
                ).forEach { (icon, value, label) ->
                    SarthiCard(modifier = Modifier.weight(1f)) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            SarthiIcon(name = icon, size = 18.dp, tint = SarthiGreen)
                            Spacer(Modifier.height(4.dp))
                            Text(value, fontSize = 18.sp, fontWeight = FontWeight.ExtraBold, color = SarthiGreenDark)
                            Text(label, fontSize = 8.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, letterSpacing = 0.4.sp)
                        }
                    }
                }
            }

            Spacer(Modifier.height(16.dp))

            // ── Before / After Hindsight ──────────────────────────────────
            SarthiSectionTitle(title = "Hindsight Impact: Before vs After")
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                // Without memory
                SarthiCard(
                    modifier = Modifier.weight(1f),
                    borderColor = Color(0xFFF5C6C6),
                    backgroundColor = Color(0xFFFFF8F8)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("WITHOUT MEMORY", fontSize = 8.sp, fontWeight = FontWeight.ExtraBold,
                            color = Color(0xFFC94F4F), letterSpacing = 0.5.sp)
                        Spacer(Modifier.height(4.dp))
                        Text(
                            "Generic Tomato recommended. Ignores 1-hr borewell limit & leaf curl history. ₹18,000 lost.",
                            fontSize = 10.5.sp, lineHeight = 15.sp, color = Color(0xFF7A3C3C)
                        )
                    }
                }
                // With Hindsight
                SarthiCard(
                    modifier = Modifier.weight(1f),
                    borderColor = Color(0xFFB8E2CD),
                    backgroundColor = Color(0xFFF0F8F3)
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text("WITH HINDSIGHT", fontSize = 8.sp, fontWeight = FontWeight.ExtraBold,
                            color = SarthiGreen, letterSpacing = 0.5.sp)
                        Spacer(Modifier.height(4.dp))
                        Text(
                            "Recalled borewell + pest memory. Recommended Black Gram. ₹22,000 saved.",
                            fontSize = 10.5.sp, lineHeight = 15.sp, color = SarthiGreenDark,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            Spacer(Modifier.height(16.dp))

            // ── Filter Pills ──────────────────────────────────────────────
            Row(
                modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
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
                        Text(cat, fontSize = 11.sp, fontWeight = FontWeight.Bold,
                            color = if (isSelected) Color.White else SarthiMuted)
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            // ── Memory Cards ──────────────────────────────────────────────
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                if (activeFilter == "All" || activeFilter == "Past Experience") {
                    pastExp.forEach { item ->
                        MemoryItemCard(
                            icon = "leaf", badgeText = item.type.uppercase(),
                            badgeTone = BadgeTone.Amber, statusText = "Hindsight Retained",
                            text = item.text,
                            meta = "Source: ${item.source}${if (item.crop != null) " · Crop: ${item.crop}" else ""}"
                        )
                    }
                }
                if (activeFilter == "All" || activeFilter == "Learned From You") {
                    learned.forEach { item ->
                        MemoryItemCard(
                            icon = "brain", badgeText = item.type.uppercase(),
                            badgeTone = BadgeTone.Green, statusText = "Learned Constraint",
                            text = item.text,
                            meta = "Source: ${item.source}${if (item.reason != null) " · Reason: ${item.reason}" else ""}"
                        )
                    }
                }
            }

            // ── Memory Evolution Timeline ─────────────────────────────────
            if (activeFilter == "All" || activeFilter == "What Changed") {
                Spacer(Modifier.height(16.dp))
                SarthiSectionTitle(title = "Memory Evolution Timeline")
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    whatChanged.forEachIndexed { idx, wc ->
                        Row(verticalAlignment = Alignment.Top) {
                            // Timeline dot + line
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Box(
                                    modifier = Modifier
                                        .size(12.dp)
                                        .clip(CircleShape)
                                        .background(SarthiGreen)
                                )
                                if (idx < whatChanged.size - 1) {
                                    Box(
                                        modifier = Modifier
                                            .width(2.dp)
                                            .height(80.dp)
                                            .background(SarthiLine)
                                    )
                                }
                            }
                            Spacer(Modifier.width(12.dp))
                            SarthiCard(modifier = Modifier.weight(1f)) {
                                Column(modifier = Modifier.padding(12.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        SarthiBadge(text = wc.trigger, tone = BadgeTone.Green)
                                        if (wc.date.isNotEmpty()) {
                                            Text(wc.date, fontSize = 9.sp, color = SarthiMuted,
                                                fontWeight = FontWeight.SemiBold)
                                        }
                                    }
                                    Spacer(Modifier.height(4.dp))
                                    Text(wc.summary, fontSize = 12.sp, fontWeight = FontWeight.Bold,
                                        color = SarthiText, lineHeight = 16.sp)
                                    Spacer(Modifier.height(4.dp))
                                    Text("✓ ${wc.impact}", fontSize = 10.sp, color = SarthiGreen,
                                        lineHeight = 14.sp)
                                }
                            }
                        }
                    }
                }
            }

            Spacer(Modifier.height(20.dp))

            // ── Bottom Buttons ────────────────────────────────────────────
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                SarthiButton(text = "Teach Sarthi", icon = "plus", onClick = onTeachMemory,
                    modifier = Modifier.weight(1f))
                SarthiButton(text = "Reset Demo", icon = "refresh", kind = ButtonKind.Soft,
                    onClick = onResetDemo, modifier = Modifier.weight(1f))
            }
        }
    }
}

// ── Shared memory card composable ─────────────────────────────────────────────
@Composable
fun MemoryItemCard(
    icon: String, badgeText: String, badgeTone: BadgeTone,
    statusText: String, text: String, meta: String
) {
    SarthiCard {
        Row(modifier = Modifier.fillMaxWidth().padding(14.dp)) {
            Box(
                modifier = Modifier.size(38.dp).background(SarthiMint, RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                SarthiIcon(name = icon, size = 18.dp, tint = SarthiGreen)
            }
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    SarthiBadge(text = badgeText, tone = badgeTone)
                    Text(statusText, fontSize = 9.sp, fontWeight = FontWeight.ExtraBold, color = SarthiGreen)
                }
                Spacer(Modifier.height(6.dp))
                Text(text, fontSize = 11.5.sp, color = SarthiText, lineHeight = 16.sp)
                Spacer(Modifier.height(6.dp))
                Text(meta, fontSize = 9.sp, color = SarthiMuted)
            }
        }
    }
}
