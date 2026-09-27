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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import ai.sarthi.app.data.model.CropRecommendationItem
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun CropDetailScreen(
    crop: CropRecommendationItem,
    onBack: () -> Unit
) {
    val photo = when {
        crop.cropName.contains("wheat", ignoreCase = true) -> "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=900&auto=format&fit=crop&q=80"
        crop.cropName.contains("rice", ignoreCase = true) || crop.cropName.contains("paddy", ignoreCase = true) -> "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=900&auto=format&fit=crop&q=80"
        crop.cropName.contains("soybean", ignoreCase = true) -> "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?w=900&auto=format&fit=crop&q=80"
        crop.cropName.contains("gram", ignoreCase = true) -> "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=900&auto=format&fit=crop&q=80"
        else -> "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&auto=format&fit=crop&q=80"
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "ICAR Package of Practices",
            onBack = onBack
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            // Photo banner
            SarthiCard {
                Box(modifier = Modifier.fillMaxWidth().height(180.dp)) {
                    AsyncImage(
                        model = photo,
                        contentDescription = crop.cropName,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Title & Fit Ring Card
            SarthiCard {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        SarthiBadge(text = crop.category.uppercase(), tone = BadgeTone.Green)
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = crop.cropName,
                            fontSize = 24.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = SarthiText
                        )
                        if (crop.scientificName != null) {
                            Text(
                                text = crop.scientificName,
                                fontSize = 11.sp,
                                color = SarthiMuted
                            )
                        }
                    }

                    Box(
                        modifier = Modifier
                            .size(68.dp)
                            .clip(CircleShape)
                            .background(SarthiMint),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = "${crop.soilCompatibility.toInt()}%",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.ExtraBold,
                                color = SarthiGreen
                            )
                            Text(text = "soil fit", fontSize = 8.sp, color = SarthiMuted)
                        }
                    }
                }
            }

            // Agronomic Specs
            SarthiSectionTitle(title = "Cultivation Parameters")
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("DURATION", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text("${crop.durationDays} Days", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("WATER NEED", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(crop.waterRequirement, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("CLIMATE MATCH", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(crop.climateMatch, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("SOURCE", fontSize = 8.5.sp, color = SarthiMuted, fontWeight = FontWeight.Bold)
                            Text(crop.source, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
                        }
                    }
                }
            }

            // Agronomic Recommendation Details
            SarthiSectionTitle(title = "Agronomic Guidance")
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = crop.explanation,
                        fontSize = 12.sp,
                        color = SarthiText,
                        lineHeight = 17.sp
                    )
                }
            }
        }
    }
}
