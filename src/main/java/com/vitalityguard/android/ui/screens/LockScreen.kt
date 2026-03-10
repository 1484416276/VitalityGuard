package com.vitalityguard.android.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * 锁屏界面
 * 对应原 Python 项目的 locker.py 和 countdown_ui.py
 * 在 Android 上显示全屏遮罩，提醒用户休息
 */
@Composable
fun LockScreen(
    remainingSeconds: Int,
    isNightRest: Boolean,
    allowUnlock: Boolean,
    escPressCount: Int,
    onUnlock: () -> Unit
) {
    val mins = remainingSeconds / 60
    val secs = remainingSeconds % 60
    val timeText = String.format("%02d:%02d", mins, secs)

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // 主提示文字
            if (isNightRest) {
                Text(
                    text = "夜间休息时间",
                    color = Color.White,
                    fontSize = 36.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(24.dp))
                Text(
                    text = "请放下手机，好好休息",
                    color = Color(0xFFAAAAAA),
                    fontSize = 18.sp
                )
            } else {
                Text(
                    text = "休息时间",
                    color = Color.White,
                    fontSize = 48.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(32.dp))
                
                // 倒计时显示
                Text(
                    text = timeText,
                    color = Color.White,
                    fontSize = 72.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "让眼睛休息一下吧",
                    color = Color(0xFFAAAAAA),
                    fontSize = 18.sp
                )
            }

            // 解锁按钮
            if (allowUnlock && !isNightRest) {
                Spacer(modifier = Modifier.height(64.dp))
                
                Button(
                    onClick = onUnlock,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF333333)
                    ),
                    modifier = Modifier.padding(horizontal = 32.dp)
                ) {
                    Text(
                        text = "紧急解锁",
                        fontSize = 16.sp,
                        modifier = Modifier.padding(vertical = 8.dp, horizontal = 16.dp)
                    )
                }

                // ESC 计数提示
                if (escPressCount > 0) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "返回键解锁: $escPressCount/5",
                        color = Color(0xFF666666),
                        fontSize = 14.sp
                    )
                }
            }

            // 底部提示
            Spacer(modifier = Modifier.height(32.dp))
            if (allowUnlock && !isNightRest) {
                Text(
                    text = "提示：按5次返回键可解锁",
                    color = Color(0xFF808080),
                    fontSize = 12.sp
                )
            }
        }
    }
}

/**
 * 倒计时界面
 * 在锁定前显示的倒计时提示
 */
@Composable
fun CountdownScreen(
    countdownSeconds: Int,
    canCancel: Boolean,
    onCancel: () -> Unit
) {
    var currentSeconds by remember { mutableStateOf(countdownSeconds) }

    LaunchedEffect(currentSeconds) {
        if (currentSeconds > 0) {
            kotlinx.coroutines.delay(1000)
            currentSeconds--
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = currentSeconds.toString(),
                color = Color.White,
                fontSize = 100.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = "秒后开始休息",
                color = Color(0xFFAAAAAA),
                fontSize = 20.sp
            )
            Text(
                text = "请保存好当前工作",
                color = Color(0xFF888888),
                fontSize = 16.sp
            )

            if (canCancel) {
                Spacer(modifier = Modifier.height(48.dp))
                Button(
                    onClick = onCancel,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF444444)
                    )
                ) {
                    Text("跳过倒计时")
                }
            }
        }
    }
}