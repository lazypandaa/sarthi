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
import androidx.compose.runtime.mutableStateMapOf
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
import ai.sarthi.app.data.model.CropCalendarItem
import ai.sarthi.app.data.model.CropCalendarStage
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun CropCalendarScreen(
    onBack: () -> Unit
) {
    val sampleCrops = listOf(
        CropCalendarItem(
            name = "Black Gram (Urad)",
            season = "Kharif",
            sowingWindow = "June 15 – July 10",
            harvestingWindow = "September 15 – October 5",
            durationDays = 85,
            criticalOperations = listOf(
                CropCalendarStage("Deep Summer Ploughing", "May 25 – June 10", "Expose soil to solar heat to eradicate pupae of pod borers and nematodes."),
                CropCalendarStage("Seed Treatment & Sowing", "June 15 – June 25", "Treat seeds with Rhizobium and Trichoderma viride @ 5g/kg before sowing."),
                CropCalendarStage("Pre-emergence Weed Control", "Day 3 – Day 5", "Apply Pendimethalin @ 1.0 kg a.i./ha within 48 hours of sowing under moist soil."),
                CropCalendarStage("Flowering & Moisture Check", "Day 35 – Day 45", "Critical moisture phase. Provide 1 life-saving irrigation if rain ceases."),
                CropCalendarStage("Pod Filling & Harvesting", "Day 75 – Day 85", "Harvest when 80% pods turn blackish brown to avoid field shattering.")
            )
        ),
        CropCalendarItem(
            name = "Groundnut",
            season = "Kharif",
            sowingWindow = "June 20 – July 15",
            harvestingWindow = "October 10 – November 5",
            durationDays = 110,
            criticalOperations = listOf(
                CropCalendarStage("Land Prep & Gypsum", "June 10 – June 20", "Apply gypsum @ 200 kg/ha in two splits: 50% basal and 50% at pegging."),
                CropCalendarStage("Sowing & Seed Inoculation", "June 20 – July 5", "Inoculate with Bradyrhizobium. Maintain 30x10 cm row spacing."),
                CropCalendarStage("Pegging Stage Moisture", "Day 40 – Day 55", "Ensure loose, moist soil for unhindered peg entry into ground.")
            )
        )
    )

    var selectedIndex by remember { mutableStateOf(0) }
    val selectedCrop = sampleCrops[selectedIndex]
    val completedOps = remember { mutableStateMapOf<String, Boolean>() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Crop Operations Calendar",
            onBack = onBack
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            Text(
                text = "Kharif & Rabi Timelines",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Tailored agronomy schedule, sowing window, and critical intercultural operations.",
                fontSize = 11.5.sp,
                color = SarthiMuted
            )

            Spacer(modifier = Modifier.height(14.dp))

            // Crop selector pills
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                sampleCrops.forEachIndexed { idx, crop ->
                    val isSelected = selectedIndex == idx
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(100.dp))
                            .background(if (isSelected) SarthiGreen else SarthiSurface)
                            .border(1.dp, if (isSelected) SarthiGreen else SarthiLine, RoundedCornerShape(100.dp))
                            .clickable { selectedIndex = idx }
                            .padding(horizontal = 16.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = crop.name,
                            fontSize = 11.5.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected) Color.White else SarthiMuted
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Crop Overview Card
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = selectedCrop.name,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = SarthiText
                        )
                        SarthiBadge(text = selectedCrop.season, tone = BadgeTone.Green)
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("SOWING WINDOW", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(selectedCrop.sowingWindow, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("HARVESTING", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(selectedCrop.harvestingWindow, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                    }
                }
            }

            // Operations List
            SarthiSectionTitle(title = "Critical Farm Operations (${selectedCrop.criticalOperations.size} stages)")
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                selectedCrop.criticalOperations.forEach { op ->
                    val isDone = completedOps[op.stage] == true

                    SarthiCard(
                        onClick = { completedOps[op.stage] = !isDone }
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(14.dp),
                            verticalAlignment = Alignment.Top
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(24.dp)
                                    .clip(CircleShape)
                                    .background(if (isDone) SarthiGreen else SarthiMint)
                                    .clickable { completedOps[op.stage] = !isDone },
                                contentAlignment = Alignment.Center
                            ) {
                                if (isDone) {
                                    SarthiIcon(name = "check", size = 14.dp, tint = Color.White)
                                }
                            }

                            Spacer(modifier = Modifier.width(12.dp))

                            Column(modifier = Modifier.weight(1f)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(
                                        text = op.stage,
                                        fontSize = 12.5.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isDone) SarthiMuted else SarthiText
                                    )
                                    Text(
                                        text = op.timing,
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = SarthiGreen
                                    )
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = op.advisory,
                                    fontSize = 10.5.sp,
                                    color = SarthiMuted,
                                    lineHeight = 14.sp
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
