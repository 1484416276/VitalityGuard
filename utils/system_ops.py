import os
import time
import datetime
import pyautogui
import logging
import subprocess
import sys
import platform
from typing import Optional

LAUNCH_AGENT_ID = "com.vitalityguard.app"
LAUNCH_AGENT_PATH = os.path.expanduser(f"~/Library/LaunchAgents/{LAUNCH_AGENT_ID}.plist")

def _get_app_path():
    """获取应用程序路径"""
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(sys.argv[0])

def _create_launch_agent_plist():
    """创建 LaunchAgent plist 文件内容"""
    app_path = _get_app_path()
    
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LAUNCH_AGENT_ID}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
'''
    return plist_content

def set_macos_startup(enabled: bool):
    """设置 macOS 开机自启动"""
    if platform.system() != "Darwin":
        raise RuntimeError("macOS startup is only supported on macOS.")
    
    launch_agents_dir = os.path.dirname(LAUNCH_AGENT_PATH)
    
    if enabled:
        try:
            os.makedirs(launch_agents_dir, exist_ok=True)
            
            plist_content = _create_launch_agent_plist()
            with open(LAUNCH_AGENT_PATH, 'w') as f:
                f.write(plist_content)
            
            subprocess.run(["launchctl", "unload", LAUNCH_AGENT_PATH], 
                         capture_output=True, timeout=5)
            
            subprocess.run(["launchctl", "load", LAUNCH_AGENT_PATH], 
                         capture_output=True, timeout=5)
            
            logging.info(f"LaunchAgent created at {LAUNCH_AGENT_PATH}")
        except Exception as e:
            logging.error(f"Failed to create LaunchAgent: {e}")
            raise
    else:
        try:
            subprocess.run(["launchctl", "unload", LAUNCH_AGENT_PATH], 
                         capture_output=True, timeout=5)
            
            if os.path.exists(LAUNCH_AGENT_PATH):
                os.remove(LAUNCH_AGENT_PATH)
            
            logging.info(f"LaunchAgent removed")
        except Exception as e:
            logging.error(f"Failed to remove LaunchAgent: {e}")
            raise

def is_macos_startup_enabled():
    """检查 macOS 开机自启动是否启用"""
    if platform.system() != "Darwin":
        return False
    
    if not os.path.exists(LAUNCH_AGENT_PATH):
        return False
    
    try:
        result = subprocess.run(
            ["launchctl", "list", LAUNCH_AGENT_ID],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return os.path.exists(LAUNCH_AGENT_PATH)

def set_windows_startup(enabled: bool):
    """Windows 开机自启动（保留兼容性）"""
    if platform.system() == "Darwin":
        return set_macos_startup(enabled)
    
    try:
        import winreg as _winreg
    except Exception:
        raise RuntimeError("Windows startup is only supported on Windows.")
    
    _RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    _APP_RUN_NAME = "VitalityGuard"
    
    exe_path = sys.executable
    lower = exe_path.lower()
    if lower.endswith("\\python.exe"):
        pythonw = exe_path[:-9] + "pythonw.exe"
        if os.path.exists(pythonw):
            exe_path = pythonw

    lower = exe_path.lower()
    if lower.endswith("\\python.exe") or lower.endswith("\\pythonw.exe"):
        script_path = os.path.abspath(sys.argv[0])
        cmd = f"\"{exe_path}\" \"{script_path}\""
    else:
        cmd = f"\"{exe_path}\""

    if enabled:
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, _winreg.KEY_SET_VALUE)
        try:
            _winreg.SetValueEx(key, _APP_RUN_NAME, 0, _winreg.REG_SZ, cmd)
        finally:
            _winreg.CloseKey(key)
        return

    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, _winreg.KEY_SET_VALUE)
    try:
        try:
            _winreg.DeleteValue(key, _APP_RUN_NAME)
        except (FileNotFoundError, OSError):
            pass
    finally:
        _winreg.CloseKey(key)

def is_windows_startup_enabled():
    """Windows 检查开机自启动（保留兼容性）"""
    if platform.system() == "Darwin":
        return is_macos_startup_enabled()
    
    try:
        import winreg as _winreg
    except Exception:
        return False
    
    _RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    _APP_RUN_NAME = "VitalityGuard"
    
    try:
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, _winreg.KEY_READ)
    except OSError:
        return False
    try:
        value, reg_type = _winreg.QueryValueEx(key, _APP_RUN_NAME)
        if reg_type != _winreg.REG_SZ:
            return False
        return bool(value)
    except (FileNotFoundError, OSError):
        return False
    finally:
        _winreg.CloseKey(key)

def save_current_work():
    """
    模拟 Cmd+S 保存当前工作
    """
    logging.info("Attempting to save work...")
    try:
        if platform.system() == "Darwin":
            pyautogui.hotkey('command', 's')
        else:
            pyautogui.hotkey('ctrl', 's')
        time.sleep(1)
        logging.info("Save command sent.")
    except Exception as e:
        logging.error(f"Failed to send save command: {e}")

def force_sleep_api():
    """
    尝试进入睡眠状态 (macOS)
    """
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [DEBUG] Entering force_sleep_api...")
    
    if platform.system() == "Darwin":
        try:
            subprocess.run(["pmset", "sleepnow"], check=True, timeout=10)
            print(f"[{now}] [DEBUG] pmset sleepnow executed")
        except Exception as e:
            print(f"[{now}] [DEBUG] pmset failed: {e}")
    else:
        import ctypes
        try:
            ret = ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            print(f"[{now}] [DEBUG] SetSuspendState returned: {ret}")
        except Exception as e:
            print(f"[{now}] [DEBUG] Failed to call SetSuspendState: {e}")
        
        try:
            ret_os = os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            print(f"[{now}] [DEBUG] rundll32 returned: {ret_os}")
        except Exception as e:
            print(f"[{now}] [DEBUG] rundll32 failed: {e}")

def force_hibernate(dry_run=False):
    """
    强制系统休眠/睡眠
    :param dry_run: 如果为True，则只打印日志不执行休眠
    """
    logging.info("Initiating hibernation/sleep sequence...")
    
    if dry_run:
        logging.info("[DRY RUN] System would hibernate/sleep now.")
        return

    if platform.system() == "Darwin":
        try:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] [DEBUG] Executing: pmset sleepnow")
            
            result = subprocess.run(["pmset", "sleepnow"], capture_output=True, text=True, timeout=10)
            
            ret = result.returncode
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] [DEBUG] pmset sleepnow returned exit code: {ret}")
            if stdout: print(f"[{now}] [DEBUG] stdout: {stdout}")
            if stderr: print(f"[{now}] [DEBUG] stderr: {stderr}")
            
        except Exception as e:
            logging.error(f"Failed to execute sleep: {e}")
    else:
        try:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] [DEBUG] Executing: shutdown /h")
            
            result = subprocess.run("shutdown /h", shell=True, capture_output=True, text=True)
            
            ret = result.returncode
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            now = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] [DEBUG] shutdown /h returned exit code: {ret}")
            if stdout: print(f"[{now}] [DEBUG] stdout: {stdout}")
            if stderr: print(f"[{now}] [DEBUG] stderr: {stderr}")

            failed = (ret != 0) or ("126" in stderr) or ("126" in stdout) or ("没有启用休眠" in stderr) or ("没有启用休眠" in stdout)

            if failed:
                print(f"[{now}] [DEBUG] Shutdown detected as failed. Triggering fallback to Sleep (S3)...")
                force_sleep_api()
            
        except Exception as e:
            logging.error(f"Failed to execute hibernation: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"Platform: {platform.system()}")
    print("Testing save (focus on a text editor)...")
    time.sleep(3)
    save_current_work()
    print("Testing hibernate (dry run)...")
    force_hibernate(dry_run=True)
    print(f"Startup enabled: {is_macos_startup_enabled() if platform.system() == 'Darwin' else is_windows_startup_enabled()}")
