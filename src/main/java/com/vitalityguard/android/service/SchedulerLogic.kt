package com.vitalityguard.android.service

import com.vitalityguard.android.data.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.Calendar

/**
 * 调度器逻辑类
 * 对应原 Python 项目的 scheduler_logic.py
 * 负责管理工作/休息周期和夜间休息判断
 */
class SchedulerLogic(
    private val config: ModeConfig = ModeConfig.DEFAULT,
    private val testMode: Boolean = false
) {
    // 当前状态
    private val _state = MutableStateFlow(SchedulerState.WORKING)
    val state: StateFlow<SchedulerState> = _state.asStateFlow()

    // 下一次转换时间（时间戳毫秒）
    private val _nextTransitionTime = MutableStateFlow(0L)
    val nextTransitionTime: StateFlow<Long> = _nextTransitionTime.asStateFlow()

    // 剩余时间（秒）
    private val _remainingSeconds = MutableStateFlow(0)
    val remainingSeconds: StateFlow<Int> = _remainingSeconds.asStateFlow()

    init {
        scheduleNextLock()
    }

    /**
     * 获取当前状态应有的持续时间（秒）
     */
    fun getCurrentInterval(state: SchedulerState = _state.value): Int {
        return when (state) {
            SchedulerState.WORKING -> {
                if (testMode) 10 // 测试模式：10秒
                else config.workDurationMinutes * 60
            }
            SchedulerState.RESTING -> {
                if (testMode) 5 // 测试模式：5秒
                else config.restDurationMinutes * 60
            }
        }
    }

    /**
     * 安排下一次锁定时间
     */
    private fun scheduleNextLock() {
        val interval = getCurrentInterval(SchedulerState.WORKING)
        _nextTransitionTime.value = System.currentTimeMillis() + interval * 1000L
        _remainingSeconds.value = interval
        _state.value = SchedulerState.WORKING
    }

    /**
     * 安排解锁时间
     */
    private fun scheduleUnlock() {
        val duration = getCurrentInterval(SchedulerState.RESTING)
        _nextTransitionTime.value = System.currentTimeMillis() + duration * 1000L
        _remainingSeconds.value = duration
        _state.value = SchedulerState.RESTING
    }

    /**
     * 检查是否在夜间休息时间
     */
    private fun isCurfewTime(): Boolean {
        if (!config.nightSleepEnabled) return false

        val now = Calendar.getInstance()
        val startParts = config.nightSleepStart.split(":")
        val endParts = config.nightSleepEnd.split(":")

        if (startParts.size != 2 || endParts.size != 2) return false

        val startHour = startParts[0].toIntOrNull() ?: return false
        val startMinute = startParts[1].toIntOrNull() ?: return false
        val endHour = endParts[0].toIntOrNull() ?: return false
        val endMinute = endParts[1].toIntOrNull() ?: return false

        val startCal = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, startHour)
            set(Calendar.MINUTE, startMinute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }

        val endCal = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, endHour)
            set(Calendar.MINUTE, endMinute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }

        // 处理跨天情况（例如 22:30 到 07:00）
        return if (startCal > endCal) {
            // 跨天：现在 >= 开始时间 或 现在 < 结束时间
            now >= startCal || now < endCal
        } else {
            // 不跨天
            now >= startCal && now < endCal
        }
    }

    /**
     * 更新剩余时间（每秒调用）
     */
    fun updateRemainingTime() {
        val remaining = ((_nextTransitionTime.value - System.currentTimeMillis()) / 1000).toInt()
        _remainingSeconds.value = if (remaining > 0) remaining else 0
    }

    /**
     * 检查当前状态并返回需要执行的动作
     */
    fun check(): SchedulerAction {
        // 1. 首先检查夜间休息时间
        if (isCurfewTime()) {
            return SchedulerAction.NIGHT_REST
        }

        // 2. 检查周期性锁定
        val currentTime = System.currentTimeMillis()

        return when (_state.value) {
            SchedulerState.WORKING -> {
                if (currentTime >= _nextTransitionTime.value) {
                    scheduleUnlock()
                    SchedulerAction.LOCK
                } else {
                    SchedulerAction.NONE
                }
            }
            SchedulerState.RESTING -> {
                if (currentTime >= _nextTransitionTime.value) {
                    scheduleNextLock()
                    SchedulerAction.UNLOCK
                } else {
                    SchedulerAction.NONE
                }
            }
        }
    }

    /**
     * 重置到工作状态（用于用户取消休息）
     */
    fun resetToWorking() {
        scheduleNextLock()
    }

    /**
     * 获取格式化的剩余时间字符串
     */
    fun getFormattedRemainingTime(): String {
        val seconds = _remainingSeconds.value
        val mins = seconds / 60
        val secs = seconds % 60
        return String.format("%02d:%02d", mins, secs)
    }
}