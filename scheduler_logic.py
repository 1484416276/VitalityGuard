import time
import random
from datetime import datetime, timedelta
from config_manager import ConfigManager

class SchedulerLogic:
    """
    调度逻辑核心类
    负责判断当前应该处于什么状态（工作/锁定/关机）
    """
    STATE_WORKING = "working"
    STATE_LOCKED = "locked"

    ACTION_NONE = "none"
    ACTION_LOCK = "lock"
    ACTION_UNLOCK = "unlock"
    ACTION_SHUTDOWN = "shutdown"

    def __init__(self, test_mode=False, mock_curfew=False):
        self.config_manager = ConfigManager()
        self.state = self.STATE_WORKING
        self.next_transition_time = 0
        self.test_mode = test_mode
        self.mock_curfew = mock_curfew
        self._schedule_next_lock() # 初始化下一次锁定时间

    def get_config(self):
        return self.config_manager.get_current_mode_config()

    def reload_config(self):
        """重新加载配置并重置计时器"""
        print("[Scheduler] Reloading configuration...")
        self.config_manager.reload_config()
        
        # If we are in working state, reschedule the next lock based on new config
        # This ensures immediate effect of duration changes.
        # But we should respect time already passed? 
        # User expectation: "I changed to 1 min, it should lock in 1 min from NOW (or sooner)"
        # Simplest approach: Reset the timer from NOW.
        if self.state == self.STATE_WORKING:
            self._schedule_next_lock()
        elif self.state == self.STATE_LOCKED:
            self._schedule_unlock()

    def _schedule_next_lock(self):
        """安排下一次锁定时间"""
        config = self.get_config()
        
        if self.test_mode:
            interval = 10 # 测试模式：10秒
        else:
            # 使用配置的工作时长
            minutes = config.get("work_duration_minutes", 40)
            interval = minutes * 60
            
        self.next_transition_time = time.time() + interval
        print(f"[Scheduler] Next lock scheduled in {interval/60:.2f} minutes (Wait for Start...)")

    def _schedule_unlock(self):
        """安排解锁时间"""
        config = self.get_config()
        
        if self.test_mode:
            duration = 5 # 测试模式：5秒
        else:
            # 使用配置的休眠时长
            minutes = config.get("rest_duration_minutes", 10)
            duration = minutes * 60
            
        self.next_transition_time = time.time() + duration
        print(f"[Scheduler] Unlock scheduled in {duration/60:.2f} minutes at {datetime.fromtimestamp(self.next_transition_time)}")

    def check(self):
        """
        检查当前状态并返回需要执行的动作
        :return: ACTION_NONE, ACTION_LOCK, ACTION_UNLOCK, ACTION_SHUTDOWN
        """
        now = datetime.now()
        current_timestamp = time.time()
        config = self.get_config()

        # 1. 检查夜间休息时间
        is_curfew_time = False
        if config.get("night_sleep_enabled", True):
            start_str = config.get("night_sleep_start", "22:30")
            end_str = config.get("night_sleep_end", "07:00")
            
            try:
                start_h, start_m = map(int, start_str.split(':'))
                end_h, end_m = map(int, end_str.split(':'))
                
                # 构建今天的时间对象
                start_time = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                end_time = now.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                
                # 处理跨天情况 (e.g. 22:30 to 07:00)
                if start_time > end_time:
                    # 如果现在是晚上 (>= start) 或者 凌晨 (< end)
                    if now >= start_time or now < end_time:
                        is_curfew_time = True
                else:
                    # 不跨天 (e.g. 01:00 to 03:00)
                    if start_time <= now < end_time:
                        is_curfew_time = True
                        
            except Exception as e:
                print(f"[Scheduler] Error parsing time: {e}")
                pass # Default to false
        
        if self.mock_curfew:
            print("[Scheduler] MOCK NIGHT REST ACTIVE")
            is_curfew_time = True

        if is_curfew_time:
            return self.ACTION_SHUTDOWN

        # 2. 检查周期性锁定
        if self.state == self.STATE_WORKING:
            if current_timestamp >= self.next_transition_time:
                self.state = self.STATE_LOCKED
                self._schedule_unlock()
                return self.ACTION_LOCK
        
        elif self.state == self.STATE_LOCKED:
            if current_timestamp >= self.next_transition_time:
                self.state = self.STATE_WORKING
                self._schedule_next_lock()
                return self.ACTION_UNLOCK

        return self.ACTION_NONE

