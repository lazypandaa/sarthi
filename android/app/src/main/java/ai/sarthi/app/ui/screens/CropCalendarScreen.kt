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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
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
import ai.sarthi.app.ui.theme.SarthiGreenDark
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

// Curated free-use crop photos (Unsplash – no API key needed)
private val cropImageUrls = mapOf(
    "Chilli"                  to "https://images.unsplash.com/photo-1588168333986-5078d3ae3976?w=600&q=80&fit=crop",
    "Cotton"                  to "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=600&q=80&fit=crop",
    "Groundnut"               to "https://images.unsplash.com/photo-1567356738706-4ca9f5929cba?w=600&q=80&fit=crop",
    "Paddy (Rice - Kharif)"   to "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=600&q=80&fit=crop",
    "Paddy"                   to "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=600&q=80&fit=crop",
    "Rice"                    to "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=600&q=80&fit=crop",
    "Soybean"                 to "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=600&q=80&fit=crop",
    "Sugarcane"               to "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&q=80&fit=crop",
    "Black Gram (Urad)"       to "https://images.unsplash.com/photo-1612257416648-3c3e3c1a8b35?w=600&q=80&fit=crop",
    "Wheat"                   to "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80&fit=crop",
)
private const val DEFAULT_CROP_IMAGE = "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=600&q=80&fit=crop"

private fun getCropImageUrl(name: String): String {
    cropImageUrls[name]?.let { return it }
    // Partial match
    cropImageUrls.entries.firstOrNull { name.contains(it.key, ignoreCase = true) }?.let { return it.value }
    return DEFAULT_CROP_IMAGE
}

