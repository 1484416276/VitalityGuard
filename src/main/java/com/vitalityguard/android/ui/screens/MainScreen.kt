package com.vitalityguard.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.vitalityguard.android.data.VitalityConfig
import com.vitalityguard.android.service.VitalityGuardService
import com.vitalityguard.android.ui.theme.*

/**
 * 主界面屏幕
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    config: VitalityConfig,
    serviceState: VitalityGuardService.ServiceState,
    onConfigChange: (VitalityConfig) -> Unit,
    onStartService: () -> Unit,
    onStopService: () -> Unit,
    onNavigateToSettings: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        text = "活力卫士",
                        fontWeight = FontWeight.Bold
                    ) 
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary
                ),
                actions = {
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(
                            Icons.Default.Settings,
                            contentDescription = "设置",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(32.dp))
            
            // 状态显示区域
            StatusDisplay(
                serviceState = serviceState,
                config = config,
                modifier = Modifier.padding(horizontal = 24.dp)
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // 控制按钮区域
            ControlButtons(
                isServiceRunning = config.serviceEnabled,
                onStart = onStartService,
                onStop = onStopService,
                modifier = Modifier.padding(horizontal = 24.dp)
            )
            
            Spacer(modifier = Modifier.height(32.dp))
            
            // 快速设置卡片
            QuickSettingsCard(
                config = config,
                onConfigChange = onConfigChange,
                modifier = Modifier.padding(horizontal = 24.dp)
            )
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // 健康提示
            HealthTipsCard(
                modifier = Modifier.padding(horizontal = 24.dp)
            )
            
            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}

@Composable
fun StatusDisplay(
    serviceState: VitalityGuardService.ServiceState,
    config: VitalityConfig,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = when (serviceState) {
                is VitalityGuardService.ServiceState.Working -> SuccessGreen.copy(alpha = 0.1f)
                is VitalityGuardService.ServiceState.Resting -> WarningYellow.copy(alpha = 0.1f)
                is VitalityGuardService.ServiceState.NightRest -> Color(0xFF1A237E).copy(alpha = 0.1f)
                is VitalityGuardService.ServiceState.Paused -> Orange80.copy(alpha = 0.1f)
                is VitalityGuardService.ServiceState.Idle -> MaterialTheme.colorScheme.surfaceVariant
            }
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 状态图标
            Box(
                modifier = Modifier
                    .size(120.dp)
                    .clip(CircleShape)
                    .background(
                        when (serviceState) {
                            is VitalityGuardService.ServiceState.Working -> SuccessGreen
                            is VitalityGuardService.ServiceState.Resting -> WarningYellow
                            is VitalityGuardService.ServiceState.NightRest -> Color(0xFF1A237E)
                            is VitalityGuardService.ServiceState.Paused -> Orange80
                            is VitalityGuardService.ServiceState.Idle -> MaterialTheme.colorScheme.outline
                        }
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = when (serviceState) {
                        is VitalityGuardService.ServiceState.Working -> Icons.Default.Build
                        is VitalityGuardService.ServiceState.Resting -> Icons.Default.Face
                        is VitalityGuardService.ServiceState.NightRest -> Icons.Default.Home
                        is VitalityGuardService.ServiceState.Paused -> Icons.Default.Info
                        is VitalityGuardService.ServiceState.Idle -> Icons.Default.PlayArrow
                    },
                    contentDescription = null,
                    modifier = Modifier.size(60.dp),
                    tint = Color.White
                )
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 状态文字
            Text(
                text = when (serviceState) {
                    is VitalityGuardService.ServiceState.Working -> "工作中"
                    is VitalityGuardService.ServiceState.Resting -> "休息中"
                    is VitalityGuardService.ServiceState.NightRest -> "夜间休息"
                    is VitalityGuardService.ServiceState.Paused -> "已暂停"
                    is VitalityGuardService.ServiceState.Idle -> "未启动"
                },
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            
            // 倒计时显示
            when (serviceState) {
                is VitalityGuardService.ServiceState.Working -> {
                    CountdownDisplay(
                        remainingSeconds = serviceState.remainingSeconds,
                        totalSeconds = serviceState.totalSeconds,
                        label = "工作剩余时间"
                    )
                }
                is VitalityGuardService.ServiceState.Resting -> {
                    CountdownDisplay(
                        remainingSeconds = serviceState.remainingSeconds,
                        totalSeconds = serviceState.totalSeconds,
                        label = "休息剩余时间"
                    )
                }
                is VitalityGuardService.ServiceState.NightRest -> {
                    Text(
                        text = "夜间休息模式已开启",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                is VitalityGuardService.ServiceState.Paused -> {
                    Text(
                        text = "监控已暂停",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                is VitalityGuardService.ServiceState.Idle -> {
                    Text(
                        text = "点击下方按钮启动监控",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
fun CountdownDisplay(
    remainingSeconds: Long,
    totalSeconds: Long,
    label: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = label,
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // 进度条
        LinearProgressIndicator(
            progress = { (remainingSeconds.toFloat() / totalSeconds).coerceIn(0f, 1f) },
            modifier = Modifier
                .fillMaxWidth(0.8f)
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp)),
            color = MaterialTheme.colorScheme.primary,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        // 时间显示
        val hours = remainingSeconds / 3600
        val minutes = (remainingSeconds % 3600) / 60
        val seconds = remainingSeconds % 60
        
        Text(
            text = if (hours > 0) {
                String.format("%02d:%02d:%02d", hours, minutes, seconds)
            } else {
                String.format("%02d:%02d", minutes, seconds)
            },
            fontSize = 36.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
    }
}

@Composable
fun ControlButtons(
    isServiceRunning: Boolean,
    onStart: () -> Unit,
    onStop: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        if (isServiceRunning) {
            // 停止按钮
            Button(
                onClick = onStop,
                modifier = Modifier
                    .weight(1f)
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = ErrorRed
                ),
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(
                    Icons.Default.Close,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("停止监控", fontSize = 16.sp)
            }
        } else {
            // 启动按钮
            Button(
                onClick = onStart,
                modifier = Modifier
                    .weight(1f)
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = SuccessGreen
                ),
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(
                    Icons.Default.PlayArrow,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("启动监控", fontSize = 16.sp)
            }
        }
    }
}

@Composable
fun QuickSettingsCard(
    config: VitalityConfig,
    onConfigChange: (VitalityConfig) -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "快速设置",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 工作时长滑块
            SettingSlider(
                label = "工作时长",
                value = config.workDurationMinutes,
                range = 15f..120f,
                unit = "分钟",
                onValueChange = { newValue ->
                    onConfigChange(config.copy(workDurationMinutes = newValue.toInt()))
                }
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 休息时长滑块
            SettingSlider(
                label = "休息时长",
                value = config.restDurationMinutes,
                range = 1f..30f,
                unit = "分钟",
                onValueChange = { newValue ->
                    onConfigChange(config.copy(restDurationMinutes = newValue.toInt()))
                }
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // 夜间休息开关
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Home,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("夜间休息模式")
                }
                Switch(
                    checked = config.nightRestEnabled,
                    onCheckedChange = { enabled ->
                        onConfigChange(config.copy(nightRestEnabled = enabled))
                    }
                )
            }
        }
    }
}

@Composable
fun SettingSlider(
    label: String,
    value: Int,
    range: ClosedFloatingPointRange<Float>,
    unit: String,
    onValueChange: (Float) -> Unit
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(label)
            Text(
                text = "$value $unit",
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
        }
        Slider(
            value = value.toFloat(),
            onValueChange = onValueChange,
            valueRange = range,
            steps = ((range.endInclusive - range.start) / 5).toInt() - 1
        )
    }
}

@Composable
fun HealthTipsCard(
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = VitalityGreenLight.copy(alpha = 0.2f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.Favorite,
                    contentDescription = null,
                    tint = ErrorRed
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "健康小贴士",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "• 每工作45-60分钟，休息5-10分钟\n" +
                       "• 保持正确的坐姿，屏幕与眼睛保持50-70cm距离\n" +
                       "• 定时做眼保健操，眺望远处放松眼睛\n" +
                       "• 保证充足的睡眠，建议晚上11点前入睡",
                fontSize = 14.sp,
                lineHeight = 22.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
        }
    }
}