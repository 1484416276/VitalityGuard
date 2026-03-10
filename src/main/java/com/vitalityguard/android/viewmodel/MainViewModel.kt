package com.vitalityguard.android.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.vitalityguard.android.data.*
import com.vitalityguard.android.service.SchedulerLogic
import com.vitalityguard.android.service.VitalityGuardService
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * UI 状态
 */
data class UiState(
    val config: VitalityConfig = VitalityConfig(),
    val serviceState: VitalityGuardService.ServiceState = VitalityGuardService.ServiceState.Idle,
    val isServiceRunning: Boolean = false,
    val isLocked: Boolean = false,
    val remainingSeconds: Int = 0,
    val formattedRemainingTime: String = "--:--",
    val isNightRest: Boolean = false,
    val allowUnlock: Boolean = true,
    val escPressCount: Int = 0,
    val isCountdownActive: Boolean = false,
    val countdownSeconds: Int = 0
)

/**
 * 主 ViewModel
 * 管理应用状态和业务逻辑
 */
class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val configManager = ConfigManager(application)
    private var scheduler: SchedulerLogic? = null
    private var timerJob: Job? = null
    private var escResetJob: Job? = null
    private var serviceStateJob: Job? = null

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadConfig()
        observeServiceState()
    }

    private fun loadConfig() {
        val config = configManager.loadConfig()
        _uiState.update { it.copy(config = config) }
    }

    private fun observeServiceState() {
        serviceStateJob = viewModelScope.launch {
            VitalityGuardService.serviceState.collect { state ->
                _uiState.update { it.copy(serviceState = state) }
                
                when (state) {
                    is VitalityGuardService.ServiceState.Working -> {
                        _uiState.update {
                            it.copy(
                                isLocked = false,
                                isNightRest = false,
                                isServiceRunning = true,  // 确保服务运行状态为true
                                remainingSeconds = state.remainingSeconds.toInt(),
                                formattedRemainingTime = formatTime(state.remainingSeconds)
                            )
                        }
                    }
                    is VitalityGuardService.ServiceState.Resting -> {
                        _uiState.update {
                            it.copy(
                                isLocked = true,
                                isNightRest = false,
                                isServiceRunning = true,  // 确保服务运行状态为true
                                remainingSeconds = state.remainingSeconds.toInt(),
                                formattedRemainingTime = formatTime(state.remainingSeconds)
                            )
                        }
                    }
                    is VitalityGuardService.ServiceState.NightRest -> {
                        _uiState.update {
                            it.copy(
                                isLocked = true,
                                isNightRest = true,
                                isServiceRunning = true,  // 确保服务运行状态为true
                                remainingSeconds = state.remainingSeconds.toInt()
                            )
                        }
                    }
                    is VitalityGuardService.ServiceState.Paused -> {
                        // 暂停时保持当前状态，但服务仍在运行
                        _uiState.update { it.copy(isServiceRunning = true) }
                    }
                    is VitalityGuardService.ServiceState.Idle -> {
                        _uiState.update {
                            it.copy(
                                isLocked = false,
                                isNightRest = false,
                                isServiceRunning = false,
                                remainingSeconds = 0,
                                formattedRemainingTime = "--:--"
                            )
                        }
                    }
                }
            }
        }
    }

    private fun formatTime(seconds: Long): String {
        val hours = seconds / 3600
        val minutes = (seconds % 3600) / 60
        val secs = seconds % 60
        return if (hours > 0) {
            String.format("%02d:%02d:%02d", hours, minutes, secs)
        } else {
            String.format("%02d:%02d", minutes, secs)
        }
    }

    fun updateConfig(newConfig: VitalityConfig) {
        configManager.saveConfig(newConfig)
        _uiState.update { it.copy(config = newConfig) }
        
        // 如果服务正在运行，通知服务热更新配置
        if (_uiState.value.isServiceRunning) {
            VitalityGuardService.updateConfig(getApplication())
        }
    }

    fun startService() {
        val config = _uiState.value.config
        configManager.updateServiceEnabled(true)
        
        _uiState.update { 
            it.copy(
                isServiceRunning = true,
                allowUnlock = config.allowUnlock
            )
        }
        
        // 启动后台服务
        VitalityGuardService.start(getApplication())
    }

    fun stopService() {
        configManager.updateServiceEnabled(false)
        VitalityGuardService.stop(getApplication())
        
        _uiState.update { 
            it.copy(
                isServiceRunning = false,
                isLocked = false,
                remainingSeconds = 0,
                formattedRemainingTime = "--:--"
            )
        }
    }

    fun unlock() {
        if (!_uiState.value.allowUnlock) return
        
        _uiState.update {
            it.copy(
                isLocked = false,
                escPressCount = 0,
                isNightRest = false
            )
        }
    }

    /**
     * 增加返回键按压计数（用于紧急解锁）
     */
    fun incrementEscPress() {
        if (!_uiState.value.allowUnlock || !_uiState.value.isLocked) return
        
        val newCount = _uiState.value.escPressCount + 1
        
        if (newCount >= 5) {
            // 达到5次，解锁
            unlock()
        } else {
            _uiState.update { it.copy(escPressCount = newCount) }
            
            // 重置计数器（2秒内需要按5次）
            escResetJob?.cancel()
            escResetJob = viewModelScope.launch {
                delay(2000)
                _uiState.update { it.copy(escPressCount = 0) }
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        timerJob?.cancel()
        escResetJob?.cancel()
        serviceStateJob?.cancel()
    }
}