@Composable
fun CropCalendarScreen(
    onBack: () -> Unit
) {
    val sampleCrops = listOf(
        CropCalendarItem(
            name = "Chilli",
            season = "Kharif",
            sowingWindow = "June 15 – July 5",
            harvestingWindow = "October 20 – December 10",
            durationDays = 150,
            criticalOperations = listOf(
                CropCalendarStage("Nursery Preparation", "May 25 – June 10", "Prepare raised beds of 3m x 1m. Apply 25g Trichoderma viride per bed and pre-soak seeds for 8 hrs."),
                CropCalendarStage("Transplanting", "June 15 – July 5", "Transplant 25-30 day old seedlings at 60×45 cm spacing. Water immediately after planting."),
                CropCalendarStage("Fertigation Stage 1", "Day 20 – Day 30", "Apply 19:19:19 NPK @ 3 kg/acre via drip. Avoid overhead irrigation to reduce Phytophthora risk."),
                CropCalendarStage("Thrips & Mite Watch", "Day 45 – Day 60", "Spray Spinosad 45SC @ 0.3 ml/L. Yellow sticky traps @ 5/acre for early detection."),
                CropCalendarStage("Fruit Set to First Pick", "Day 80 – Day 120", "Harvest at red ripening stage. Allow 70% pods to redden before commencing main harvest.")
            )
        ),
        CropCalendarItem(
            name = "Cotton",
            season = "Kharif",
            sowingWindow = "May 15 – June 15",
            harvestingWindow = "October 15 – January 10",
            durationDays = 180,
            criticalOperations = listOf(
                CropCalendarStage("Deep Ploughing & FYM", "April 25 – May 10", "Deep plough 25–30 cm. Add 10 tonnes FYM/ha. Border planting of maize as trap crop for bollworm."),
                CropCalendarStage("Sowing (BT Hybrid)", "May 15 – June 5", "Use BT hybrid seed 0.75 kg/acre. Maintain 90x60 cm spacing. Apply imidacloprid 600 FS seed treatment."),
                CropCalendarStage("Square Formation", "Day 40 – Day 55", "Apply NPK 2:1:2 ratio. Spray Monocrotophos for jassids if threshold exceeded (1 nymph/leaf)."),
                CropCalendarStage("Boll Development", "Day 75 – Day 100", "Supplement with foliar KNO3 @ 1% to improve boll filling. Check for Pink Bollworm pheromone traps."),
                CropCalendarStage("Picking", "Day 120 – Day 180", "Pick mature opened bolls. Avoid mixing contaminated and clean cotton. Sun dry to 8% moisture.")
            )
        ),
        CropCalendarItem(
            name = "Groundnut",
            season = "Kharif",
            sowingWindow = "June 20 – July 15",
            harvestingWindow = "October 10 – November 5",
            durationDays = 110,
            criticalOperations = listOf(
                CropCalendarStage("Land Prep & Gypsum", "June 10 – June 20", "Apply gypsum @ 200 kg/ha in two splits: 50% basal and 50% at pegging stage."),
                CropCalendarStage("Sowing & Seed Inoculation", "June 20 – July 5", "Inoculate with Bradyrhizobium. Maintain 30×10 cm row spacing. 100 kg seed/ha."),
                CropCalendarStage("Pegging Stage Moisture", "Day 40 – Day 55", "Ensure loose, moist soil for unhindered peg entry. Avoid water logging."),
                CropCalendarStage("Tikka Disease Check", "Day 50 – Day 70", "Spray Mancozeb @ 2.5 g/L if early leaf spot (Tikka) observed. Repeat after 10 days."),
                CropCalendarStage("Harvesting & Drying", "Day 100 – Day 115", "Harvest when 70% pods show dark inner shell. Dry windrow in field for 3–4 days before threshing.")
            )
        ),
        CropCalendarItem(
            name = "Paddy (Rice - Kharif)",
            season = "Kharif",
            sowingWindow = "June 15 – July 10",
            harvestingWindow = "October 20 – November 20",
            durationDays = 130,
            criticalOperations = listOf(
                CropCalendarStage("Nursery Raising", "June 1 – June 15", "Sow pre-germinated seeds @ 50g/m² in puddle nursery. Apply Carbofuran @ 1 kg a.i./ha to control stem borer."),
                CropCalendarStage("Transplanting", "June 20 – July 10", "Transplant 21–25 day old seedlings at 20×15 cm spacing. Avoid deep water stagnation > 15 cm."),
                CropCalendarStage("Tillering Fertilizer", "Day 20 – Day 30", "Apply 40 kg N/ha (Urea @ 87 kg/ha) in two split doses at tillering and panicle initiation."),
                CropCalendarStage("Brown Plant Hopper (BPH) Watch", "Day 50 – Day 70", "Monitor with light traps. Spray Buprofezin if >5 BPH/hill. Drain water before spraying."),
                CropCalendarStage("Harvest at Physiological Maturity", "Day 120 – Day 135", "Harvest when 80% grains are straw-colored. Moisture should be 20–22% at cutting stage.")
            )
        ),
        CropCalendarItem(
            name = "Soybean",
            season = "Kharif",
            sowingWindow = "June 20 – July 5",
            harvestingWindow = "September 25 – October 20",
            durationDays = 100,
            criticalOperations = listOf(
                CropCalendarStage("Seed Treatment", "June 15 – June 20", "Treat with Thiram + Carbendazim (2:1) @ 3g/kg. Inoculate with Bradyrhizobium japonicum."),
                CropCalendarStage("Sowing", "June 20 – July 5", "Sow at 45×5 cm spacing. Seed rate 65–70 kg/ha. Apply Pendimethalin pre-emergence @ 1 kg a.i./ha."),
                CropCalendarStage("Vegetative Growth Irrigation", "Day 30 – Day 40", "Irrigate once if rainfall gap >15 days. Apply 40 kg K₂O/ha for stem strength."),
                CropCalendarStage("Pod Fill & Pest Watch", "Day 55 – Day 75", "Monitor girdle beetle and stem fly. Spray Profenophos @ 2 ml/L at economic threshold."),
                CropCalendarStage("Harvest & Threshing", "Day 90 – Day 105", "Harvest when 95% pods turn yellow-brown. Thresh within 3 days to avoid shattering losses.")
            )
        ),
        CropCalendarItem(
            name = "Sugarcane",
            season = "Kharif",
            sowingWindow = "February 15 – March 30",
            harvestingWindow = "November 1 – March 30",
            durationDays = 365,
            criticalOperations = listOf(
                CropCalendarStage("Sett Treatment & Planting", "Feb 15 – Mar 30", "Treat setts with Carbendazim 50 WP @ 1g/L for 10 min. Plant at 90 cm row spacing, 3 bud setts."),
                CropCalendarStage("Gap Filling & Earthing Up", "Day 30 – Day 45", "Fill gaps within 30 days of planting. First earthing up at 45 days with 40 kg N/ha."),
                CropCalendarStage("Interculture & Borer Control", "Day 60 – Day 90", "Apply Chlorpyriphos granules @ 4 kg a.i./ha to control shoot borer. Release Trichogramma 50,000/ha."),
                CropCalendarStage("Grand Growth Phase", "Day 120 – Day 270", "Irrigate every 10–12 days. Stop nitrogen application 90 days before harvest to improve sucrose %."),
                CropCalendarStage("Harvest (Maturity Test)", "Day 330 – Day 365", "Harvest when Brix > 18% and Pol % > 15%. Cut at ground level. Crush within 24 hours.")
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
                text = "KHARIF 2026 CALENDAR",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Synchronized with ICAR agronomy cycles and Sehore, Madhya Pradesh agro-climatic norms.",
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

            // ── Crop Hero Image Card ────────────────────────────────────────
            SarthiCard(shape = RoundedCornerShape(20.dp)) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                ) {
                    // Crop photo
                    AsyncImage(
                        model = getCropImageUrl(selectedCrop.name),
                        contentDescription = selectedCrop.name,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.fillMaxSize()
                    )
                    // Dark green gradient overlay at bottom
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(
                                Brush.verticalGradient(
                                    colors = listOf(
                                        Color.Transparent,
                                        Color(0xCC075238)
                                    ),
                                    startY = 60f
                                )
                            )
                    )
                    // Crop name + season on overlay
                    Column(
                        modifier = Modifier
                            .align(Alignment.BottomStart)
                            .padding(14.dp)
                    ) {
                        Text(
                            text = selectedCrop.name,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = Color.White,
                            lineHeight = 24.sp
                        )
                        Text(
                            text = "${selectedCrop.durationDays} Days · ${selectedCrop.season} Season",
                            fontSize = 10.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xCCFFFFFF)
                        )
                    }
                    // Duration badge top-right
                    SarthiBadge(
                        text = "${selectedCrop.durationDays} Days",
                        tone = BadgeTone.Green,
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .padding(10.dp)
                    )
                }

                // Planting & Harvest info below photo
                Column(modifier = Modifier.padding(horizontal = 14.dp, vertical = 12.dp)) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("SOWING WINDOW", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp)
                            Text(selectedCrop.sowingWindow, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("HARVESTING", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp)
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
                                        color = if (isDone) SarthiMuted else SarthiText,
                                        modifier = Modifier.weight(1f)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
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

            Spacer(modifier = Modifier.height(16.dp))
        }
    }
}
