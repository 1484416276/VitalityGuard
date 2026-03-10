package com.vitalityguard.android.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.vitalityguard.android.data.ConfigManager
import com.vitalityguard.android.service.VitalityGuardService

/**
 * 开机自启动接收器
 */
class BootReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // 检查是否设置了自动启动
            val configManager = ConfigManager(context)
            val config = configManager.loadConfig()
            
            if (config.serviceEnabled) {
                // 启动服务
                VitalityGuardService.start(context)
            }
        }
    }
}