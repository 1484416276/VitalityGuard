# VitalityGuard - Anti-Overwork Assistant

[中文](README_zh.md) | [日本語](README_ja.md) | [Français](README_fr.md) | [Deutsch](README_de.md) | [Español](README_es.md) | [한국어](README_ko.md) | [Русский](README_ru.md)

> **"Hearing recent news about sudden deaths from overwork has been heartbreaking. I spent a few days creating this tool, hoping it helps everyone stay healthy."**

**VitalityGuard** is a simple yet powerful anti-overwork tool designed for Windows.

**Simple & Effective**: No complex setup. Just **one single configuration page** to manage your health.

It helps you enforce work/rest cycles and mandatory night rest to prevent health risks caused by prolonged computer use.

### Recent Updates

- Fixed Tcl/Tk version conflict in PyInstaller build
- Improved EXE logging for easier troubleshooting
- Added --self-test for automated positive/negative flow checks
- Moved local tools/tests under .local to avoid GitHub uploads
- Added EXE download link

### Features

- **Work/Rest Cycles**: Customizable work/rest cycles (minutes).
- **Forced Black Screen/Hibernation**: 
  - Enforces a black screen during rest periods.
  - Option to force system hibernation for stricter control.
- **Night Rest Mode**:
  - Mandatory rest period (e.g., 22:30 - 07:00).
  - **Forced Hibernation**: System will be forced to hibernate if turned on during night rest.
- **Modern GUI**: Built with `customtkinter`.
- **Internationalization**: Supports 8 languages (English/Chinese/Japanese/French/German/Spanish/Korean/Russian).
- **Safety Features**:
  - **Optional Unlock During Black Screen**: Button click + press `ESC` 5 times (configurable).

### Installation

Download Windows EXE:

- https://github.com/1484416276/VitalityGuard/releases/latest

1. Ensure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. Configure settings in the GUI.
3. Click "Save & Restart Assistant". The app will minimize to the system tray.
4. Right-click the tray icon to open settings or quit.

---

## Illustrated Tutorial (Windows)

This section is for running the EXE directly, and also applies to `python main.py`.

Screenshots are in [docs/images](docs/images/) (e.g. English: `docs/images/en_US/`).

### 1) First Launch & Settings

1. Run `VitalityGuard.exe`. The settings window should open (check tray if not).
2. **Adjust Durations** (Recommended):
   - Work 60 min / Black screen 5 min / Countdown 10 sec
3. **Night Rest** (Optional):
   - When enabled (default 22:30 - 07:00), the system will force hibernation. Test during the day first!

![Settings window](docs/images/en_US/01-settings-home.png)

### 2) Unlock during black screen (enabled by default)

Setting: `Allow unlock during black screen (button and ESC x5)`

When enabled, you can unlock by:

- Clicking the “Emergency Unlock” button
- Pressing `ESC` 5 times

![Black screen unlock](docs/images/en_US/03-black-screen-unlock.png)

### 3) Save and run in tray

After clicking “Save & Restart Assistant”:

- The window hides (runs in background)
- A tray icon appears

![Tray icon](docs/images/tray.png)

![Tray menu](docs/images/en_US/04-tray-menu.png)

### 4) Config file

Config file: `%APPDATA%\\VitalityGuard\\config.json`

![config.json](docs/images/en_US/06-config-json.png)

---

## FAQ

### EXE exits immediately / no window

VitalityGuard.exe will write logs for troubleshooting. Check:

- `%APPDATA%\\VitalityGuard\\logs\\vitalityguard.log`

### Cannot find tray icon

Windows may hide it under the `^` (hidden tray icons).

### Feedback

Suggestions and Pull Requests are welcome!
If you find any bugs or have ideas for new features, please open an issue.

### Contact

Add me on WeChat:

![WeChat QR](微信二维码.jpg)
