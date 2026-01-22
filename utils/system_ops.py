import os
import time
import datetime
import pyautogui
import logging
import ctypes
import subprocess
import sys

try:
    import winreg
except Exception:
    winreg = None

_RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_RUN_NAME = "VitalityGuard"

def _build_startup_command():
    exe_path = sys.executable
    lower = exe_path.lower()
    if lower.endswith("\\python.exe"):
        pythonw = exe_path[:-9] + "pythonw.exe"
        if os.path.exists(pythonw):
            exe_path = pythonw

    lower = exe_path.lower()
    if lower.endswith("\\python.exe") or lower.endswith("\\pythonw.exe"):
        script_path = os.path.abspath(sys.argv[0])
        return f"\"{exe_path}\" \"{script_path}\""

    return f"\"{exe_path}\""

def set_windows_startup(enabled: bool):
    if winreg is None:
        raise RuntimeError("Windows startup is only supported on Windows.")

    if enabled:
        cmd = _build_startup_command()
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.SetValueEx(key, _APP_RUN_NAME, 0, winreg.REG_SZ, cmd)
        finally:
            winreg.CloseKey(key)
        return

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE)
    try:
        try:
            winreg.DeleteValue(key, _APP_RUN_NAME)
        except FileNotFoundError:
            pass
        except OSError:
            pass
    finally:
        winreg.CloseKey(key)

def is_windows_startup_enabled():
    if winreg is None:
        return False
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, winreg.KEY_READ)
    except OSError:
        return False
    try:
        value, reg_type = winreg.QueryValueEx(key, _APP_RUN_NAME)
        if reg_type != winreg.REG_SZ:
            return False
        return bool(value)
    except FileNotFoundError:
        return False
    except OSError:
        return False
    finally:
        winreg.CloseKey(key)

def save_current_work():
    """
    模拟Ctrl+S保存当前工作
    """
    logging.info("Attempting to save work...")
    try:
        # 发送 Ctrl+S
        pyautogui.hotkey('ctrl', 's')
        time.sleep(1) # 等待保存对话框或保存完成
        # 再次发送，以防万一
        # pyautogui.hotkey('ctrl', 's')
        logging.info("Save command sent.")
    except Exception as e:
        logging.error(f"Failed to send save command: {e}")

def force_sleep_api():
    """
    尝试多种方式进入睡眠状态 (S3)
    """
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [DEBUG] Entering force_sleep_api...")
    
    # Method 1: ctypes SetSuspendState
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [DEBUG] Method 1: ctypes SetSuspendState(0, 1, 0)")
    try:
        # Hibernate=0 (Sleep), Force=1 (Force), DisableWakeEvent=0
        ret = ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
        print(f"[{now}] [DEBUG] SetSuspendState returned: {ret}")
    except Exception as e:
        print(f"[{now}] [DEBUG] Failed to call SetSuspendState: {e}")

    # Method 2: rundll32
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [DEBUG] Method 2: rundll32 powrprof.dll,SetSuspendState 0,1,0")
    try:
        ret_os = os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        print(f"[{now}] [DEBUG] rundll32 returned: {ret_os}")
    except Exception as e:
        print(f"[{now}] [DEBUG] rundll32 failed: {e}")

def force_hibernate(dry_run=False):
    """
    强制系统休眠
    :param dry_run: 如果为True，则只打印日志不执行休眠
    """
    logging.info("Initiating hibernation sequence...")
    
    if dry_run:
        logging.info("[DRY RUN] System would hibernate now.")
        return

    # Windows hibernate command
    # /h = hibernate
    try:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [DEBUG] Executing: shutdown /h")
        
        # Use subprocess to capture output because shutdown /h might return 0 even on failure
        # forcing us to check stderr/stdout for error messages.
        result = subprocess.run("shutdown /h", shell=True, capture_output=True, text=True)
        
        ret = result.returncode
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [DEBUG] shutdown /h returned exit code: {ret}")
        if stdout: print(f"[{now}] [DEBUG] stdout: {stdout}")
        if stderr: print(f"[{now}] [DEBUG] stderr: {stderr}")

        # Check for known failure indicators
        # 126 is the error code often printed in text: "此系统上没有启用休眠...(126)"
        # Also check if return code is non-zero
        failed = (ret != 0) or ("126" in stderr) or ("126" in stdout) or ("没有启用休眠" in stderr) or ("没有启用休眠" in stdout)

        if failed:
            print(f"[{now}] [DEBUG] Shutdown detected as failed. Triggering fallback to Sleep (S3)...")
            force_sleep_api()
        else:
            # If it returned 0 and no error text, it might have worked or is in progress.
            # But just in case, if it was instantaneous and we are still here...
            pass
            
    except Exception as e:
        logging.error(f"Failed to execute hibernation: {e}")

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    print("Testing save (focus on a text editor)...")
    time.sleep(3)
    save_current_work()
    print("Testing hibernate (dry run)...")
    force_hibernate(dry_run=True)
