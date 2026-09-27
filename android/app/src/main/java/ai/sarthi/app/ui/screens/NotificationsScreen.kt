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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.ui.components.BadgeTone
import ai.sarthi.app.ui.components.SarthiBadge
import ai.sarthi.app.ui.components.SarthiCard
import ai.sarthi.app.ui.components.SarthiHeader
import ai.sarthi.app.ui.components.SarthiIcon
import ai.sarthi.app.ui.theme.SarthiBg
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiText

@Composable
fun NotificationsScreen(
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
            title = "Farm Notifications & Alerts",
            onBack = onBack
        )

        Column(modifier = Modifier.padding(horizontal = 16.dp)) {
            Text(
                text = "Live Agro-Intelligence Feed",
                fontSize = 22.sp,
                fontWeight = FontWeight.ExtraBold,
                color = SarthiText,
                letterSpacing = (-0.5).sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Real-time alerts generated from telemetry, outbreak models, and state advisories.",
                fontSize = 11.5.sp,
                color = SarthiMuted
            )

            Spacer(modifier = Modifier.height(16.dp))

            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                NotificationItemCard(
                    icon = "cloud",
                    badge = "WEATHER TELEMETRY",
                    badgeTone = BadgeTone.Amber,
                    time = "10 mins ago",
                    title = "High Humidity Fungal Warning",
                    message = "Atmospheric relative humidity recorded at 87%. Delay foliar fungicide application until 4:00 PM."
                )

                NotificationItemCard(
                    icon = "shield",
                    badge = "OUTBREAK RADAR",
                    badgeTone = BadgeTone.Danger,
                    time = "1 hour ago",
                    title = "Village Outbreak Alert: Warangal Block",
                    message = "12 verified farmer reports of whitefly and leaf curl in adjoining clusters. Preventive sticky traps advised."
                )

                NotificationItemCard(
                    icon = "spark",
                    badge = "HINDSIGHT RETAIN",
                    badgeTone = BadgeTone.Green,
                    time = "Today",
                    title = "Memory Constraint Synchronized",
                    message = "Sarthi verified your borewell water limit of 1 hour/day. High-water crop suggestions automatically excluded."
                )

                NotificationItemCard(
                    icon = "rupee",
                    badge = "MANDI UPDATE",
                    badgeTone = BadgeTone.Neutral,
                    time = "Yesterday",
                    title = "Warangal Mandi Modal Price Up",
                    message = "Black Gram (Urad) traded at ₹7,650 / q (+4.2%). Optimal window for ready produce dispatch."
                )
            }
        }
    }
}

@Composable
fun NotificationItemCard(
    icon: String,
    badge: String,
    badgeTone: BadgeTone,
    time: String,
    title: String,
    message: String
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
                    SarthiBadge(text = badge, tone = badgeTone)
                    Text(text = time, fontSize = 9.sp, color = SarthiMuted)
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = title,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                    color = SarthiText
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = message,
                    fontSize = 11.sp,
                    color = SarthiMuted,
                    lineHeight = 15.sp
                )
            }
        }
    }
}
