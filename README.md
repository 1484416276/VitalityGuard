# VitalityGuard for Android

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Android-green.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Language-Kotlin-orange.svg" alt="Language">
  <img src="https://img.shields.io/badge/Version-1.2.1-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-red.svg" alt="License">
</p>

**活力卫士 - 防过劳助手 Android版**

## 📱 功能特性

- ⏰ **工作/休息周期管理** - 自定义工作和休息时长，强制提醒
- 🌙 **夜间休息模式** - 设定夜间休息时段，强制休息
- 🔒 **Root锁屏** - 利用Root权限实现强制锁屏（需Root）
- ♿ **无障碍服务** - 拦截按键和手势，防止绕过锁屏
- 🚨 **紧急解锁** - 5次返回键快速解锁（可配置）
- 📞 **通讯穿透** - 锁屏时允许电话、微信、QQ等通讯应用
- 🔔 **通知查看** - 锁屏时可下拉查看通知栏
- ⏱️ **熄屏计时** - 使用WakeLock保持计时器在熄屏时继续运行

## 📥 安装

1. 下载最新APK: [Releases](../../releases)
2. 安装到Android设备（需要开启未知来源）
3. 授予必要权限
4. 开启无障碍服务

## 🔧 系统要求

- Android 7.0 (API 24) 或更高版本
- Root权限（可选，用于强制锁屏功能）

## 📖 使用说明

1. **启动服务** - 点击开关启动监控
2. **配置设置** - 设置工作时长、休息时长、夜间休息时段
3. **保存设置** - 支持热更新，无需重启服务
4. **紧急解锁** - 休息模式下连按5次返回键可解锁

## 🔒 权限说明

| 权限 | 用途 |
|------|------|
| 前台服务 | 保持后台运行 |
| 通知 | 显示状态通知 |
| 开机启动 | 开机自动启动 |
| 唤醒锁 | 熄屏时保持计时 |
| 悬浮窗 | 显示锁屏界面 |
| 无障碍服务 | 拦截按键手势 |

## 🏗️ 编译

```bash
# 克隆仓库
git clone https://github.com/你的用户名/VitalityGuard-Android.git

# 进入项目目录
cd VitalityGuard-Android

# 编译Debug版本
./gradlew assembleDebug

# 编译Release版本
./gradlew assembleRelease
```

## 📝 更新日志

### v1.2.1
- 🔧 修复熄屏时计时器暂停的问题（添加WakeLock）

### v1.2.0
- ✨ 新增电话/微信/QQ等通讯软件穿透白名单
- ✨ 允许锁屏时查看通知栏

### v1.1.3
- 🐛 修复服务状态显示"已暂停"的问题

### v1.1.2
- 🐛 优化协程取消逻辑

### v1.1.1
- 🐛 修复夜间休息结束时不自动解锁的问题

### v1.0.0
- 🎉 首次发布

## 📄 许可证

MIT License

## 🙏 致谢

本项目是 [VitalityGuard](https://github.com/原作者/VitalityGuard) 的Android移植版本。

原始Python/Windows版本请参考 VitalityGuard-master 目录。
