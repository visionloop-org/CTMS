package com.ctms.app.presentation.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * Strict Dark Theme Color Scheme for CTMS.
 * Light mode is explicitly disallowed to ensure outdoor legibility, battery conservation
 * on OLED handheld devices (Zebra/Honeywell/smartphones), and high contrast for drivers.
 */
private val CTMSDarkColorScheme = darkColorScheme(
    primary = CyanPrimary,
    onPrimary = OnCyanPrimary,
    primaryContainer = CyanPrimaryContainer,
    onPrimaryContainer = OnCyanPrimaryContainer,
    secondary = EmeraldSafe,
    onSecondary = OnEmeraldSafe,
    secondaryContainer = EmeraldContainer,
    onSecondaryContainer = OnEmeraldContainer,
    tertiary = AmberWarning,
    onTertiary = OnAmberWarning,
    tertiaryContainer = AmberContainer,
    onTertiaryContainer = OnAmberContainer,
    error = CrimsonDanger,
    onError = OnCrimsonDanger,
    errorContainer = CrimsonContainer,
    onErrorContainer = OnCrimsonContainer,
    background = DarkBackground,
    onBackground = TextPrimary,
    surface = DarkSurface,
    onSurface = TextPrimary,
    surfaceVariant = DarkSurfaceVariant,
    onSurfaceVariant = TextSecondary,
    outline = BorderSubtle
)

/**
 * CTMSTheme enforces Dark Theme ONLY across the entire application.
 * System light/dark preference is intentionally ignored to maintain industrial safety
 * and contrast consistency.
 */
@Composable
fun CTMSTheme(
    content: @Composable () -> Unit
) {
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as? Activity)?.window
            if (window != null) {
                window.statusBarColor = DarkBackground.toArgb()
                window.navigationBarColor = DarkBackground.toArgb()
                val controller = WindowCompat.getInsetsController(window, view)
                // False means light text / icons on dark status/nav bars
                controller.isAppearanceLightStatusBars = false
                controller.isAppearanceLightNavigationBars = false
            }
        }
    }

    MaterialTheme(
        colorScheme = CTMSDarkColorScheme,
        typography = CTMSTypography,
        content = content
    )
}
