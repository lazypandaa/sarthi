package ai.sarthi.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ai.sarthi.app.ui.theme.SarthiAmber
import ai.sarthi.app.ui.theme.SarthiAmberBg
import ai.sarthi.app.ui.theme.SarthiAmberText
import ai.sarthi.app.ui.theme.SarthiGreen
import ai.sarthi.app.ui.theme.SarthiLine
import ai.sarthi.app.ui.theme.SarthiMint
import ai.sarthi.app.ui.theme.SarthiMuted
import ai.sarthi.app.ui.theme.SarthiNeutralBg
import ai.sarthi.app.ui.theme.SarthiRed
import ai.sarthi.app.ui.theme.SarthiRedBg
import ai.sarthi.app.ui.theme.SarthiSurface
import ai.sarthi.app.ui.theme.SarthiText

enum class ButtonKind {
    Primary, Soft, Icon, Ghost
}

enum class BadgeTone {
    Green, Amber, Danger, Neutral
}

@Composable
fun SarthiCard(
    modifier: Modifier = Modifier,
    shape: RoundedCornerShape = RoundedCornerShape(20.dp),
    backgroundColor: Color = SarthiSurface,
    borderColor: Color = Color(0x1011472F),
    elevation: Dp = 1.dp,
    onClick: (() -> Unit)? = null,
    content: @Composable () -> Unit
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .then(
                if (onClick != null) Modifier.clickable { onClick() }
                else Modifier
            ),
        shape = shape,
        color = backgroundColor,
        border = BorderStroke(1.dp, borderColor),
        shadowElevation = elevation
    ) {
        content()
    }
}

@Composable
fun SarthiButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    kind: ButtonKind = ButtonKind.Primary,
    icon: String? = null,
    enabled: Boolean = true
) {
    val bg = when (kind) {
        ButtonKind.Primary -> SarthiGreen
        ButtonKind.Soft -> SarthiMint
        ButtonKind.Icon -> SarthiSurface
        ButtonKind.Ghost -> Color.Transparent
    }
    val contentColor = when (kind) {
        ButtonKind.Primary -> SarthiSurface
        ButtonKind.Soft -> SarthiGreen
        ButtonKind.Icon -> SarthiText
        ButtonKind.Ghost -> SarthiGreen
    }

    Surface(
        modifier = modifier
            .height(48.dp)
            .clip(RoundedCornerShape(15.dp))
            .clickable(enabled = enabled) { onClick() },
        color = if (enabled) bg else SarthiNeutralBg,
        shape = RoundedCornerShape(15.dp),
        shadowElevation = if (kind == ButtonKind.Icon) 3.dp else 0.dp
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center
        ) {
            Text(
                text = text,
                color = if (enabled) contentColor else SarthiMuted,
                fontSize = 13.5.sp,
                fontWeight = FontWeight.Bold
            )
            if (icon != null) {
                Spacer(modifier = Modifier.width(6.dp))
                SarthiIcon(
                    name = icon,
                    size = 17.dp,
                    tint = if (enabled) contentColor else SarthiMuted
                )
            }
        }
    }
}

@Composable
fun SarthiIconButton(
    icon: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    isDark: Boolean = false,
    size: Dp = 44.dp
) {
    val bg = if (isDark) Color(0x24FFFFFF) else SarthiSurface
    val tint = if (isDark) Color.White else SarthiGreen

    Box(
        modifier = modifier
            .size(size)
            .shadow(if (isDark) 0.dp else 3.dp, CircleShape)
            .background(bg, CircleShape)
            .clip(CircleShape)
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        SarthiIcon(name = icon, size = 20.dp, tint = tint)
    }
}

