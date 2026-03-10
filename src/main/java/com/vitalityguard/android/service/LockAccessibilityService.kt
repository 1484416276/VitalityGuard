package com.vitalityguard.android.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

/**
 * 无障碍服务 - 用于拦截系统按键
 * 允许电话、通知等系统功能正常使用
 */
class LockAccessibilityService : AccessibilityService() {
    
    companion object {
        private const val TAG = "LockAccessibilityService"
        private var instance: LockAccessibilityService? = null
        private var isLocked = false
        private val handler = Handler(Looper.getMainLooper())
        
        // 允许在锁屏时使用的应用包名（电话、通知、通讯软件等）
        private val ALLOWED_PACKAGES = setOf(
            // 电话相关
            "com.android.phone",           // 电话
            "com.android.incallui",        // 来电界面
            "com.samsung.android.incallui", // 三星来电
            "com.huawei.android.incallui",  // 华为来电
            "com.miui.phone",               // 小米电话
            "com.coloros.phone",            // OPPO电话
            "com.vivo.contact",             // vivo电话
            "com.oplus.phone",              // OnePlus电话
            // 系统UI（通知栏、快速设置等）
            "com.android.systemui",         // 系统UI（通知栏）
            "com.android.launcher",         // 启动器
            "com.android.launcher3",
            "com.huawei.android.launcher",
            "com.miui.home",
            "com.android.settings",         // 设置
            // 通讯软件
            "com.tencent.mm",               // 微信
            "com.tencent.mobileqq",         // QQ
            "com.immomo.momo",              // 陌陌
            "com.sina.weibo",               // 微博
            "com.alibaba.android.rimet",    // 钉钉
            "com.alibaba.wireless",         // 阿里旺旺
            "com.ss.android.lark",          // 飞书/Lark
            "cn.wps.moffice",               // WPS
            // 本应用
            "com.vitalityguard.android"     // 本应用
        )
        
        fun getInstance(): LockAccessibilityService? = instance
        
        fun isServiceEnabled(): Boolean = instance != null
        
        fun setLocked(locked: Boolean) {
            isLocked = locked
            instance?.updateServiceInfo()
            Log.d(TAG, "锁定状态更新: $locked")
        }
        
        fun isCurrentlyLocked(): Boolean = isLocked
        
        /**
         * 检查无障碍服务是否已启用
         */
        fun isAccessibilityServiceEnabled(context: Context): Boolean {
            val service = "${context.packageName}/${LockAccessibilityService::class.java.canonicalName}"
            var accessibilityEnabled = 0
            try {
                accessibilityEnabled = android.provider.Settings.Secure.getInt(
                    context.contentResolver,
                    android.provider.Settings.Secure.ACCESSIBILITY_ENABLED
                )
            } catch (e: Exception) {
                Log.e(TAG, "获取无障碍服务状态失败", e)
            }
            
            if (accessibilityEnabled == 1) {
                val settingValue = android.provider.Settings.Secure.getString(
                    context.contentResolver,
                    android.provider.Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
                )
                return settingValue?.contains(service) == true
            }
            return false
        }
        
        /**
         * 打开无障碍服务设置页面
         */
        fun openAccessibilitySettings(context: Context) {
            val intent = Intent(android.provider.Settings.ACTION_ACCESSIBILITY_SETTINGS).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
        }
    }
    
    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
        Log.d(TAG, "无障碍服务已连接")
        updateServiceInfo()
    }
    
    private fun updateServiceInfo() {
        val info = AccessibilityServiceInfo().apply {
            // 只监听按键和窗口切换事件
            eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
            // 提供按键过滤能力
            flags = AccessibilityServiceInfo.FLAG_REQUEST_FILTER_KEY_EVENTS or
                    AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
            
            // 监听所有包
            packageNames = null
            // 反馈类型
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            // 通知超时
            notificationTimeout = 100
        }
        serviceInfo = info
        Log.d(TAG, "无障碍服务配置已更新, 锁定状态: $isLocked")
    }
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (!isLocked) return
        
        event?.let {
            when (it.eventType) {
                AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                    val packageName = it.packageName?.toString() ?: ""
                    
                    // 允许的系统应用直接放行
                    if (packageName in ALLOWED_PACKAGES) {
                        Log.d(TAG, "允许系统应用: $packageName")
                        return
                    }
                    
                    // 检查是否是电话相关应用（包含call关键字）
                    if (packageName.contains("call", ignoreCase = true) ||
                        packageName.contains("phone", ignoreCase = true)) {
                        Log.d(TAG, "允许电话应用: $packageName")
                        return
                    }
                    
                    // 检查是否是通讯软件（微信、QQ等）
                    if (packageName.contains("tencent", ignoreCase = true) ||
                        packageName.contains("mm", ignoreCase = true) ||
                        packageName.contains("mqq", ignoreCase = true) ||
                        packageName.contains("im", ignoreCase = true) ||
                        packageName.contains("chat", ignoreCase = true) ||
                        packageName.contains("message", ignoreCase = true)) {
                        Log.d(TAG, "允许通讯应用: $packageName")
                        return
                    }
                    
                    // 其他应用，延迟一下再检查是否需要回到锁屏
                    handler.postDelayed({
                        val currentPackage = getCurrentActivityPackage()
                        if (currentPackage !in ALLOWED_PACKAGES && 
                            !currentPackage.contains("call", ignoreCase = true) &&
                            !currentPackage.contains("phone", ignoreCase = true) &&
                            !currentPackage.contains("tencent", ignoreCase = true) &&
                            !currentPackage.contains("mm", ignoreCase = true) &&
                            !currentPackage.contains("mqq", ignoreCase = true) &&
                            !currentPackage.contains("im", ignoreCase = true) &&
                            !currentPackage.contains("chat", ignoreCase = true) &&
                            !currentPackage.contains("message", ignoreCase = true)) {
                            Log.d(TAG, "检测到切换到其他应用: $currentPackage，返回锁屏")
                            performGlobalAction(GLOBAL_ACTION_HOME)
                            handler.postDelayed({
                                restartLockScreenActivity()
                            }, 300)
                        }
                    }, 500)
                }
                else -> {
                    // 其他事件类型不处理
                }
            }
        }
    }
    
    /**
     * 获取当前顶层Activity的包名
     */
    private fun getCurrentActivityPackage(): String {
        return try {
            val rootNode = rootInActiveWindow
            rootNode?.packageName?.toString() ?: ""
        } catch (e: Exception) {
            ""
        }
    }
    
    override fun onInterrupt() {
        Log.d(TAG, "无障碍服务被中断")
    }
    
    override fun onKeyEvent(event: android.view.KeyEvent?): Boolean {
        if (!isLocked) return super.onKeyEvent(event)
        
        event?.let { evt ->
            Log.d(TAG, "按键事件: ${evt.keyCode}, 动作: ${evt.action}")
            
            val keyCode = evt.keyCode
            
            // Home键 - 拦截但不阻止，记录后重启锁屏
            if (keyCode == android.view.KeyEvent.KEYCODE_HOME) {
                Log.d(TAG, "Home键按下")
                if (evt.action == android.view.KeyEvent.ACTION_UP) {
                    handler.postDelayed({
                        restartLockScreenActivity()
                    }, 500)
                }
                return false  // 不拦截，让系统处理
            }
            
            // 最近任务键 - 拦截
            if (keyCode == android.view.KeyEvent.KEYCODE_APP_SWITCH || 
                keyCode == android.view.KeyEvent.KEYCODE_RECENT_APPS) {
                Log.d(TAG, "拦截最近任务键")
                return true
            }
            
            // 返回键 - 用于紧急解锁
            if (keyCode == android.view.KeyEvent.KEYCODE_BACK) {
                if (evt.action == android.view.KeyEvent.ACTION_DOWN) {
                    handleBackPress()
                }
                return true
            }
            
            // 音量键 - 允许
            if (keyCode == android.view.KeyEvent.KEYCODE_VOLUME_UP ||
                keyCode == android.view.KeyEvent.KEYCODE_VOLUME_DOWN ||
                keyCode == android.view.KeyEvent.KEYCODE_VOLUME_MUTE) {
                return false
            }
            
            // 电源键 - 允许
            if (keyCode == android.view.KeyEvent.KEYCODE_POWER) {
                Log.d(TAG, "电源键按下")
                return false
            }
            
            // 拨号键 - 允许
            if (keyCode == android.view.KeyEvent.KEYCODE_CALL) {
                return false
            }
            
            // 挂断键 - 允许
            if (keyCode == android.view.KeyEvent.KEYCODE_ENDCALL) {
                return false
            }
            
            // 菜单键 - 拦截
            if (keyCode == android.view.KeyEvent.KEYCODE_MENU) {
                return true
            }
            
            // 搜索键 - 拦截
            if (keyCode == android.view.KeyEvent.KEYCODE_SEARCH) {
                return true
            }
            
            // 其他按键使用默认处理
            return super.onKeyEvent(event)
        }
        
        return super.onKeyEvent(event)
    }
    
    private var backPressCount = 0
    private var lastBackPressTime = 0L
    private val BACK_PRESS_THRESHOLD = 5
    private val BACK_PRESS_TIMEOUT = 3000L
    
    private fun handleBackPress() {
        val currentTime = System.currentTimeMillis()
        
        // 检查是否在超时时间内
        if (currentTime - lastBackPressTime > BACK_PRESS_TIMEOUT) {
            backPressCount = 0
        }
        
        backPressCount++
        lastBackPressTime = currentTime
        
        Log.d(TAG, "返回键计数: $backPressCount/$BACK_PRESS_THRESHOLD")
        
        // 通知Service处理解锁
        if (backPressCount >= BACK_PRESS_THRESHOLD) {
            Log.d(TAG, "达到解锁阈值，尝试解锁")
            VitalityGuardService.handleBackPress(this)
            backPressCount = 0
        }
    }
    
    /**
     * 重启锁屏Activity
     */
    private fun restartLockScreenActivity() {
        try {
            val intent = Intent(this, Class.forName("com.vitalityguard.android.MainActivity")).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
                addFlags(Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS)
                putExtra("show_lock_screen", true)
                putExtra("force_lock", true)
            }
            startActivity(intent)
            Log.d(TAG, "已重启锁屏Activity")
        } catch (e: Exception) {
            Log.e(TAG, "重启锁屏Activity失败", e)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
        Log.d(TAG, "无障碍服务已销毁")
    }
    
    /**
     * 强制返回桌面
     */
    fun forceGoHome() {
        performGlobalAction(GLOBAL_ACTION_HOME)
    }
    
    /**
     * 强制返回
     */
    fun forceGoBack() {
        performGlobalAction(GLOBAL_ACTION_BACK)
    }
    
    /**
     * 强制打开最近任务
     */
    fun forceOpenRecents() {
        performGlobalAction(GLOBAL_ACTION_RECENTS)
    }
    
    /**
     * 强制打开通知栏
     */
    fun forceOpenNotifications() {
        performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
    }
    
    /**
     * 强制打开快速设置
     */
    fun forceOpenQuickSettings() {
        performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS)
    }
    
    /**
     * 强制锁定屏幕
     */
    fun forceLockScreen() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN)
        }
    }
    
    /**
     * 截图
     */
    fun takeScreenshot() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            performGlobalAction(GLOBAL_ACTION_TAKE_SCREENSHOT)
        }
    }
}