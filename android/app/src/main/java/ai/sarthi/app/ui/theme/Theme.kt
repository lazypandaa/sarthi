package ai.sarthi.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val SarthiColorScheme = lightColorScheme(
    primary = SarthiGreen,
    onPrimary = SarthiSurface,
    primaryContainer = SarthiMint,
    onPrimaryContainer = SarthiGreenDark,
    secondary = SarthiGreenLight,
    onSecondary = SarthiSurface,
    background = SarthiBg,
    onBackground = SarthiText,
    surface = SarthiSurface,
    onSurface = SarthiText,
    outline = SarthiLine
)

@Composable
fun SarthiAppTheme(
    content: @Composable () -> Unit
) {
    val colorScheme = SarthiColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = SarthiHeroStart.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
