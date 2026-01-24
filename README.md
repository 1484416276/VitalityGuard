# VitalityGuard - Anti-Overwork Assistant

[中文](README_zh.md) | [日本語](README_ja.md) | [Français](README_fr.md) | [Deutsch](README_de.md) | [Español](README_es.md) | [한국어](README_ko.md) | [Русский](README_ru.md)

> **"Hearing recent news about sudden deaths from overwork has been heartbreaking. I spent a few days creating this tool, hoping it helps everyone stay healthy."**

**VitalityGuard** is a simple yet powerful anti-overwork tool designed for Windows.

**Simple & Effective**: No complex setup. Just **one single configuration page** to manage your health.

It helps you enforce work/rest cycles and mandatory night rest to prevent health risks caused by prolonged computer use.
 
 github_url : https://github.com/1484416276/VitalityGuard/
 
 ## Illustrated Tutorial (Windows)

This section applies to "Running EXE directly" as well as `python main.py`.

Screenshots are located in [docs/images](docs/images/); English screenshots are in `docs/images/en_US/`.

### 1) Run and Setup

1. Run `VitalityGuard.exe`. The settings window will pop up (if not, check the tray icon).
2. **Set Durations** (Recommended defaults):
   - Work 60 minutes / Black Screen 5 minutes / Countdown 10 seconds
3. **Night Rest** (Optional):
   - When enabled, during the specified period (default 22:30 - 07:00), it will force hibernation. Recommended for personal home computers.

![Settings Home](docs/images/en_US/01-settings-home.png)

### 2) Black Screen (Unlock options)

Config item: `Allow unlock during black screen (button or ESC x5)`

When enabled, both unlock methods are available during the black screen:

- Click the "Emergency Unlock" button
- Press `ESC` 5 times rapidly

![Black Screen Unlock](docs/images/en_US/03-black-screen-unlock.png)

### 3) Minimize to Tray

After clicking "Save & Restart Assistant", the program will hide and show an icon in the system tray.

![Tray Icon](docs/images/tray.png)

### Features

- **Work/Rest Cycles**: Customizable work/rest cycles (minutes).
- **Forced Black Screen/Hibernation**: 
  - Enforces a black screen during rest periods.
  - Option to force system hibernation for stricter control.
- **Night Rest Mode**:
  - Mandatory rest period (default 22:30 - 07:00).
  - **Forced Hibernation**: If turned on during this period, the computer will be immediately forced into hibernation.
- **Modern GUI**: Built with `customtkinter`.
- **Internationalization**: Supports 8 languages (English/Chinese/Japanese/French/German/Spanish/Korean/Russian).
- **Safety Features**:
  - **Optional Unlock During Black Screen**: Unlock via "Emergency Unlock" button or pressing `ESC` 5 times (configurable).

### Installation

Windows EXE Download:

- https://github.com/1484416276/VitalityGuard/releases/latest

1. Ensure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Run the program:
   ```bash
   python main.py
   ```
2. Adjust parameters in the settings window.
3. Click "Save & Restart Assistant". The program will hide and run in the background.
4. Right-click the system tray icon to reopen settings or exit.

Config file path: `%APPDATA%\VitalityGuard\config.json`

![config.json](docs/images/en_US/06-config-json.png)

---

## FAQ

### Tray icon not found

Windows might have collapsed it into the `^` (Hidden Icons) area.

### Feedback & Suggestions

If you have any suggestions or find bugs, feel free to submit an Issue or Pull Request!
Your feedback helps us make VitalityGuard better.

### Contact Author

Scan WeChat QR code to add:

![WeChat QR](微信二维码.jpg)
