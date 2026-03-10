package com.vitalityguard.android.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import androidx.core.app.NotificationCompat
import com.vitalityguard.android.MainActivity
import com.vitalityguard.android.R
import com.vitalityguard.android.data.ConfigManager
import com.vitalityguard.android.data.VitalityConfig
import kotlinx.coroutines.*
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.Calendar

/**
 * 活力卫士后台服务
 * 负责监控工作/休息周期和夜间休息模式
 * 支持Root权限强制锁屏
 */
class VitalityGuardService : Service() {
    
    companion object {
        const val TAG = "VitalityGuardService"
        const val CHANNEL_ID = "vitality_guard_channel"
        const val NOTIFICATION_ID = 1001
        
        // Actions
        const val ACTION_START = "com.vitalityguard.android.START"
        const val ACTION_STOP = "com.vitalityguard.android.STOP"
        const val ACTION_PAUSE = "com.vitalityguard.android.PAUSE"
        const val ACTION_RESUME = "com.vitalityguard.android.RESUME"
        const val ACTION_UNLOCK = "com.vitalityguard.android.UNLOCK"
        const val ACTION_EMERGENCY_UNLOCK = "com.vitalityguard.android.EMERGENCY_UNLOCK"
        const val ACTION_UPDATE_CONFIG = "com.vitalityguard.android.UPDATE_CONFIG"
        
        // 状态流
        private val _serviceState = MutableStateFlow<ServiceState>(ServiceState.Idle)
        val serviceState: StateFlow<ServiceState> = _serviceState
        
        // 锁屏状态
        private val _isLocked = MutableStateFlow(false)
        val isLocked: StateFlow<Boolean> = _isLocked
        
        // 解锁计数
        private val _unlockPressCount = MutableStateFlow(0)
        val unlockPressCount: StateFlow<Int> = _unlockPressCount
        
        // 是否有Root权限
        private val _hasRootPermission = MutableStateFlow(false)
        val hasRootPermission: StateFlow<Boolean> = _hasRootPermission
        
        // 当前模式是否为夜间模式
        private var isNightMode = false
        
        // 解锁计数器（内部使用）
        private var unlockPressCounter = 0
        private val UNLOCK_PRESS_THRESHOLD = 5
        private var lastUnlockPressTime = 0L
        private val UNLOCK_PRESS_TIMEOUT = 3000L // 3秒内按5次
        
        fun start(context: Context) {
            val intent = Intent(context, VitalityGuardService::class.java).apply {
                action = ACTION_START
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
        
        fun stop(context: Context) {
            val intent = Intent(context, VitalityGuardService::class.java).apply {
                action = ACTION_STOP
            }
            context.startService(intent)
        }
        
        fun emergencyUnlock(context: Context) {
            val intent = Intent(context, VitalityGuardService::class.java).apply {
                action = ACTION_EMERGENCY_UNLOCK
            }
            context.startService(intent)
        }
        
        /**
         * 热更新配置（无需重启服务）
         */
        fun updateConfig(context: Context) {
            val intent = Intent(context, VitalityGuardService::class.java).apply {
                action = ACTION_UPDATE_CONFIG
            }
            context.startService(intent)
        }
        
        /**
         * 处理返回键按下（从无障碍服务调用）
         */
        fun handleBackPress(context: Context) {
            Log.d(TAG, "handleBackPress 被调用")
            val currentTime = System.currentTimeMillis()
            
            // 检查是否在超时时间内
            if (currentTime - lastUnlockPressTime > UNLOCK_PRESS_TIMEOUT) {
                unlockPressCounter = 0
            }
            
            unlockPressCounter++
            lastUnlockPressTime = currentTime
            _unlockPressCount.value = unlockPressCounter
            
            Log.d(TAG, "解锁按键计数: $unlockPressCounter/$UNLOCK_PRESS_THRESHOLD")
            
            // 检查是否达到解锁阈值
            if (unlockPressCounter >= UNLOCK_PRESS_THRESHOLD) {
                // 夜间模式不允许解锁
                if (isNightMode) {
                    Log.d(TAG, "夜间模式不允许解锁")
                    unlockPressCounter = 0
                    _unlockPressCount.value = 0
                    return
                }
                
                // 发送紧急解锁Intent
                emergencyUnlock(context)
            }
        }
    }
    
    // 服务状态
    sealed class ServiceState {
        object Idle : ServiceState()
        data class Working(val remainingSeconds: Long, val totalSeconds: Long) : ServiceState()
        data class Resting(val remainingSeconds: Long, val totalSeconds: Long, val isLocked: Boolean) : ServiceState()
        data class NightRest(val remainingSeconds: Long, val isLocked: Boolean) : ServiceState()
        object Paused : ServiceState()
    }
    
    private lateinit var configManager: ConfigManager
    private var config: VitalityConfig = VitalityConfig()
    private var serviceJob: Job? = null
    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    // WakeLock保持CPU运行（熄屏时计时器不暂停）
    private var wakeLock: PowerManager.WakeLock? = null
    
    private var isWorking = true
    private var remainingSeconds = 0L
    private var totalSeconds = 0L
    private var isCurrentlyLocked = false
    
    override fun onCreate() {
        super.onCreate()
        configManager = ConfigManager(applicationContext)
        config = configManager.loadConfig()
        createNotificationChannel()
        
        // 检查Root权限
        checkRootPermission()
    }
    
    private fun checkRootPermission() {
        serviceScope.launch {
            val hasRoot = RootLockManager.checkRootPermission()
            _hasRootPermission.value = hasRoot
            Log.d(TAG, "Root权限: $hasRoot")
        }
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startMonitoring()
            ACTION_STOP -> stopMonitoring()
            ACTION_PAUSE -> pauseMonitoring()
            ACTION_RESUME -> resumeMonitoring()
            ACTION_UNLOCK -> handleUnlockPress()
            ACTION_EMERGENCY_UNLOCK -> emergencyUnlock()
            ACTION_UPDATE_CONFIG -> reloadConfig()
        }
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "活力卫士",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "工作/休息周期提醒服务"
            }
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(title: String, content: String): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(content)
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build()
    }
    
