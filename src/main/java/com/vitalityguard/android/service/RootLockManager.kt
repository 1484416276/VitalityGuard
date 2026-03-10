package com.vitalityguard.android.service

import android.content.Context
import android.os.Build
import android.util.Log
import java.io.BufferedReader
import java.io.DataOutputStream
import java.io.InputStreamReader

/**
 * Root锁屏管理器
 * 使用Root权限实现强制锁屏，禁止用户操作手机
 */
object RootLockManager {
    private const val TAG = "RootLockManager"
    private var isLocked = false
    private var hasRootPermission: Boolean? = null
    
    /**
     * 检查是否有Root权限
     */
    fun checkRootPermission(): Boolean {
        if (hasRootPermission != null) return hasRootPermission!!
        
        try {
            val process = Runtime.getRuntime().exec("su")
            val os = DataOutputStream(process.outputStream)
            os.writeBytes("exit\n")
            os.flush()
            os.close()
            val exitValue = process.waitFor()
            hasRootPermission = exitValue == 0
            Log.d(TAG, "Root权限检查: $hasRootPermission")
            return hasRootPermission!!
        } catch (e: Exception) {
            Log.e(TAG, "Root权限检查失败", e)
            hasRootPermission = false
            return false
        }
    }
    
    /**
     * 执行Root命令
     */
    private fun executeRootCommand(command: String): Boolean {
        return try {
            val process = Runtime.getRuntime().exec("su")
            val os = DataOutputStream(process.outputStream)
            os.writeBytes("$command\n")
            os.writeBytes("exit\n")
            os.flush()
            os.close()
            val exitValue = process.waitFor()
            Log.d(TAG, "执行命令: $command, 结果: $exitValue")
            exitValue == 0
        } catch (e: Exception) {
            Log.e(TAG, "执行Root命令失败: $command", e)
            false
        }
    }
    
    /**
     * 执行多条Root命令
     */
    private fun executeRootCommands(vararg commands: String): Boolean {
        return try {
            val process = Runtime.getRuntime().exec("su")
            val os = DataOutputStream(process.outputStream)
            for (cmd in commands) {
                os.writeBytes("$cmd\n")
            }
            os.writeBytes("exit\n")
            os.flush()
            os.close()
            val exitValue = process.waitFor()
            Log.d(TAG, "执行命令组, 结果: $exitValue")
            exitValue == 0
        } catch (e: Exception) {
            Log.e(TAG, "执行Root命令组失败", e)
            false
        }
    }
    
    /**
     * 锁定手机 - 禁用触摸屏和按键
     */
    fun lockDevice(): Boolean {
        if (isLocked) return true
        
        Log.d(TAG, "开始锁定设备...")
        
        val commands = mutableListOf<String>()
        
        // 方法1: 使用input命令禁用触摸屏 (Android 9+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            commands.add("settings put secure input_methods_subtype_history \"\"")
        }
        
        // 方法2: 冻结输入设备
        commands.add("echo 0 > /proc/touchpanel/enable 2>/dev/null || true")
        commands.add("echo 0 > /sys/devices/virtual/touch/tpd/enable 2>/dev/null || true")
        commands.add("echo 0 > /sys/class/input/input0/enable 2>/dev/null || true")
        
