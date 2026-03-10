# VitalityGuard for iPad

> 防过劳助手 iPad 版 - 保护你的健康，从合理休息开始

## 简介

VitalityGuard for iPad 是一款专为 iPad 设计的防过劳工具，帮助用户建立健康的工作/休息循环，预防因长时间使用设备而导致的健康问题。

## 功能特性

### 🔔 工作/休息周期
- 自定义工作时长（默认 60 分钟）
- 自定义休息时长（默认 5 分钟）
- 倒计时提醒（默认 10 秒）

### 🌙 夜间休息模式
- 可设置夜间强制休息时段（默认 22:30 - 07:00）
- 夜间自动进入休息状态

### 💪 强制健康任务
休息期间需要完成随机健康任务才能继续：
- 👁️ 眼球转动 - 缓解眼部疲劳
- 👁️ 远近交替 - 训练眼部肌肉
- 👁️ 眨眼放松 - 滋润眼球
- 🚶 颈部伸展 - 放松颈椎
- 💨 深呼吸 - 调节身心

### 🔒 引导式访问支持
- 提供引导式访问开启指引
- 配合系统功能实现设备锁定

### 🌐 多语言支持
- 中文（简体）
- English

## 安装方法

### 方式一：Xcode 编译
1. 克隆仓库
```bash
git clone https://github.com/your-username/VitalityGuard-iPad.git
```

2. 用 Xcode 打开项目
```bash
open VitalityGuard-iPad/VitalityGuard.xcodeproj
```

3. 连接 iPad，选择设备并运行

### 方式二：直接安装 IPA
从 [Releases](https://github.com/your-username/VitalityGuard-iPad/releases) 页面下载 IPA 文件，使用 Xcode 或其他工具安装到设备。

## 使用指南

### 基本设置
1. 打开 App，进入设置页面
2. 配置工作/休息时长
3. 可选：开启夜间休息模式
4. 点击保存，开始工作周期

### 引导式访问（推荐）
为获得最佳强制效果，建议开启引导式访问：
1. 设置 → 辅助功能 → 引导式访问 → 开启
2. 在 App 中连按三次侧边按钮
3. 点击开始，设备将被锁定在此 App

## 技术栈

- Swift 5.0
- SwiftUI
- UserNotifications
- iOS 17.0+

## 致谢

本项目灵感来源于 [VitalityGuard](https://github.com/1484416276/VitalityGuard) Windows 版本。

## 许可证

MIT License

---

⚠️ **免责声明**：本应用仅供健康管理辅助使用，如有身体不适请及时就医。
