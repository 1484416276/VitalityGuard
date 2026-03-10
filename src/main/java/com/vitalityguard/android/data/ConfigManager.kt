package com.vitalityguard.android.data

import android.content.Context
import android.content.SharedPreferences
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

/**
 * 活力卫士配置数据类
 */
@Serializable
data class VitalityConfig(
    // 工作/休息周期设置
    val workDurationMinutes: Int = 60,          // 工作时长（分钟）
    val restDurationMinutes: Int = 5,           // 休息时长（分钟）
    val countdownSeconds: Int = 10,             // 倒计时时长（秒）
    
    // 夜间休息模式
    val nightRestEnabled: Boolean = false,      // 是否启用夜间休息
    val nightRestStartHour: Int = 22,           // 夜间休息开始时间（小时）
    val nightRestStartMinute: Int = 30,         // 夜间休息开始时间（分钟）
    val nightRestEndHour: Int = 7,              // 夜间休息结束时间（小时）
    val nightRestEndMinute: Int = 0,            // 夜间休息结束时间（分钟）
    
    // 休息方式
    val forceScreenOff: Boolean = false,        // 是否强制息屏
    
    // 解锁选项
    val allowUnlock: Boolean = true,            // 是否允许解锁
    val unlockEscCount: Int = 5,                // ESC解锁次数
    
    // 语言设置
    val language: String = "zh",                // 语言代码
    
    // 服务状态
    val serviceEnabled: Boolean = false,        // 服务是否启用
    val lastWorkStartTime: Long = 0L            // 上次工作开始时间
)

/**
 * 配置管理器
 */
class ConfigManager(context: Context) {
    private val sharedPreferences: SharedPreferences = 
        context.getSharedPreferences("VitalityGuardPrefs", Context.MODE_PRIVATE)
    
    private val json = Json { 
        ignoreUnknownKeys = true
        encodeDefaults = true
    }
    
    /**
     * 保存配置
     */
    fun saveConfig(config: VitalityConfig) {
        val configJson = json.encodeToString(config)
        sharedPreferences.edit()
            .putString("config", configJson)
            .apply()
    }
    
    /**
     * 加载配置
     */
    fun loadConfig(): VitalityConfig {
        val configJson = sharedPreferences.getString("config", null)
        return if (configJson != null) {
            try {
                json.decodeFromString<VitalityConfig>(configJson)
            } catch (e: Exception) {
                VitalityConfig()
            }
        } else {
            VitalityConfig()
        }
    }
    
    /**
     * 更新服务启用状态
     */
    fun updateServiceEnabled(enabled: Boolean) {
        val config = loadConfig()
        saveConfig(config.copy(serviceEnabled = enabled))
    }
    
    /**
     * 更新工作开始时间
     */
    fun updateWorkStartTime(time: Long) {
        val config = loadConfig()
        saveConfig(config.copy(lastWorkStartTime = time))
    }
    
    /**
     * 重置为默认配置
     */
    fun resetToDefault(): VitalityConfig {
        val defaultConfig = VitalityConfig()
        saveConfig(defaultConfig)
        return defaultConfig
    }
}