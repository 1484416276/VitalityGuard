package com.vitalityguard.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.vitalityguard.android.ui.screens.LockScreen
import com.vitalityguard.android.ui.screens.SettingsScreen
import com.vitalityguard.android.ui.theme.VitalityGuardTheme
import com.vitalityguard.android.viewmodel.MainViewModel

/**
 * 主 Activity
 * 活力卫士 - 防沉迷助手 Android 版
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        setContent {
            VitalityGuardTheme {
                val viewModel: MainViewModel = viewModel()
                val uiState by viewModel.uiState.collectAsState()
                
                if (uiState.isLocked) {
                    // 锁屏界面
                    LockScreen(
                        remainingSeconds = uiState.remainingSeconds,
                        isNightRest = uiState.isNightRest,
                        allowUnlock = uiState.allowUnlock,
                        escPressCount = uiState.escPressCount,
                        onUnlock = { viewModel.unlock() }
                    )
                } else {
                    // 设置界面
                    SettingsScreen(
                        currentConfig = uiState.config,
                        isServiceRunning = uiState.isServiceRunning,
                        remainingTime = uiState.formattedRemainingTime,
                        onConfigChange = { viewModel.updateConfig(it) },
                        onStartService = { viewModel.startService() },
                        onStopService = { viewModel.stopService() }
                    )
                }
            }
        }
    }
}