@Composable
fun SarthiBadge(
    text: String,
    modifier: Modifier = Modifier,
    tone: BadgeTone = BadgeTone.Green
) {
    val (bg, textColor) = when (tone) {
        BadgeTone.Green -> Pair(SarthiMint, SarthiGreen)
        BadgeTone.Amber -> Pair(SarthiAmberBg, SarthiAmberText)
        BadgeTone.Danger -> Pair(SarthiRedBg, SarthiRed)
        BadgeTone.Neutral -> Pair(SarthiNeutralBg, SarthiMuted)
    }

    Surface(
        modifier = modifier,
        color = bg,
        shape = RoundedCornerShape(100.dp)
    ) {
        Text(
            text = text,
            color = textColor,
            fontSize = 10.sp,
            fontWeight = FontWeight.ExtraBold,
            modifier = Modifier.padding(horizontal = 9.dp, vertical = 4.dp),
            letterSpacing = 0.5.sp
        )
    }
}

@Composable
fun SarthiHeader(
    title: String,
    onBack: (() -> Unit)? = null,
    onNotificationClick: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(64.dp)
            .padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        if (onBack != null) {
            SarthiIconButton(icon = "back", onClick = onBack)
        } else {
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .background(SarthiGreen, RoundedCornerShape(13.dp)),
                contentAlignment = Alignment.Center
            ) {
                SarthiIcon(name = "leaf", size = 20.dp, tint = Color.White)
            }
        }

        Text(
            text = title,
            fontSize = 16.sp,
            fontWeight = FontWeight.ExtraBold,
            color = SarthiText,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            textAlign = TextAlign.Center,
            modifier = Modifier.weight(1f).padding(horizontal = 8.dp)
        )

        if (onNotificationClick != null) {
            SarthiIconButton(icon = "bell", onClick = onNotificationClick)
        } else {
            Spacer(modifier = Modifier.size(44.dp))
        }
    }
}

@Composable
fun SarthiSectionTitle(
    title: String,
    modifier: Modifier = Modifier,
    action: String? = null,
    onAction: (() -> Unit)? = null
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(top = 22.dp, bottom = 10.dp, start = 2.dp, end = 2.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = title,
            fontSize = 16.sp,
            fontWeight = FontWeight.ExtraBold,
            color = SarthiText
        )
        if (action != null && onAction != null) {
            Row(
                modifier = Modifier
                    .clip(RoundedCornerShape(8.dp))
                    .clickable { onAction() }
                    .padding(4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = action,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = SarthiGreen
                )
                Spacer(modifier = Modifier.width(3.dp))
                SarthiIcon(name = "arrow", size = 13.dp, tint = SarthiGreen)
            }
        }
    }
}

// 5-Tab Navigation matching frontend App.tsx exactly
data class NavItem(val id: String, val icon: String, val label: String)

val sarthiNavItems = listOf(
    NavItem("home", "home", "Home"),
    NavItem("advice", "leaf", "Advice"),
    NavItem("ai", "spark", "AI"),
    NavItem("community", "users", "Community"),
    NavItem("profile", "user", "Profile")
)

@Composable
fun SarthiBottomNav(
    activeTab: String,
    onTabSelected: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .shadow(16.dp),
        color = Color(0xF5FFFFFF),
        border = BorderStroke(1.dp, SarthiLine)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 6.dp, horizontal = 4.dp),
            horizontalArrangement = Arrangement.SpaceAround,
            verticalAlignment = Alignment.CenterVertically
        ) {
            for (item in sarthiNavItems) {
                val isActive = activeTab == item.id
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(12.dp))
                        .clickable { onTabSelected(item.id) }
                        .padding(vertical = 2.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(width = 42.dp, height = 28.dp)
                            .background(
                                color = if (isActive) SarthiMint else Color.Transparent,
                                shape = RoundedCornerShape(12.dp)
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        SarthiIcon(
                            name = item.icon,
                            size = 19.dp,
                            tint = if (isActive) SarthiGreen else Color(0xFF79827E)
                        )
                    }
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = item.label,
                        fontSize = 10.sp,
                        fontWeight = if (isActive) FontWeight.ExtraBold else FontWeight.Medium,
                        color = if (isActive) SarthiGreen else Color(0xFF79827E),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        }
    }
}
