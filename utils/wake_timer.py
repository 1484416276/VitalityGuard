import ctypes
from ctypes import wintypes
import logging
import datetime
import subprocess

class WakeTimer:
    """
    Windows Waitable Timer 封装
    用于设置系统从休眠/睡眠中自动唤醒
    
    Update: 增加 Scheduled Task 作为备份唤醒机制
    """
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.handle = None

    def set_timer(self, seconds):
        """
        设置唤醒定时器
        :param seconds: 多少秒后唤醒
        :return: Boolean 成功与否
        """
        if seconds <= 0:
            return False

        # 1. 尝试使用 WaitableTimer (Primary Method)
        timer_success = self._set_waitable_timer(seconds)
        
        # 2. 尝试使用 Scheduled Task (Backup Method)
        # 这对于休眠唤醒通常更可靠
        task_success = self._set_scheduled_task(seconds)
        
        return timer_success or task_success

    def _set_waitable_timer(self, seconds):
        try:
            # 创建 WaitableTimer
            # CreateWaitableTimerW(lpTimerAttributes, bManualReset, lpTimerName)
            self.handle = self.kernel32.CreateWaitableTimerW(None, True, "PowerZilvWakeTimer")
            
            if not self.handle:
                logging.error(f"Failed to create waitable timer. Error code: {self.kernel32.GetLastError()}")
                return False

            # 设置时间
            # lpDueTime: 100-nanosecond intervals. Negative values indicate relative time.
            # 1 second = 10,000,000 intervals
            delay = int(seconds * 10000000) * -1
            t = ctypes.c_longlong(delay)
            
            # SetWaitableTimer(hTimer, pDueTime, lPeriod, pfnCompletionRoutine, lpArgToCompletionRoutine, fResume)
            # fResume = True 表示系统处于挂起状态时恢复系统
            success = self.kernel32.SetWaitableTimer(
                self.handle, 
                ctypes.byref(t), 
                0, 
                None, 
                None, 
                True # fResume=True (Critical for waking up)
            )

            if not success:
                logging.error(f"Failed to set waitable timer. Error code: {self.kernel32.GetLastError()}")
                self.close()
                return False
                
            logging.info(f"WaitableTimer set successfully for {seconds} seconds.")
            return True
        except Exception as e:
            logging.error(f"Error setting waitable timer: {e}")
            return False

    def _set_scheduled_task(self, seconds):
        """
        创建一个一次性的 Windows 计划任务来唤醒电脑
        """
        try:
            # 计算唤醒时间
            wake_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            # 格式化时间为 HH:mm:ss (schtasks 需要)
            # 注意：schtasks /st 只能精确到分钟 (HH:mm) 或者秒?
            # schtasks 的 /ST 参数通常是 HH:mm，不带秒。这可能不够精确。
            # 但是 /Z 参数（删除任务）很有用。
            # 如果我们只能精确到分钟，那么对于短时间测试可能不准确，但对于实际使用（10分钟）是可以的。
            # 为了更精确，我们可以使用 Powershell 注册任务，但这比较复杂。
            # 让我们尝试使用 PowerShell 的 Register-ScheduledTask 来设置更精确的触发器。
            
            # 但为了简单和兼容性，我们先用 schtasks，稍微提前一点唤醒？或者向后取整。
            # 如果 seconds < 60，schtasks 可能无法设置。
            if seconds < 60:
                logging.warning("Scheduled Task interval too short (<60s), skipping backup wake method.")
                return False
                
            start_time = wake_time.strftime("%H:%M")
            start_date = wake_time.strftime("%d/%m/%Y") # depend on locale? 
            # schtasks /Create /SC ONCE /TN "VitalityGuardWake" /TR "cmd.exe /c echo Waking up" /ST HH:mm /SD dd/mm/yyyy /F /RL HIGHEST
            # 还要确保勾选 "Wake the computer to run this task" -> 这只能通过 XML 或 PowerShell 设置。
            # 简单的 schtasks 命令行默认不开启 "Wake the computer"。
            
            # 所以我们必须使用 PowerShell。
            
            ps_script = f"""
            $Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c echo VitalityGuard Waking Up"
            $Trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddSeconds({seconds}))
            $Settings = New-ScheduledTaskSettingsSet -WakeToRun -Priority 1
            Register-ScheduledTask -TaskName "VitalityGuardWake" -Action $Action -Trigger $Trigger -Settings $Settings -User "System" -Force
            """
            
            # 运行 PowerShell 命令
            # 需要管理员权限。如果当前不是管理员，这会失败。
            # 我们假设用户以管理员运行，或者接受失败。
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, check=True)
            logging.info(f"Scheduled Task 'VitalityGuardWake' set for {seconds}s later.")
            return True
            
        except Exception as e:
            logging.warning(f"Failed to set backup Scheduled Task: {e}")
            return False

    def close(self):
        """释放句柄"""
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None
        
        # 清理计划任务
        try:
            subprocess.run(["schtasks", "/Delete", "/TN", "VitalityGuardWake", "/F"], capture_output=True)
        except:
            pass

    def wait(self):
        """
        等待定时器触发 (阻塞)
        通常不需要调用这个，因为我们会直接去休眠。
        但如果作为测试，可以调用。
        """
        if self.handle:
            self.kernel32.WaitForSingleObject(self.handle, 0xFFFFFFFF)

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    print("Testing WakeTimer creation (Dry Run)...")
    wt = WakeTimer()
    if wt.set_timer(5):
        print("Timer set. Closing handle.")
        wt.close()
    else:
        print("Timer failed.")
