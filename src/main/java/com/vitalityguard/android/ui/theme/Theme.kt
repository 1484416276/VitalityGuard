package com.vitalityguard.android.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = VitalityGreen80,
    onPrimary = DarkBackground,
    primaryContainer = Green40,
    onPrimaryContainer = VitalityGreenLight,
    secondary = Teal80,
    onSecondary = DarkBackground,
    secondaryContainer = Teal40,
    onSecondaryContainer = TealLight,
    tertiary = Orange80,
    onTertiary = DarkBackground,
    background = DarkBackground,
    surface = DarkSurface,
    onBackground = LightBackground,
    onSurface = LightBackground,
    error = ErrorRed,
    onError = LightBackground
)

private val LightColorScheme = lightColorScheme(
    primary = Green40,
    onPrimary = LightBackground,
    primaryContainer = VitalityGreenLight,
    onPrimaryContainer = Green40,
    secondary = Teal40,
    onSecondary = LightBackground,
    secondaryContainer = TealLight,
    onSecondaryContainer = Teal40,
    tertiary = Orange40,
    onTertiary = LightBackground,
    background = LightBackground,
    surface = LightSurface,
    onBackground = DarkBackground,
    onSurface = DarkBackground,
    error = ErrorRed,
    onError = LightBackground
)

@Composable
fun VitalityGuardTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
