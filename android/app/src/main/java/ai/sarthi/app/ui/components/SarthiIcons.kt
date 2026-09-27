package ai.sarthi.app.ui.components

import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.ArrowForward
import androidx.compose.material.icons.outlined.Air
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Cloud
import androidx.compose.material.icons.outlined.CurrencyRupee
import androidx.compose.material.icons.outlined.Eco
import androidx.compose.material.icons.outlined.EmojiEvents
import androidx.compose.material.icons.outlined.FilterList
import androidx.compose.material.icons.outlined.Group
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Mic
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.Psychology
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Shield
import androidx.compose.material.icons.outlined.ThumbDown
import androidx.compose.material.icons.outlined.ThumbUp
import androidx.compose.material.icons.outlined.TrendingDown
import androidx.compose.material.icons.outlined.TrendingUp
import androidx.compose.material.icons.outlined.WaterDrop
import androidx.compose.material.icons.outlined.WbSunny
import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

@Composable
fun SarthiIcon(
    name: String,
    modifier: Modifier = Modifier,
    size: Dp = 22.dp,
    tint: Color = Color.Unspecified
) {
    val vector: ImageVector = when (name.lowercase()) {
        "home" -> Icons.Outlined.Home
        "leaf" -> Icons.Outlined.Eco
        "spark" -> Icons.Outlined.AutoAwesome
        "users" -> Icons.Outlined.Group
        "user" -> Icons.Outlined.Person
        "bell" -> Icons.Outlined.Notifications
        "search" -> Icons.Outlined.Search
        "mic" -> Icons.Outlined.Mic
        "pin" -> Icons.Outlined.LocationOn
        "cloud" -> Icons.Outlined.Cloud
        "drop" -> Icons.Outlined.WaterDrop
        "wind" -> Icons.Outlined.Air
        "arrow" -> Icons.AutoMirrored.Outlined.ArrowForward
        "back" -> Icons.AutoMirrored.Outlined.ArrowBack
        "calendar" -> Icons.Outlined.CalendarMonth
        "brain" -> Icons.Outlined.Psychology
        "sun" -> Icons.Outlined.WbSunny
        "check" -> Icons.Outlined.Check
        "close" -> Icons.Outlined.Close
        "shield" -> Icons.Outlined.Shield
        "award" -> Icons.Outlined.EmojiEvents
        "trendingup" -> Icons.Outlined.TrendingUp
        "trendingdown" -> Icons.Outlined.TrendingDown
        "rupee" -> Icons.Outlined.CurrencyRupee
        "filter" -> Icons.Outlined.FilterList
        "info" -> Icons.Outlined.Info
        "thumbup" -> Icons.Outlined.ThumbUp
        "thumbdown" -> Icons.Outlined.ThumbDown
        "play" -> Icons.Outlined.PlayArrow
        "pause" -> Icons.Outlined.Pause
        "refresh" -> Icons.Outlined.Refresh
        else -> Icons.Outlined.Info
    }

    Icon(
        imageVector = vector,
        contentDescription = name,
        modifier = modifier.size(size),
        tint = tint
    )
}
