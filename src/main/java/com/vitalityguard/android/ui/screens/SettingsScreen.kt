package com.vitalityguard.android.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.vitalityguard.android.data.VitalityConfig

/**
 * 设置界面
 * 对应原 Python 项目的 settings_gui.py
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    currentConfig: VitalityConfig,
    isServiceRunning: Boolean,
    remainingTime: String,
    onConfigChange: (VitalityConfig) -> Unit,
    onStartService: () -> Unit,
    onStopService: () -> Unit
) {
    var workDuration by remember(currentConfig.workDurationMinutes) {
        mutableStateOf(currentConfig.workDurationMinutes.toString())
    }
    var restDuration by remember(currentConfig.restDurationMinutes) {
        mutableStateOf(currentConfig.restDurationMinutes.toString())
    }
    var countdownSeconds by remember(currentConfig.countdownSeconds) {
        mutableStateOf(currentConfig.countdownSeconds.toString())
    }
    var allowUnlock by remember(currentConfig.allowUnlock) {
        mutableStateOf(currentConfig.allowUnlock)
    }
    var nightRestEnabled by remember(currentConfig.nightRestEnabled) {
        mutableStateOf(currentConfig.nightRestEnabled)
    }
    var nightStartHour by remember(currentConfig.nightRestStartHour) {
        mutableStateOf(currentConfig.nightRestStartHour.toString())
    }
    var nightStartMinute by remember(currentConfig.nightRestStartMinute) {
        mutableStateOf(currentConfig.nightRestStartMinute.toString())
    }
    var nightEndHour by remember(currentConfig.nightRestEndHour) {
        mutableStateOf(currentConfig.nightRestEndHour.toString())
    }
    var nightEndMinute by remember(currentConfig.nightRestEndMinute) {
        mutableStateOf(currentConfig.nightRestEndMinute.toString())
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("活力卫士") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 状态卡片
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (isServiceRunning)
                        MaterialTheme.colorScheme.primaryContainer
                    else
                        MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = if (isServiceRunning) Icons.Default.CheckCircle else Icons.Default.Info,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = if (isServiceRunning)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.outline
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = if (isServiceRunning) "服务运行中" else "服务已暂停",
                        style = MaterialTheme.typography.titleMedium
                    )
                    if (isServiceRunning) {
                        Text(
                            text = "下次休息: $remainingTime",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(
                        onClick = {
                            if (isServiceRunning) onStopService() else {
                                // 保存配置并启动服务
                                val newConfig = VitalityConfig(
                                    workDurationMinutes = workDuration.toIntOrNull() ?: 60,
                                    restDurationMinutes = restDuration.toIntOrNull() ?: 5,
                                    countdownSeconds = countdownSeconds.toIntOrNull() ?: 10,
                                    nightRestEnabled = nightRestEnabled,
                                    nightRestStartHour = nightStartHour.toIntOrNull() ?: 22,
                                    nightRestStartMinute = nightStartMinute.toIntOrNull() ?: 30,
                                    nightRestEndHour = nightEndHour.toIntOrNull() ?: 7,
                                    nightRestEndMinute = nightEndMinute.toIntOrNull() ?: 0,
                                    allowUnlock = allowUnlock
                                )
                                onConfigChange(newConfig)
                                onStartService()
                            }
                        },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (isServiceRunning)
                                MaterialTheme.colorScheme.error
                            else
                                MaterialTheme.colorScheme.primary
                        )
                    ) {
                        Icon(
                            imageVector = if (isServiceRunning) Icons.Default.Close else Icons.Default.PlayArrow,
                            contentDescription = null
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(if (isServiceRunning) "停止服务" else "保存并启动")
                    }
                }
            }

            // 工作休息设置
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "工作/休息周期",
                        style = MaterialTheme.typography.titleMedium
                    )

                    OutlinedTextField(
                        value = workDuration,
                        onValueChange = { workDuration = it.filter { c -> c.isDigit() } },
                        label = { Text("工作时长（分钟）") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )

                    OutlinedTextField(
                        value = restDuration,
                        onValueChange = { restDuration = it.filter { c -> c.isDigit() } },
                        label = { Text("休息时长（分钟）") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )

                    OutlinedTextField(
                        value = countdownSeconds,
                        onValueChange = { countdownSeconds = it.filter { c -> c.isDigit() } },
                        label = { Text("倒计时（秒）") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                }
            }

            // 解锁选项
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "解锁选项",
                        style = MaterialTheme.typography.titleMedium
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("允许解锁")
                            Text(
                                text = "可通过按钮或按5次返回键解锁",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Switch(
                            checked = allowUnlock,
                            onCheckedChange = { allowUnlock = it }
                        )
                    }
                }
            }

            // 夜间休息设置
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("夜间休息模式")
                            Text(
                                text = "指定时间段内强制休息",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Switch(
                            checked = nightRestEnabled,
                            onCheckedChange = { nightRestEnabled = it }
                        )
                    }

                    if (nightRestEnabled) {
                        HorizontalDivider()

                        Text(
                            text = "开始时间",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            OutlinedTextField(
                                value = nightStartHour,
                                onValueChange = { nightStartHour = it.filter { c -> c.isDigit() } },
                                label = { Text("时") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f),
                                singleLine = true
                            )
                            OutlinedTextField(
                                value = nightStartMinute,
                                onValueChange = { nightStartMinute = it.filter { c -> c.isDigit() } },
                                label = { Text("分") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f),
                                singleLine = true
                            )
                        }

                        Text(
                            text = "结束时间",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            OutlinedTextField(
                                value = nightEndHour,
                                onValueChange = { nightEndHour = it.filter { c -> c.isDigit() } },
                                label = { Text("时") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f),
                                singleLine = true
                            )
                            OutlinedTextField(
                                value = nightEndMinute,
                                onValueChange = { nightEndMinute = it.filter { c -> c.isDigit() } },
                                label = { Text("分") },
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.weight(1f),
                                singleLine = true
                            )
                        }
                    }
                }
            }

            // 关于
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "关于",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "活力卫士 Android 版 v1.0.0\n" +
                                "基于 VitalityGuard 项目适配\n" +
                                "帮助你保持健康的工作/休息节奏",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}