import os
import time
import datetime
import pyautogui
import logging
import ctypes
import subprocess

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
