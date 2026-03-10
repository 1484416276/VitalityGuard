package com.vitalityguard.android.data

/**
 * 应用配置数据类
 * 对应原 Python 项目的 config_manager.py
 */
data class AppConfig(
    val language: String = "zh_CN",
    val autoStart: Boolean = false,
    val autoUpdate: Boolean = true,
    val mode: ModeConfig = ModeConfig()
)

data class ModeConfig(
    val name: String = "默认模式",
    val workDurationMinutes: Int = 60,
    val restDurationMinutes: Int = 5,
    val allowBlackScreenUnlock: Boolean = true,
    val nightSleepEnabled: Boolean = false,
    val nightSleepStart: String = "22:30",
    val nightSleepEnd: String = "07:00",
    val countdownSeconds: Int = 10
) {
    companion object {
        val DEFAULT = ModeConfig()
    }
}

/**
 * 调度器状态
 */
enum class SchedulerState {
    WORKING,    // 工作中
    RESTING     // 休息中（黑屏/锁屏）
}

/**
 * 调度器动作
 */
enum class SchedulerAction {
    NONE,       // 无动作
    LOCK,       // 锁定屏幕
    UNLOCK,     // 解锁屏幕
    NIGHT_REST  // 夜间休息
}

/**
 * 倒计时状态
 */
data class CountdownState(
    val isActive: Boolean = false,
    val remainingSeconds: Int = 0,
    val canCancel: Boolean = true
)

/**
 * 锁屏状态
 */
data class LockScreenState(
    val isLocked: Boolean = false,
    val remainingSeconds: Int = 0,
    val isNightRest: Boolean = false,
    val escPressCount: Int = 0
)