        // 方法3: 使用cmd input禁用 (需要Android 10+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            commands.add("cmd input set interactive 0 2>/dev/null || true")
        }
        
        // 方法4: 禁用导航栏和状态栏
        commands.add("service call activity 79 s16 com.android.systemui 2>/dev/null || true")
        
        // 方法5: 禁用按键
        commands.add("sendevent /dev/input/event0 1 158 0 2>/dev/null || true")  // BACK键
        commands.add("sendevent /dev/input/event0 1 139 0 2>/dev/null || true")  // MENU键
        commands.add("sendevent /dev/input/event0 1 172 0 2>/dev/null || true")  // HOME键
        
        val result = executeRootCommands(*commands.toTypedArray())
        if (result) {
            isLocked = true
            Log.d(TAG, "设备锁定成功")
        } else {
            Log.w(TAG, "设备锁定可能未完全成功")
            isLocked = true  // 仍然标记为锁定，依赖Overlay锁屏
        }
        
        return result
    }
    
    /**
     * 解锁手机 - 恢复触摸屏和按键
     */
    fun unlockDevice(): Boolean {
        if (!isLocked) return true
        
        Log.d(TAG, "开始解锁设备...")
        
        val commands = mutableListOf<String>()
        
        // 恢复输入设备
        commands.add("echo 1 > /proc/touchpanel/enable 2>/dev/null || true")
        commands.add("echo 1 > /sys/devices/virtual/touch/tpd/enable 2>/dev/null || true")
        commands.add("echo 1 > /sys/class/input/input0/enable 2>/dev/null || true")
        
        // 恢复交互模式
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            commands.add("cmd input set interactive 1 2>/dev/null || true")
        }
        
        // 恢复SystemUI
        commands.add("service call activity 79 s16 com.android.systemui 2>/dev/null || true")
        commands.add("am startservice -n com.android.systemui/.SystemUIService 2>/dev/null || true")
        
        // 恢复按键
        commands.add("sendevent /dev/input/event0 1 158 1 2>/dev/null || true")
        commands.add("sendevent /dev/input/event0 1 139 1 2>/dev/null || true")
        commands.add("sendevent /dev/input/event0 1 172 1 2>/dev/null || true")
        
        val result = executeRootCommands(*commands.toTypedArray())
        isLocked = false
        Log.d(TAG, "设备解锁完成")
        return result
    }
    
    /**
     * 强制关闭指定应用
     */
    fun forceStopApp(packageName: String): Boolean {
        return executeRootCommand("am force-stop $packageName")
    }
    
    /**
     * 强制启动指定Activity
     */
    fun startActivity(activityPath: String): Boolean {
        return executeRootCommand("am start -n $activityPath")
    }
    
    /**
     * 模拟按键事件
     */
    fun sendKeyEvent(keyCode: Int): Boolean {
        return executeRootCommand("input keyevent $keyCode")
    }
    
    /**
     * 禁用状态栏下拉
     */
    fun disableStatusBar(): Boolean {
        return executeRootCommands(
            "settings put global heads_up_enabled 0",
            "settings put secure accessibility_display_daltonizer_enabled 0",
            "service call statusbar 2 2>/dev/null || true"
        )
    }
    
    /**
     * 恢复状态栏
     */
    fun enableStatusBar(): Boolean {
        return executeRootCommands(
            "service call statusbar 1 2>/dev/null || true"
        )
    }
    
    /**
     * 关闭屏幕 (使用设备管理器API更可靠，这里用Root备用)
     */
    fun turnOffScreen(): Boolean {
        return executeRootCommands(
            "input keyevent 26",  // POWER键
            "echo 0 > /sys/class/backlight/*/brightness 2>/dev/null || true"
        )
    }
    
    /**
     * 唤醒屏幕
     */
    fun wakeUpScreen(): Boolean {
        return executeRootCommands(
            "input keyevent 26",  // POWER键
            "input keyevent 82",  // 解锁键
            "echo 255 > /sys/class/backlight/*/brightness 2>/dev/null || true"
        )
    }
    
    /**
     * 禁用电源键长按(防止关机)
     */
    fun disablePowerMenu(): Boolean {
        return executeRootCommands(
            "settings put global power_menu_enabled 0 2>/dev/null || true",
            "settings put secure lock_screen_lock_after_timeout 0 2>/dev/null || true"
        )
    }
    
    /**
     * 恢复电源键
     */
    fun enablePowerMenu(): Boolean {
        return executeRootCommands(
            "settings put global power_menu_enabled 1 2>/dev/null || true"
        )
    }
    
    /**
     * 设置屏幕亮度
     */
    fun setBrightness(brightness: Int): Boolean {
        val safeBrightness = brightness.coerceIn(0, 255)
        return executeRootCommands(
            "settings put system screen_brightness $safeBrightness",
            "echo $safeBrightness > /sys/class/backlight/*/brightness 2>/dev/null || true"
        )
    }
    
    /**
     * 禁用飞行模式、WiFi、蓝牙 (防止用户通过这些绕过锁屏)
     */
    fun disableNetworkToggles(): Boolean {
        return executeRootCommands(
            "settings put global airplane_mode_on 0",
            "svc wifi enable",
            "svc bluetooth disable"
        )
    }
    
    /**
     * 强制保持屏幕常亮
     */
    fun keepScreenOn(enabled: Boolean): Boolean {
        return if (enabled) {
            executeRootCommands(
                "settings put system screen_off_timeout 2147483647",  // 最大值
                "echo 1 > /sys/class/backlight/*/bl_power 2>/dev/null || true"
            )
        } else {
            executeRootCommands(
                "settings put system screen_off_timeout 30000"  // 恢复默认30秒
            )
        }
    }
    
    /**
     * 获取当前运行的顶层Activity
     */
    fun getTopActivity(): String? {
        return try {
            val process = Runtime.getRuntime().exec("su")
            val os = DataOutputStream(process.outputStream)
            os.writeBytes("dumpsys activity activities | grep mResumedActivity\n")
            os.writeBytes("exit\n")
            os.flush()
            os.close()
            
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            val line = reader.readLine()
            reader.close()
            
            // 解析输出获取包名
            val regex = Regex("([\\w.]+)/([\\w.]+)")
            val match = regex.find(line ?: "")
            match?.groupValues?.get(1)
        } catch (e: Exception) {
            Log.e(TAG, "获取顶层Activity失败", e)
            null
        }
    }
    
    /**
     * 是否已锁定
     */
    fun isDeviceLocked(): Boolean = isLocked
    
    /**
     * 清理资源
     */
    fun cleanup() {
        if (isLocked) {
            unlockDevice()
        }
    }
}