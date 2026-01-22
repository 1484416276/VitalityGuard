# VitalityGuard 标准发布（Windows 单文件 EXE + GitHub Actions）

本文档用于把 VitalityGuard 以“标准发布”的方式交付给别人使用：
- 生成 Windows x64 单文件 EXE：`VitalityGuard-vX.Y.Z-windows-x64.exe`
- 推送 Git Tag 自动触发 GitHub Actions 打包
- 自动创建 GitHub Release 并附带校验信息（SHA256）

## 约定

- 版本号使用 Git Tag：`vX.Y.Z`（例如：`v1.0.0`）
- 发布产物命名：`VitalityGuard-vX.Y.Z-windows-x64.exe`
- 发布触发方式：推送 Tag（匹配 `v*`）

## 一、一次性准备（只需做一次）

### 1) 确认仓库忽略规则

发布产物与临时文件不应提交到仓库：
- `dist/`
- `build/`
- `*.spec`

已在 `.gitignore` 中配置。

### 2) 确认 GitHub Actions 工作流已存在

工作流文件：
- `.github/workflows/release-windows.yml`

触发条件：
- push tag：`v*`
- 或手动触发（只会生成 Actions Artifact，不会自动发 Release）

## 二、标准发布流程（推荐：用 Tag 触发自动 Release）

### 1) 确认当前代码已推送到 GitHub

```powershell
git status
git push
```

确保输出包含：
- `working tree clean`
- `Your branch is up to date with 'origin/master'`（或你的主分支名）

### 2) 创建并推送版本 Tag

以 `v1.0.0` 为例：

```powershell
git tag -a v1.0.0 -m "VitalityGuard v1.0.0"
git push origin v1.0.0
```

推送成功后会触发 GitHub Actions：`release-windows`。

### 3) 检查 Actions 与 Release

在 GitHub 仓库页面：
- Actions → 找到 `release-windows` 对应的运行记录
- Releases → 应出现 `VitalityGuard v1.0.0`
- Release Assets 中应包含：`VitalityGuard-v1.0.0-windows-x64.exe`
- Release 文本中应包含 SHA256 校验值

## 三、如果 Tag 早于工作流（需要重新触发一次）

如果你先打了 `v1.0.0`，后面才把工作流推上去，那么 GitHub Actions 不会“自动补跑”。

解决方式：把 `v1.0.0` Tag 重新指向最新提交并强制推送（会再次触发 Actions）。

```powershell
git tag -d v1.0.0
git tag -a v1.0.0 -m "VitalityGuard v1.0.0"
git push --force origin v1.0.0
```

注意：这是“重写 Tag”，若该 Tag 已被别人使用或你已经发布过正式 Release，不建议这么做。更标准的做法是发布一个新版本（例如 `v1.0.1`）。

## 四、本地手动打包（可选，用于你自己验证）

### 1) 安装依赖与打包工具

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

### 2) 生成单文件 EXE（无控制台窗口）

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name VitalityGuard main.py
```

产物位置：
- `dist\VitalityGuard.exe`

你可以将其重命名为发布格式：
- `VitalityGuard-vX.Y.Z-windows-x64.exe`

### 3) 本地验证建议（避免真实休眠/关机）

项目支持参数：
- `--dry-run`：不执行真实休眠/关机动作
- `--test-mode`：缩短周期便于快速验证

控制台版（便于看日志）：

```powershell
python -m PyInstaller --noconfirm --clean --onefile --console --name VitalityGuardConsole main.py
.\dist\VitalityGuardConsole.exe --dry-run --test-mode
```

## 五、发布给别人使用的注意事项

- 单文件 EXE（onefile）首次运行会解压到临时目录，启动会比普通程序慢一些
- 未签名的 EXE 可能触发 Windows SmartScreen/杀软提示，属于常见情况
- Release 页面提供 SHA256，用户可自行校验文件完整性

