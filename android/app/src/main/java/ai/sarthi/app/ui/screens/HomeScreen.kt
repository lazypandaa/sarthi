package ai.sarthi.app.ui.screens

import androidx.compose.foundation.BorderStroke
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
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import ai.sarthi.app.data.model.AgriNewsItem
import ai.sarthi.app.data.model.CropRecommendationItem
import ai.sarthi.app.data.model.OutbreakMapResponse
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.data.model.WeatherData
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.components.SarthiIconButton
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiAmber
import ai.sarthi.app.ui.theme.SarthiAmberBg
import ai.sarthi.app.ui.theme.SarthiAmberText
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiGreenDark
import ai.sarthi.app.ui.theme.SarthiHeroEnd
import ai.sarthi.app.ui.theme.SarthiHeroMid
import ai.sarthi.app.ui.theme.SarthiHeroStart
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun HomeScreen(
    user: UserProfile,
    weather: WeatherData,
    cropRecs: List<CropRecommendationItem>,
    agriNews: List<AgriNewsItem>,
    outbreakMap: OutbreakMapResponse,
    memoriesCount: Int,
    onNavigate: (String) -> Unit
) {
    val topCrop = cropRecs.firstOrNull()
    val topNews = agriNews.firstOrNull()
    val topOutbreak = outbreakMap.outbreaks.firstOrNull()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        // ================= HERO HEADER =================
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.linearGradient(
                        colors = listOf(SarthiHeroStart, SarthiHeroMid, SarthiHeroEnd)
                    ),
                    shape = RoundedCornerShape(bottomStart = 32.dp, bottomEnd = 32.dp)
                )
                .padding(top = 28.dp, start = 18.dp, end = 18.dp, bottom = 65.dp)
        ) {
            Column(modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column {
                        Text(
                            text = "Namaste, Farmer",
                            color = Color(0xBFFFFFFF),
                            fontSize = 13.5.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = user.phoneNumber,
                            color = Color.White,
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = (-0.5).sp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            SarthiIcon(name = "pin", size = 14.dp, tint = Color(0xC7FFFFFF))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = user.location,
                                color = Color(0xC7FFFFFF),
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Normal
                            )
                        }
                    }

                    SarthiIconButton(
                        icon = "bell",
                        onClick = { onNavigate("notifications") },
                        isDark = true
                    )
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Hero Ask Button
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(18.dp))
                        .background(Color(0x1AFFFFFF))
                        .clickable { onNavigate("voice") }
                        .padding(horizontal = 14.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.weight(1f)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(38.dp)
                                .background(Color.White, RoundedCornerShape(12.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            SarthiIcon(name = "spark", size = 20.dp, tint = SarthiGreen)
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(
                                text = "Ask Sarthi AI Agronomist",
                                color = Color.White,
                                fontSize = 13.5.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Speak in Hindi, Telugu, or English",
                                color = Color(0xB3FFFFFF),
                                fontSize = 10.sp
                            )
                        }
                    }

                    SarthiIcon(name = "mic", size = 22.dp, tint = Color.White)
                }
            }
        }

        // ================= MAIN CONTENT (Overlaps Hero with -45dp) =================
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .offset(y = (-45).dp)
                .padding(horizontal = 16.dp)
        ) {
            // Weather Card
            WeatherCard(
                weather = weather,
                location = user.location.split(",")[0],
                onClick = { onNavigate("weather") }
            )

            // Recommended for your farm
            SarthiSectionTitle(title = "Recommended for your farm")
            RecommendationCard(
                crop = topCrop?.cropName ?: "Black Gram (Urad)",
                match = topCrop?.soilCompatibility?.toInt() ?: 95,
                explanation = topCrop?.explanation ?: "Adapted for your soil nutrients and irrigation conditions.",
                onClick = { onNavigate("ai") }
            )

            // Shortcuts Grid: 2 side-by-side buttons
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                ShortcutCard(
                    icon = "calendar",
                    title = "Crop calendar",
                    subtitle = "Seasonal operations",
                    modifier = Modifier.weight(1f),
                    onClick = { onNavigate("calendar") }
                )
                ShortcutCard(
                    icon = "brain",
                    title = "Farm memories ($memoriesCount)",
                    subtitle = "Hindsight retention",
                    modifier = Modifier.weight(1f),
                    onClick = { onNavigate("memory") }
                )
            }

            // Today's farm advice & schemes
            SarthiSectionTitle(
                title = "Today's farm advice & schemes",
                action = "View all",
                onAction = { onNavigate("advice") }
            )
            CardAdviceBanner(
                newsItem = topNews,
                onClick = { onNavigate("advice") }
            )

            // Village outbreak alerts
            SarthiSectionTitle(
                title = "Village outbreak alerts",
                action = "Community",
                onAction = { onNavigate("community") }
            )
            CardOutbreakAlert(
                outbreak = topOutbreak,
                onClick = { onNavigate("community") }
            )
        }
    }
}

