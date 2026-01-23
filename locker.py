import tkinter as tk
import tkinter.messagebox as messagebox
import sys
import threading
import time
import random
import logging
from scheduler_logic import SchedulerLogic
from utils.system_ops import save_current_work, force_hibernate
from utils.sound_player import SoundPlayer
from settings_gui import SettingsGUI
from countdown_ui import CountdownWindow
from config_manager import ConfigManager
from i18n import i18n

from system_tray import SystemTrayIcon

class ScreenLockerApp:
    """
    屏幕锁定主程序
    整合UI和调度逻辑，现在使用休眠替代黑屏锁定
    """
    def __init__(self, test_mode=False, dry_run=False, mock_curfew=False):
        self.scheduler = SchedulerLogic(test_mode=test_mode, mock_curfew=mock_curfew)
        self.dry_run = dry_run
        self.test_mode = test_mode
        self.config_manager = ConfigManager()
        self.overlay_window = None # Black screen overlay
        
        # 使用 SettingsGUI 作为主界面
        # Pass quit_callback to handle full exit
        self.gui = SettingsGUI(root_callback=self.start_service, quit_callback=self.quit_app)
        self.root = self.gui.root # 兼容引用

        # System Tray
        self.tray = SystemTrayIcon(on_quit=self.quit_app, on_show=self.show_settings)
        self.check_loop_id = None # Track the after loop ID
        self.root.protocol("WM_DELETE_WINDOW", self._on_root_close)

    def start(self):
        """启动应用 (显示设置界面)"""
        print("Starting GUI...")
        try:
            self.tray.start_in_thread()
        except Exception as e:
            logging.exception("Failed to start tray thread")
        self.root.after(1200, self._verify_tray_ready)
        self.gui.run()

    def start_self_test(self):
        """
        运行简短的 GUI 自检（用于真实运行时的正例/反例覆盖）。

        行为：
        - 反例：写入非法数值并触发保存，验证不会崩溃
        - 正例：写入合法数值并模拟点击“保存并重启助手”，进入后台循环
        - 模拟关闭窗口最小化到托盘、再从托盘显示设置、最后退出
        """
        import tkinter.messagebox as _mb

        def _stub(name):
            def _fn(title=None, message=None, *args, **kwargs):
                try:
                    logging.info("[SELF-TEST] messagebox.%s title=%s message=%s", name, title, message)
                except Exception:
                    pass
                return True
            return _fn

        try:
            _mb.showerror = _stub("showerror")
            _mb.showinfo = _stub("showinfo")
            _mb.showwarning = _stub("showwarning")
        except Exception:
            pass

        try:
            self.tray.start_in_thread()
        except Exception:
            logging.exception("[SELF-TEST] Failed to start tray thread")

        def _negative_case():
            try:
                if hasattr(self.gui, "entry_work_duration_minutes"):
                    self.gui.entry_work_duration_minutes.delete(0, "end")
                    self.gui.entry_work_duration_minutes.insert(0, "not-a-number")
                ok = self.gui.save_settings(show_message=False)
                logging.info("[SELF-TEST] negative save_settings ok=%s", ok)
            except Exception:
                logging.exception("[SELF-TEST] negative case failed")

        def _positive_case():
            try:
                if hasattr(self.gui, "entry_work_duration_minutes"):
                    self.gui.entry_work_duration_minutes.delete(0, "end")
                    self.gui.entry_work_duration_minutes.insert(0, "1")
                if hasattr(self.gui, "entry_rest_duration_minutes"):
                    self.gui.entry_rest_duration_minutes.delete(0, "end")
                    self.gui.entry_rest_duration_minutes.insert(0, "1")
                if hasattr(self.gui, "entry_countdown_seconds"):
                    self.gui.entry_countdown_seconds.delete(0, "end")
                    self.gui.entry_countdown_seconds.insert(0, "0")
                try:
                    self.gui.var_night.set(False)
                    self.gui.toggle_night_settings()
                except Exception:
                    pass

                logging.info("[SELF-TEST] clicking start_app")
                self.gui.start_app()
            except Exception:
                logging.exception("[SELF-TEST] positive case failed")

        def _simulate_close_to_tray():
            try:
                self._on_root_close()
                logging.info("[SELF-TEST] simulated window close (withdraw/iconify)")
            except Exception:
                logging.exception("[SELF-TEST] simulate close failed")

        def _simulate_show_settings():
            try:
                self.show_settings()
                logging.info("[SELF-TEST] simulated show settings via tray callback")
            except Exception:
                logging.exception("[SELF-TEST] simulate show settings failed")

        def _finish_exit():
            logging.info("[SELF-TEST] quitting")
            self.quit_app()

        self.root.after(300, _negative_case)
        self.root.after(900, _positive_case)
        self.root.after(1800, _simulate_close_to_tray)
        self.root.after(2600, _simulate_show_settings)
        self.root.after(3600, _finish_exit)

        self.gui.run()

    def _verify_tray_ready(self):
        if self.tray.last_error:
            try:
                messagebox.showwarning("VitalityGuard", f"托盘启动失败：{self.tray.last_error}\n窗口将保持可见。")
            except Exception:
                pass
            return
        if self.tray.icon is None:
            self.root.after(1200, self._verify_tray_ready)

    def _on_root_close(self):
        if self.tray.icon is None or self.tray.last_error:
            try:
                self.root.iconify()
            except Exception:
                pass
            return
        self.root.withdraw()

    def start_service(self):
        """用户点击开始后，隐藏界面并启动后台服务"""
        print("Service started. Running in background...")
        self.tray.show_notification(i18n.get("notification_title"), i18n.get("notification_started"))
        
        # Reload config and reset timer immediately
        self.config_manager.reload_config()
        self.scheduler.reload_config()
        
        # Cancel existing loop if running to prevent duplicates
        if self.check_loop_id:
            try:
                self.root.after_cancel(self.check_loop_id)
                self.check_loop_id = None
                print("Previous loop cancelled.")
            except Exception as e:
                print(f"Error cancelling loop: {e}")

        # Immediate check to print status
        print("Service Loop Started. Monitoring...")
        self._check_loop()

    def show_settings(self):
        """显示设置界面 (从托盘)"""
        # CTk/Tkinter methods must be called from main thread usually.
        # But tray runs in separate thread.
        # We can use root.after or similar mechanism if needed, 
        # but here we can try deiconify directly if thread safe enough, or queue it.
        # Best practice: use root.after(0, callback)
        self.root.after(0, self._show_settings_main_thread)

    def _show_settings_main_thread(self):
        self.root.deiconify()
        self.root.lift()

    def quit_app(self):
        """完全退出"""
        try:
            print("Exiting application...")
            try:
                self.tray.stop()
            except BaseException:
                pass

            def _do_quit():
                try:
                    self.root.quit()
                except Exception:
                    pass
                try:
                    self.root.destroy()
                except Exception:
                    pass

            try:
                self.root.after(0, _do_quit)
            except Exception:
                _do_quit()
        except BaseException:
            pass

    def _perform_sleep_lock(self):
        """执行强制黑屏锁定 (替代休眠)"""
        config = self.config_manager.get_current_mode_config()
        countdown_sec = config.get("countdown_seconds", 5)
        allow_unlock = bool(config.get("allow_black_screen_unlock", True))

        # 1. 倒计时
        if countdown_sec > 0:
            # 显示全屏倒计时
            proceed = CountdownWindow(self.root, countdown_sec, allow_cancel=allow_unlock).show()
            if not proceed:
                print("Lock cancelled by user.")
                # 重置调度器到工作状态
                self.scheduler.state = SchedulerLogic.STATE_WORKING
                self.scheduler._schedule_next_lock()
                return

        # 2. 计算锁定时间
        now = time.time()
        unlock_time = self.scheduler.next_transition_time
        lock_duration = unlock_time - now
        
        # Check if already locked to prevent duplicate windows
        if self.overlay_window and self.overlay_window.winfo_exists():
            print(f"[{time.strftime('%H:%M:%S')}] Warning: Overlay window already exists. Skipping duplicate lock.")
            return

        if lock_duration < 1:
            lock_duration = 60 # 至少1分钟
            
        print(f"[{time.strftime('%H:%M:%S')}] Initiating Black Screen Lock. Unlocking in {lock_duration:.2f} seconds.")
        
        if self.dry_run:
             print(f"[DRY RUN] Would show black screen for {lock_duration}s")
        else:
             # 3. 启动黑屏遮罩
             self._show_black_screen(lock_duration, allow_unlock)

    def _show_black_screen(self, duration, allow_unlock):
        """显示全屏黑色遮罩"""
        # Create a new Toplevel window for black screen
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.title("Rest Time")
        self.overlay_window.attributes("-fullscreen", True)
        self.overlay_window.attributes("-topmost", True)
        self.overlay_window.configure(bg="black")
        
        # Set localized title
        self.overlay_window.title(i18n.get("rest_screen_title"))

        # Intercept close events
        self.overlay_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        print(f"[{time.strftime('%H:%M:%S')}] Black Screen Created. Duration: {duration}s")

        # Safety Unlock: Press ESC 5 times
        self.esc_press_count = 0
        def on_esc(event):
            if not allow_unlock:
                return

            self.esc_press_count += 1
            print(f"ESC pressed: {self.esc_press_count}/5")
            
            # Update feedback label
            try:
                self.esc_feedback_label.config(text=f"Unlock: {self.esc_press_count}/5")
            except:
                pass

            if self.esc_press_count >= 5:
                print("Emergency ESC unlock triggered.")
                self._close_black_screen()
        
        # Use bind_all to ensure we catch it even if focus is slightly off
        # Also bind <Key> generally to catch any keypress for debugging if needed
        self.overlay_window.bind_all('<Escape>', on_esc)
        
        # Ensure focus is grabbed immediately
        self.overlay_window.focus_set()
        self.overlay_window.focus_force()
        
        # Bind mouse click to force focus as well (in case user clicks somewhere)
        self.overlay_window.bind_all('<Button-1>', lambda e: self.overlay_window.focus_force())

        # Packing Order: Bottom widgets FIRST to ensure they are visible at the bottom
        
        # Hint label (Subtle but visible)
        # Changed color to #808080 for better visibility
        if allow_unlock:
            hint_label = tk.Label(self.overlay_window, text=i18n.get("press_esc_hint"), font=("Microsoft YaHei", 12), fg="#808080", bg="black")
            hint_label.pack(side="bottom", pady=20)
            
            # Add visual feedback label for ESC press
            self.esc_feedback_label = tk.Label(self.overlay_window, text="", font=("Microsoft YaHei", 10), fg="#444444", bg="black")
            self.esc_feedback_label.pack(side="bottom", pady=5)

        # Cancel button if allowed
        if allow_unlock:
            btn_exit = tk.Button(self.overlay_window, text=i18n.get("emergency_unlock"), font=("Microsoft YaHei", 12), command=self._close_black_screen)
            btn_exit.pack(side="bottom", pady=20)

        # Label showing remaining time (Packed last to fill remaining space)
        text = i18n.get("rest_screen_text", time=f"{int(duration)//60:02d}:00")
        label = tk.Label(self.overlay_window, text=text, font=("Microsoft YaHei", 48), fg="white", bg="black")
        label.pack(expand=True)

        # Update loop for timer
        end_time = time.time() + duration
        
        def update_timer():
            try:
                # Check if window is still valid
                if not self.overlay_window or not self.overlay_window.winfo_exists():
                    print("Overlay window does not exist. Stopping timer.")
                    return

                remaining = int(end_time - time.time())
                if remaining <= 0:
                    print(f"[{time.strftime('%H:%M:%S')}] Time is up. Unlocking...")
                    self._close_black_screen()
                    return
                
                # Update label
                mins, secs = divmod(remaining, 60)
                try:
                    text = i18n.get("rest_screen_text", time=f"{mins:02d}:{secs:02d}")
                    label.config(text=text)
                except Exception as e:
                    print(f"Error updating label: {e}")
                
                # Force focus and top
                try:
                    self.overlay_window.attributes("-topmost", True)
                    self.overlay_window.focus_force()
                except Exception as e:
                    print(f"Error focusing window: {e}")
                
                # Check every 100ms
                self.overlay_window.after(100, update_timer)
            except Exception as e:
                print(f"Critical error in update_timer: {e}")
                # Emergency unlock
                self._close_black_screen()

        update_timer()
        
        # Wait for window to close
        try:
            self.root.wait_window(self.overlay_window)
        except Exception as e:
            print(f"Error waiting for window: {e}")
            
        print(f"[{time.strftime('%H:%M:%S')}] Black screen lock finished.")
        # Safety cleanup
        self._close_black_screen()

    def _close_black_screen(self):
        if self.overlay_window:
            try:
                print(f"[{time.strftime('%H:%M:%S')}] Destroying black screen window.")
                self.overlay_window.destroy()
            except Exception as e:
                # If window is already destroyed (e.g. manual close), this might fail
                print(f"[{time.strftime('%H:%M:%S')}] Error destroying overlay window: {e}")
            finally:
                self.overlay_window = None

    def _perform_curfew_sleep(self):
        """夜间休息黑屏"""
        print("Executing Night Rest Black Screen Sequence...")
        save_current_work()
        
        # 夜间休息是一直持续到结束时间的
        # 我们可以复用 _show_black_screen，但是时间不确定
        # 或者我们做一个循环检查
        
        # 简单起见，我们开启黑屏，并在 update_timer 里检查 scheduler 状态
        
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.attributes("-fullscreen", True)
        self.overlay_window.attributes("-topmost", True)
        self.overlay_window.configure(bg="black")
        self.overlay_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Safety Unlock: Press ESC 5 times
        self.esc_press_count = 0
        def on_esc(event):
            self.esc_press_count += 1
            print(f"ESC pressed: {self.esc_press_count}/5")
            if self.esc_press_count >= 5:
                print("Emergency ESC unlock triggered.")
                self._close_black_screen()
        # Use bind_all to ensure we catch it even if focus is slightly off
        self.overlay_window.bind_all('<Escape>', on_esc)
        
        # Hint label (Subtle but visible)
        hint_label = tk.Label(self.overlay_window, text=i18n.get("press_esc_hint"), font=("Microsoft YaHei", 12), fg="#808080", bg="black")
        hint_label.pack(side="bottom", pady=20)
        
        label = tk.Label(self.overlay_window, text=i18n.get("curfew_text"), font=("Microsoft YaHei", 48), fg="white", bg="black")
        label.pack(expand=True)

        def check_curfew():
            # Check if curfew is over
            action = self.scheduler.check()
            if action != SchedulerLogic.ACTION_SHUTDOWN:
                self._close_black_screen()
                return
            
            # Update label to show forced shutdown warning
            label.config(text=i18n.get("curfew_shutdown_hint"))
            
            # Execute forced hibernate logic
            # To avoid spamming, we can check every X seconds or just do it once then wait
            # But user wants "cannot be turned on", so we should sleep immediately.
            # Give a small grace period?
            
            if not self.dry_run:
                 print(f"[{time.strftime('%H:%M:%S')}] Night Rest active. Forcing hibernation...")
                 # We need to run this in a way that doesn't block the UI loop forever, 
                 # but since we are sleeping, blocking is kinda the point.
                 # However, if we block, the window might freeze.
                 # Let's call it, it will return after sleep command is issued.
                 force_hibernate()
                 
                 # After wake up, we are here.
                 print(f"[{time.strftime('%H:%M:%S')}] Woke up from night rest sleep. Checking again...")
                 # Wait a bit before checking again to allow system to stabilize?
                 # Or just continue loop
            else:
                 print(f"[{time.strftime('%H:%M:%S')}] [DRY RUN] Night Rest active. Would hibernate.")

            self.overlay_window.attributes("-topmost", True)
            self.overlay_window.focus_force()
            self.overlay_window.after(5000, check_curfew) # Check every 5s to re-hibernate
            
        check_curfew()
        self.root.wait_window(self.overlay_window)

    def _check_loop(self):
        """定时检查调度器状态"""
        action = self.scheduler.check()
        
        if action == SchedulerLogic.ACTION_LOCK:
            self._perform_sleep_lock()
            
        elif action == SchedulerLogic.ACTION_UNLOCK:
            print(f"[{time.strftime('%H:%M:%S')}] Cycle completed. Back to work.")
            SoundPlayer.play_wake_up_sound()
            
        elif action == SchedulerLogic.ACTION_SHUTDOWN:
            self._perform_curfew_sleep()
            
        if self.dry_run and action == SchedulerLogic.ACTION_SHUTDOWN:
             print("Dry Run Hibernation Complete. Exiting app.")
             sys.exit(0)

        # 每秒检查一次
        # Debug info for user
        if action == SchedulerLogic.ACTION_NONE and self.scheduler.state == SchedulerLogic.STATE_WORKING:
             remaining = int(self.scheduler.next_transition_time - time.time())
             if remaining % 30 == 0: # Print every 30s
                 print(f"[{time.strftime('%H:%M:%S')}] Time until lock: {remaining} seconds")
                 
        self.check_loop_id = self.root.after(1000, self._check_loop)
