# VitalityGuard - Anti-Overwork Assistant

[中文](README_zh.md) | [日本語](README_ja.md)

> **"Hearing recent news about sudden deaths from overwork has been heartbreaking. I spent a few days creating this tool, hoping it helps everyone stay healthy."**

**VitalityGuard** is a desktop health and control tool designed for Windows, aiming to help users manage work/rest cycles and enforce rest during specific times (e.g., night rest).

### Features

- **Work/Rest Cycles**: Default 40 minutes work, 10 minutes rest.
- **Forced Black Screen/Hibernation**: 
  - Enforces a black screen during rest periods.
  - Option to force system hibernation for stricter control.
- **Night Rest Mode**:
  - Mandatory rest period (e.g., 22:30 - 07:00).
  - **Forced Hibernation**: System will be forced to hibernate if turned on during night rest.
- **Strict & Flexible Modes**:
  - **Default Mode**: 40/10 min, strict (cannot skip).
  - **Meeting Mode**: 60/5 min, flexible (allows skip).
  - **Movie Mode**: 120/15 min, flexible.
- **Modern GUI**: Built with `customtkinter`.
- **Internationalization**: Supports English, Chinese, and Japanese.
- **Safety Features**:
  - **Emergency Unlock**: Press `ESC` 5 times to unlock the black screen (configurable).

### Installation

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

### Feedback

Suggestions and Pull Requests are welcome!
If you find any bugs or have ideas for new features, please open an issue.