@Composable
fun WeatherCard(
    weather: WeatherData,
    location: String,
    onClick: () -> Unit
) {
    SarthiCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        SarthiIcon(name = "pin", size = 13.dp, tint = SarthiMuted)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = location,
                            color = SarthiMuted,
                            fontSize = 11.5.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(verticalAlignment = Alignment.Top) {
                        Text(
                            text = "${weather.temperature.toInt()}",
                            fontSize = 42.sp,
                            fontWeight = FontWeight.Bold,
                            color = SarthiText,
                            letterSpacing = (-1).sp
                        )
                        Text(
                            text = "°C",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Medium,
                            color = SarthiText,
                            modifier = Modifier.padding(top = 4.dp)
                        )
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        SarthiIcon(name = "cloud", size = 16.dp, tint = SarthiGreen)
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = weather.condition,
                            fontSize = 12.5.sp,
                            color = SarthiText,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }

                // Weather Art
                Box(
                    modifier = Modifier.size(width = 85.dp, height = 75.dp),
                    contentAlignment = Alignment.BottomEnd
                ) {
                    SarthiIcon(
                        name = "sun",
                        size = 36.dp,
                        tint = Color(0xFFF3B935),
                        modifier = Modifier.align(Alignment.TopEnd)
                    )
                    SarthiIcon(
                        name = "cloud",
                        size = 58.dp,
                        tint = Color(0xFFA9C9D0),
                        modifier = Modifier.align(Alignment.BottomStart)
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Weather Stats Grid (3 columns)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 10.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                WeatherStatCol(icon = "drop", value = "${weather.humidity.toInt()}%", label = "Humidity", modifier = Modifier.weight(1f))
                WeatherStatCol(icon = "cloud", value = "${weather.rainfall.toInt()} mm", label = "Rain", modifier = Modifier.weight(1f))
                WeatherStatCol(icon = "wind", value = "12 km/h", label = "Wind", modifier = Modifier.weight(1f))
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Advisory warning chip
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = SarthiAmberBg,
                shape = RoundedCornerShape(11.dp)
            ) {
                Text(
                    text = weather.alert ?: if (weather.humidity > 80)
                        "High humidity (${weather.humidity.toInt()}%) increases fungal risk. Safe spray window: 4:00 PM – 6:30 PM."
                    else "Weather conditions stable. Verified by IMD & OpenWeather telemetry.",
                    color = SarthiAmberText,
                    fontSize = 10.5.sp,
                    fontWeight = FontWeight.SemiBold,
                    lineHeight = 15.sp,
                    modifier = Modifier.padding(10.dp)
                )
            }
        }
    }
}

@Composable
fun WeatherStatCol(
    icon: String,
    value: String,
    label: String,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.padding(horizontal = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        SarthiIcon(name = icon, size = 16.dp, tint = SarthiGreen)
        Spacer(modifier = Modifier.width(6.dp))
        Column {
            Text(text = value, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = SarthiText)
            Text(text = label, fontSize = 8.5.sp, color = SarthiMuted)
        }
    }
}

