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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.data.model.EnvironmentalProfile
import ai.sarthi.app.data.model.UserProfile
import ai.sarthi.app.data.model.WeatherData
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.ButtonKind
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiButton
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiSectionTitle
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun WeatherDetailScreen(
    user: UserProfile,
    weather: WeatherData,
    envProfile: EnvironmentalProfile,
    onRefresh: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(SarthiBg)
            .verticalScroll(rememberScrollState())
            .padding(bottom = 90.dp)
    ) {
        SarthiHeader(
            title = "Hyperlocal Agro-Weather",
            onBack = onBack
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            Text(
                text = user.location,
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Live telemetry from OpenWeather & IMD Agro-meteorological sensors.",
                fontSize = 11.5.sp,
                color = SarthiMuted
            )

            Spacer(modifier = Modifier.height(14.dp))

            // Main Weather Card
            WeatherCard(
                weather = weather,
                location = user.location,
                onClick = {}
            )

            // Environmental metrics
            SarthiSectionTitle(title = "Agricultural Environmental Profile (Soil & Telemetry)")
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                MetricCard(
                    title = "SOIL TYPE",
                    value = envProfile.soilType.split(" ").firstOrNull() ?: "Black",
                    sub = envProfile.soilType,
                    modifier = Modifier.weight(1f)
                )
                MetricCard(
                    title = "NITROGEN (N)",
                    value = "${envProfile.nitrogen}",
                    sub = "kg/ha",
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                MetricCard(
                    title = "PHOSPHORUS (P)",
                    value = "${envProfile.phosphorus}",
                    sub = "kg/ha",
                    modifier = Modifier.weight(1f)
                )
                MetricCard(
                    title = "SOIL PH",
                    value = "${envProfile.soilPh}",
                    sub = "Normal Range",
                    modifier = Modifier.weight(1f)
                )
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Farm Outlook Card
            SarthiCard {
                Column(modifier = Modifier.padding(16.dp)) {
                    SarthiBadge(text = "AGRO-WEATHER RECOMMENDATION", tone = BadgeTone.Amber)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = if (weather.humidity > 80) "Fungal Spore Risk Alert" else "Favorable Farming Conditions",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = SarthiText
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (weather.humidity > 80)
                            "Relative humidity is elevated at ${weather.humidity.toInt()}%. Avoid early morning spraying. Optimal bio-fungicide spray window is 4:00 PM – 6:30 PM."
                        else "Weather is clear with low moisture risk. Normal intercultural operations can proceed as scheduled.",
                        fontSize = 11.5.sp,
                        color = SarthiMuted,
                        lineHeight = 16.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                SarthiButton(
                    text = "Refresh Telemetry",
                    icon = "refresh",
                    kind = ButtonKind.Soft,
                    onClick = onRefresh
                )
            }
        }
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    sub: String,
    modifier: Modifier = Modifier
) {
    SarthiCard(modifier = modifier) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(text = title, fontSize = 8.5.sp, fontWeight = FontWeight.Bold, color = SarthiMuted)
            Spacer(modifier = Modifier.height(2.dp))
            Text(text = value, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = SarthiText)
            Text(text = sub, fontSize = 9.sp, color = SarthiGreen, fontWeight = FontWeight.SemiBold)
        }
    }
}