    private fun startMonitoring() {
        config = configManager.loadConfig()
        
        // 获取WakeLock，保持CPU运行（熄屏时计时器不暂停）
        acquireWakeLock()
        
        // 启动前台服务
        startForeground(NOTIFICATION_ID, createNotification("活力卫士运行中", "正在监控工作周期"))
        
        // 检查是否在夜间休息时段
        if (config.nightRestEnabled && isInNightRestPeriod()) {
            startNightRest()
            return
        }
        
        // 开始工作周期
        startWorkCycle()
    }
    
    /**
     * 获取WakeLock保持CPU运行
     */
    private fun acquireWakeLock() {
        if (wakeLock == null) {
            val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
            wakeLock = powerManager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "VitalityGuard::TimerWakeLock"
            ).apply {
                acquire(10 * 60 * 60 * 1000L) // 最多10小时，足够长
            }
            Log.d(TAG, "WakeLock已获取")
        }
    }
    
    /**
     * 释放WakeLock
     */
    private fun releaseWakeLock() {
        wakeLock?.let {
            if (it.isHeld) {
                it.release()
                Log.d(TAG, "WakeLock已释放")
            }
        }
        wakeLock = null
    }
    
    private fun startWorkCycle() {
        Log.d(TAG, "开始工作周期")
        isWorking = true
        totalSeconds = (config.workDurationMinutes * 60).toLong()
        remainingSeconds = totalSeconds
        configManager.updateWorkStartTime(System.currentTimeMillis())
        
        // 确保解锁
        if (isCurrentlyLocked) {
            unlockDevice()
        }
        
        // 立即更新状态为工作状态
        _serviceState.value = ServiceState.Working(remainingSeconds, totalSeconds)
        updateNotification("工作中", formatTime(remainingSeconds))
        
        // 不再取消之前的 job，而是让新协程直接运行
        serviceJob = serviceScope.launch {
            try {
                while (remainingSeconds > 0 && isActive) {
                    // 检查夜间休息
                    if (config.nightRestEnabled && isInNightRestPeriod()) {
                        withContext(NonCancellable) {
                            startNightRest()
                        }
                        return@launch
                    }
                    
                    _serviceState.value = ServiceState.Working(remainingSeconds, totalSeconds)
                    updateNotification("工作中", formatTime(remainingSeconds))
                    delay(1000)
                    remainingSeconds--
                }
                
                // 工作结束，开始休息
                if (isActive) {
                    startRestCycle()
                }
            } catch (e: CancellationException) {
                Log.d(TAG, "工作周期被取消")
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "工作周期异常: ${e.message}", e)
            }
        }
    }
    
    private fun startRestCycle() {
        Log.d(TAG, "开始休息周期")
        isWorking = false
        totalSeconds = (config.restDurationMinutes * 60).toLong()
        remainingSeconds = totalSeconds
        
        // 发送休息通知
        sendRestNotification()
        
        // 启动锁屏
        if (_hasRootPermission.value) {
            lockDevice()
        }
        
        // 启动锁屏Activity
        startLockScreenActivity()
        
        serviceJob = serviceScope.launch {
            try {
                while (remainingSeconds > 0 && isActive) {
                    _serviceState.value = ServiceState.Resting(remainingSeconds, totalSeconds, isCurrentlyLocked)
                    updateNotification("休息中", formatTime(remainingSeconds))
                    delay(1000)
                    remainingSeconds--
                    
                    // 检查是否需要保持锁屏状态
                    if (isCurrentlyLocked && _hasRootPermission.value) {
                        keepDeviceLocked()
                    }
                }
                
                // 休息结束，解锁
                unlockDevice()
                
                // 开始新的工作周期
                if (isActive) {
                    startWorkCycle()
                }
            } catch (e: CancellationException) {
                Log.d(TAG, "休息周期被取消")
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "休息周期异常: ${e.message}", e)
            }
        }
    }
    
    private fun startNightRest() {
        Log.d(TAG, "开始夜间休息模式")
        isNightMode = true
        remainingSeconds = calculateNightRestRemainingSeconds()
        
        // 启动锁屏（夜间模式强制锁定）
        if (_hasRootPermission.value) {
            lockDevice()
        }
        
        // 启用无障碍服务拦截
        LockAccessibilityService.setLocked(true)
        
        // 启动锁屏Activity
        startLockScreenActivity(isNight = true)
        
        serviceJob = serviceScope.launch {
            try {
                // 使用 isInNightRestPeriod() 作为循环条件
                while (isInNightRestPeriod() && isActive) {
                    remainingSeconds = calculateNightRestRemainingSeconds()
                    _serviceState.value = ServiceState.NightRest(remainingSeconds, isCurrentlyLocked)
                    updateNotification("夜间休息模式", "请休息，到${config.nightRestEndHour}:${String.format("%02d", config.nightRestEndMinute)}结束")
                    delay(1000)
                    
                    // 保持锁屏状态
                    if (isCurrentlyLocked && _hasRootPermission.value) {
                        keepDeviceLocked()
                    }
                }
                
                Log.d(TAG, "夜间休息结束，准备开始工作周期")
                
                // 夜间休息结束，解锁
                isNightMode = false
                unlockDevice()
                
                // 等待一小段时间确保解锁完成
                delay(200)
                
                // 开始工作周期
                if (isActive) {
                    withContext(NonCancellable) {
                        Log.d(TAG, "启动工作周期")
                        startWorkCycle()
                    }
                }
            } catch (e: CancellationException) {
                Log.d(TAG, "夜间休息被取消")
                isNightMode = false
                unlockDevice()
                throw e
            } catch (e: Exception) {
                Log.e(TAG, "夜间休息模式异常: ${e.message}", e)
                // 确保解锁
                isNightMode = false
                unlockDevice()
            }
        }
    }
    
    private fun lockDevice() {
        Log.d(TAG, "锁定设备...")
        isCurrentlyLocked = true
        _isLocked.value = true
        
        // 启用无障碍服务拦截
        LockAccessibilityService.setLocked(true)
        
        if (_hasRootPermission.value) {
            // 使用Root权限锁定
            RootLockManager.apply {
                lockDevice()
                disableStatusBar()
                disablePowerMenu()
                keepScreenOn(true)
            }
        }
        
        Log.d(TAG, "设备已锁定")
    }
    
    private fun unlockDevice() {
        Log.d(TAG, "解锁设备...")
        isCurrentlyLocked = false
        _isLocked.value = false
        unlockPressCounter = 0
        _unlockPressCount.value = 0
        
        // 禁用无障碍服务拦截
        LockAccessibilityService.setLocked(false)
        
        if (_hasRootPermission.value) {
            // 使用Root权限解锁
            RootLockManager.apply {
                unlockDevice()
                enableStatusBar()
                enablePowerMenu()
                keepScreenOn(false)
            }
        }
        
        Log.d(TAG, "设备已解锁")
    }
    
    private fun keepDeviceLocked() {
        // 定期检查并保持锁屏状态
        if (_hasRootPermission.value && isCurrentlyLocked) {
            // 可以在这里添加额外的锁定检查
        }
    }
    
    private fun startLockScreenActivity(isNight: Boolean = false) {
        val intent = Intent(this, MainActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
            putExtra("show_lock_screen", true)
            putExtra("is_night_rest", isNight)
            putExtra("remaining_seconds", remainingSeconds)
        }
        startActivity(intent)
    }
    
    private fun handleUnlockPress() {
        val currentTime = System.currentTimeMillis()
        
        // 检查是否在超时时间内
        if (currentTime - lastUnlockPressTime > UNLOCK_PRESS_TIMEOUT) {
            unlockPressCounter = 0
        }
        
        unlockPressCounter++
        lastUnlockPressTime = currentTime
        _unlockPressCount.value = unlockPressCounter
        
        Log.d(TAG, "解锁按键计数: $unlockPressCounter/$UNLOCK_PRESS_THRESHOLD")
        
        // 检查是否达到解锁阈值
        if (unlockPressCounter >= UNLOCK_PRESS_THRESHOLD && config.allowUnlock) {
            emergencyUnlock()
        }
    }
    
    private fun emergencyUnlock() {
        Log.d(TAG, "紧急解锁!")
        
        // 只有在休息模式下才能解锁
        val currentState = _serviceState.value
        if (currentState is ServiceState.Resting || currentState is ServiceState.NightRest) {
            // 夜间模式不允许解锁
            if (currentState is ServiceState.NightRest) {
                Log.d(TAG, "夜间模式不允许解锁")
                return
            }
            
            // 解锁
            unlockDevice()
            
            // 重置解锁计数
            unlockPressCounter = 0
            _unlockPressCount.value = 0
            
            // 发送解锁通知
            sendUnlockNotification()
        }
    }
    
    private fun stopMonitoring() {
        // 解锁设备
        unlockDevice()
        
        // 释放WakeLock
        releaseWakeLock()
        
        serviceJob?.cancel()
        serviceJob = null
        _serviceState.value = ServiceState.Idle
        configManager.updateServiceEnabled(false)
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }
    
    private fun pauseMonitoring() {
        // 暂停时解锁
        unlockDevice()
        
        serviceJob?.cancel()
        _serviceState.value = ServiceState.Paused
        updateNotification("已暂停", "点击恢复继续监控")
    }
    
    private fun resumeMonitoring() {
        if (isWorking) {
            startWorkCycle()
        } else {
            startRestCycle()
        }
    }
    
    /**
     * 热更新配置
     * 服务运行时更新配置，立即生效
     */
    private fun reloadConfig() {
        Log.d(TAG, "热更新配置...")
        val oldConfig = config
        config = configManager.loadConfig()
        
        // 更新 allowUnlock 状态
        // 夜间模式相关配置会在下一个循环周期自动生效
        
        Log.d(TAG, "配置已更新: 工作时长=${config.workDurationMinutes}分钟, 休息时长=${config.restDurationMinutes}分钟")
        
        // 如果当前在工作周期，更新剩余时间（如果工作时间变化了）
        val currentState = _serviceState.value
        if (currentState is ServiceState.Working) {
            // 重新计算剩余时间
            val newTotalSeconds = (config.workDurationMinutes * 60).toLong()
            // 保持进度比例
            val progress = remainingSeconds.toDouble() / (oldConfig.workDurationMinutes * 60).coerceAtLeast(1)
            remainingSeconds = (newTotalSeconds * progress).toLong().coerceAtLeast(1)
            totalSeconds = newTotalSeconds
            _serviceState.value = ServiceState.Working(remainingSeconds, totalSeconds)
            updateNotification("工作中", formatTime(remainingSeconds))
        }
    }
    
    private fun isInNightRestPeriod(): Boolean {
        val calendar = Calendar.getInstance()
        val currentHour = calendar.get(Calendar.HOUR_OF_DAY)
        val currentMinute = calendar.get(Calendar.MINUTE)
        val currentTotal = currentHour * 60 + currentMinute
        
        val startTotal = config.nightRestStartHour * 60 + config.nightRestStartMinute
        val endTotal = config.nightRestEndHour * 60 + config.nightRestEndMinute
        
        return if (startTotal > endTotal) {
            // 跨午夜的情况（如 22:30 - 07:00）
            currentTotal >= startTotal || currentTotal < endTotal
        } else {
            // 同一天内
            currentTotal >= startTotal && currentTotal < endTotal
        }
    }
    
    private fun calculateNightRestRemainingSeconds(): Long {
        val calendar = Calendar.getInstance()
        val currentHour = calendar.get(Calendar.HOUR_OF_DAY)
        val currentMinute = calendar.get(Calendar.MINUTE)
        val currentSecond = calendar.get(Calendar.SECOND)
        
        var endHour = config.nightRestEndHour
        var endMinute = config.nightRestEndMinute
        
        // 如果结束时间在当前时间之前，说明是第二天
        if (endHour < currentHour || (endHour == currentHour && endMinute <= currentMinute)) {
            // 结束时间是第二天
            val endCalendar = Calendar.getInstance().apply {
                add(Calendar.DAY_OF_MONTH, 1)
                set(Calendar.HOUR_OF_DAY, endHour)
                set(Calendar.MINUTE, endMinute)
                set(Calendar.SECOND, 0)
            }
            return (endCalendar.timeInMillis - System.currentTimeMillis()) / 1000
        } else {
            // 结束时间是今天
            val remainingHours = endHour - currentHour
            val remainingMinutes = endMinute - currentMinute
            return (remainingHours * 3600 + remainingMinutes * 60 - currentSecond).toLong()
        }
    }
    
    private fun updateNotification(title: String, content: String) {
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, createNotification(title, content))
    }
    
    private fun sendRestNotification() {
        val notificationManager = getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("休息时间到！")
            .setContentText("您已连续工作${config.workDurationMinutes}分钟，请休息${config.restDurationMinutes}分钟")
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .build()
        notificationManager.notify(NOTIFICATION_ID + 1, notification)
    }
    
    private fun sendUnlockNotification() {
        val notificationManager = getSystemService(NotificationManager::class.java)
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("紧急解锁")
            .setContentText("已通过紧急解锁方式解锁")
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .build()
        notificationManager.notify(NOTIFICATION_ID + 2, notification)
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
    
    override fun onDestroy() {
        super.onDestroy()
        // 确保解锁
        unlockDevice()
        // 释放WakeLock
        releaseWakeLock()
        RootLockManager.cleanup()
        serviceJob?.cancel()
        serviceScope.cancel()
    }
}