@Composable
fun RecommendationCard(
    crop: String,
    match: Int,
    explanation: String,
    onClick: () -> Unit
) {
    SarthiCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(24.dp)
                        .background(SarthiGreen, RoundedCornerShape(8.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    SarthiIcon(name = "spark", size = 14.dp, tint = Color.White)
                }
                Text(
                    text = "SARTHI AI",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = SarthiGreen,
                    letterSpacing = 1.sp
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "MEMORY-INFORMED CROP RECOMMENDATION",
                fontSize = 8.5.sp,
                fontWeight = FontWeight.Bold,
                color = SarthiMuted,
                letterSpacing = 0.5.sp
            )
            Spacer(modifier = Modifier.height(2.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = crop,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = SarthiText,
                        letterSpacing = (-0.5).sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = explanation,
                        fontSize = 11.5.sp,
                        color = SarthiMuted,
                        lineHeight = 16.sp
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                // Score ring
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(SarthiMint),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "$match%",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.ExtraBold,
                            color = SarthiGreen
                        )
                        Text(
                            text = "farm fit",
                            fontSize = 7.5.sp,
                            color = SarthiMuted
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            SarthiButton(
                text = "Explore recommendation",
                icon = "arrow",
                onClick = onClick,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
fun ShortcutCard(
    icon: String,
    title: String,
    subtitle: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    SarthiCard(
        modifier = modifier.height(100.dp),
        onClick = onClick,
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(36.dp)
                    .background(SarthiMint, RoundedCornerShape(12.dp)),
                contentAlignment = Alignment.Center
            ) {
                SarthiIcon(name = icon, size = 18.dp, tint = SarthiGreen)
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = title,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = SarthiText,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            Text(
                text = subtitle,
                fontSize = 9.sp,
                color = SarthiMuted,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
fun CardAdviceBanner(
    newsItem: AgriNewsItem?,
    onClick: () -> Unit
) {
    val photo = newsItem?.image ?: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&auto=format&fit=crop&q=80"

    SarthiCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Column {
            AsyncImage(
                model = photo,
                contentDescription = "Advisory",
                modifier = Modifier
                    .fillMaxWidth()
                    .height(145.dp),
                contentScale = ContentScale.Crop
            )
            Column(modifier = Modifier.padding(14.dp)) {
                SarthiBadge(
                    text = newsItem?.category?.uppercase()?.replace("_", " ") ?: "HYPERLOCAL ADVISORY",
                    tone = BadgeTone.Green
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = newsItem?.title ?: "Protect your crop from unseasonal weather",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = SarthiText,
                    letterSpacing = (-0.3).sp
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = newsItem?.summary ?: "Western disturbance and humidity tracking active. Check foliage for fungal stress.",
                    fontSize = 11.sp,
                    color = SarthiMuted,
                    lineHeight = 15.sp,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "${newsItem?.source ?: "IMD Agromet Advisory Service"} · Verified",
                    fontSize = 9.sp,
                    color = SarthiMuted
                )
            }
        }
    }
}

@Composable
fun CardOutbreakAlert(
    outbreak: ai.sarthi.app.data.model.OutbreakVillage?,
    onClick: () -> Unit
) {
    SarthiCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(11.dp)
                    .background(SarthiAmber, CircleShape)
            )
            Spacer(modifier = Modifier.width(10.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = if (outbreak != null) "${outbreak.village}: ${outbreak.recentReports.firstOrNull()?.crop ?: "Crop"} alert"
                    else "Tomato leaf curl reported",
                    fontSize = 12.5.sp,
                    fontWeight = FontWeight.Bold,
                    color = SarthiText
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = if (outbreak != null) "${outbreak.totalReports} verified reports in ${outbreak.village} · ${outbreak.alertLevel.uppercase()} risk"
                    else "Active cluster monitoring in your agricultural block.",
                    fontSize = 9.5.sp,
                    color = SarthiMuted
                )
            }
            SarthiIcon(name = "arrow", size = 18.dp, tint = SarthiMuted)
        }
    }
}
