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
import androidx.compose.material3.Surface
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
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import ai.sarthi.app.data.model.AgriNewsItem
import ai.sarthi.app.data.model.CropRecommendationItem
import ai.sarthi.app.data.model.MarketItem
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun AdviceScreen(
    cropRecs: List<CropRecommendationItem>,
    markets: List<MarketItem>,
    agriNews: List<AgriNewsItem>,
    onSelectCrop: (CropRecommendationItem) -> Unit,
    onNavigate: (String) -> Unit
) {
    var activeFilter by remember { mutableStateOf("All") }
    val filters = listOf("All", "Mandi prices", "Crops", "Weather alerts", "Govt schemes")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Farm Advisory & Mandi",
            onNotificationClick = { onNavigate("notifications") }
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            // Intro
            Text(
                text = "फार्म सलाहकार एवं मंडी भाव",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Expert agronomic guidance, live Agmarknet mandi prices, and government schemes.",
                fontSize = 11.5.sp,
                color = SarthiMuted,
                lineHeight = 16.sp
            )

            Spacer(modifier = Modifier.height(14.dp))

            // Filter horizontal row
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

            // ================= 1. LIVE MANDI PRICES TABLE =================
            if (activeFilter == "All" || activeFilter == "Mandi prices") {
                Spacer(modifier = Modifier.height(8.dp))
                SarthiSectionTitle(title = "Live Mandi Market Prices (Agmarknet)")
                SarthiCard {
                    Column(modifier = Modifier.padding(12.dp)) {
                        // Header row
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 8.dp),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("COMMODITY", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1.4f))
                            Text("MODAL", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1f))
                            Text("RANGE", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1f))
                            Text("MARKET", fontSize = 9.sp, fontWeight = FontWeight.Bold, color = SarthiMuted, modifier = Modifier.weight(1.1f), textAlign = TextAlign.End)
                        }

                        if (markets.isNotEmpty()) {
                            for (item in markets) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 6.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Column(modifier = Modifier.weight(1.4f)) {
                                        Text(item.commodity, fontSize = 11.5.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                                        Text(item.variety ?: "Standard", fontSize = 8.5.sp, color = SarthiMuted)
                                    }
                                    Column(modifier = Modifier.weight(1f)) {
                                        Text("₹${item.modalPrice.toInt()}", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                                        Text("/ q", fontSize = 8.5.sp, color = SarthiMuted)
                                    }
                                    Text(
                                        "₹${item.minPrice.toInt()}-₹${item.maxPrice.toInt()}",
                                        fontSize = 9.sp,
                                        color = SarthiMuted,
                                        modifier = Modifier.weight(1f)
                                    )
                                    Box(modifier = Modifier.weight(1.1f), contentAlignment = Alignment.CenterEnd) {
                                        SarthiBadge(text = item.market, tone = BadgeTone.Neutral)
                                    }
                                }
                            }
                        } else {
                            Text(
                                text = "Connecting to state mandi feed...",
                                fontSize = 11.sp,
                                color = SarthiMuted,
                                textAlign = TextAlign.Center,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 16.dp)
                            )
                        }

                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "Source: Directorate of Marketing & Inspection (agmarknet.gov.in)",
                            fontSize = 8.5.sp,
                            color = SarthiMuted,
                            textAlign = TextAlign.End,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            }

            // ================= 2. ICAR CROPS RECOMMENDATION =================
            if (activeFilter == "All" || activeFilter == "Crops") {
                Spacer(modifier = Modifier.height(8.dp))
                SarthiSectionTitle(
                    title = "Recommended Crops for Your Soil & Season",
                    action = "${cropRecs.size} crops"
                )
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    for (crop in cropRecs) {
                        val thumb = when {
                            crop.cropName.contains("wheat", ignoreCase = true) -> "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop"
                            crop.cropName.contains("rice", ignoreCase = true) || crop.cropName.contains("paddy", ignoreCase = true) -> "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=300&h=200&fit=crop"
                            crop.cropName.contains("soybean", ignoreCase = true) -> "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?w=300&h=200&fit=crop"
                            crop.cropName.contains("gram", ignoreCase = true) -> "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=300&h=200&fit=crop"
                            crop.cropName.contains("onion", ignoreCase = true) -> "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=300&h=200&fit=crop"
                            crop.cropName.contains("cotton", ignoreCase = true) -> "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=300&h=200&fit=crop"
                            else -> "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=300&h=200&fit=crop"
                        }

                        SarthiCard(
                            onClick = { onSelectCrop(crop) }
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    AsyncImage(
                                        model = thumb,
                                        contentDescription = crop.cropName,
                                        modifier = Modifier
                                            .size(56.dp)
                                            .clip(RoundedCornerShape(10.dp)),
                                        contentScale = ContentScale.Crop
                                    )
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Column(modifier = Modifier.weight(1f)) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Text(
                                                text = crop.cropName,
                                                fontSize = 13.5.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = SarthiText
                                            )
                                            SarthiBadge(
                                                text = "${crop.soilCompatibility.toInt()}% Fit",
                                                tone = BadgeTone.Green
                                            )
                                        }
                                        Text(
                                            text = "${crop.scientificName ?: ""} · ${crop.category}",
                                            fontSize = 9.5.sp,
                                            color = SarthiMuted
                                        )
                                        Spacer(modifier = Modifier.height(2.dp))
                                        Text(
                                            text = crop.explanation,
                                            fontSize = 10.5.sp,
                                            color = SarthiMuted,
                                            lineHeight = 14.sp,
                                            maxLines = 2
                                        )
                                    }
                                }

                                Spacer(modifier = Modifier.height(8.dp))
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text("⏳ ${crop.durationDays} days", fontSize = 9.5.sp, color = SarthiMuted)
                                    Spacer(modifier = Modifier.width(10.dp))
                                    Text("💧 ${crop.waterRequirement}", fontSize = 9.5.sp, color = SarthiMuted)
                                    Spacer(modifier = Modifier.weight(1f))
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text(
                                            text = "Package of Practices",
                                            fontSize = 9.5.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = SarthiGreen
                                        )
                                        Spacer(modifier = Modifier.width(2.dp))
                                        SarthiIcon(name = "arrow", size = 11.dp, tint = SarthiGreen)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // ================= 3. OFFICIAL ADVISORIES & SCHEMES WITH PHOTOS =================
            if (activeFilter == "All" || activeFilter == "Weather alerts" || activeFilter == "Govt schemes") {
                val filteredAdvisories = agriNews.filter { item ->
                    when (activeFilter) {
                        "Weather alerts" -> item.category == "weather_warning" || item.category == "pest_alert"
                        "Govt schemes" -> item.category == "government_scheme"
                        else -> true
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))
                SarthiSectionTitle(
                    title = "Official Advisories & Schemes",
                    action = "${filteredAdvisories.size} updates"
                )

                Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    for (item in filteredAdvisories) {
                        val photo = item.image ?: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=700&h=350&fit=crop"
                        val tone = when (item.category) {
                            "weather_warning" -> BadgeTone.Amber
                            "pest_alert" -> BadgeTone.Danger
                            else -> BadgeTone.Green
                        }

                        SarthiCard {
                            Column {
                                Box(modifier = Modifier.fillMaxWidth().height(155.dp)) {
                                    AsyncImage(
                                        model = photo,
                                        contentDescription = item.title,
                                        modifier = Modifier.fillMaxSize(),
                                        contentScale = ContentScale.Crop
                                    )
                                    Row(
                                        modifier = Modifier
                                            .align(Alignment.TopStart)
                                            .padding(10.dp),
                                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                                    ) {
                                        SarthiBadge(
                                            text = item.category.uppercase().replace("_", " "),
                                            tone = tone
                                        )
                                        if (item.crop != null) {
                                            Surface(
                                                color = Color(0xB80F172A),
                                                shape = RoundedCornerShape(6.dp)
                                            ) {
                                                Text(
                                                    text = item.crop,
                                                    color = Color.White,
                                                    fontSize = 9.sp,
                                                    fontWeight = FontWeight.Bold,
                                                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                                )
                                            }
                                        }
                                    }
                                }

                                Column(modifier = Modifier.padding(14.dp)) {
                                    Text(
                                        text = item.title,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.ExtraBold,
                                        color = SarthiText,
                                        letterSpacing = (-0.3).sp
                                    )
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = item.summary,
                                        fontSize = 11.sp,
                                        color = SarthiMuted,
                                        lineHeight = 15.sp
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "Source: ${item.source} · Verified",
                                        fontSize = 8.5.sp,
                                        color = SarthiMuted
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
