import argparse
import sys
import logging
import ctypes
import os
from config_manager import ConfigManager, set_runtime_current_mode
from utils.system_ops import set_windows_startup

_SINGLE_INSTANCE_MUTEX = None

def _acquire_single_instance_lock():
    global _SINGLE_INSTANCE_MUTEX
    try:
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\VitalityGuard")
        if not handle:
            return True
        _SINGLE_INSTANCE_MUTEX = handle
        return ctypes.windll.kernel32.GetLastError() != 183
    except Exception:
        return True

def _get_log_file_path():
    base = os.getenv("APPDATA") or os.getcwd()
    log_dir = os.path.join(base, "VitalityGuard", "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = os.getcwd()
    return os.path.join(log_dir, "vitalityguard.log")

def _configure_tk_for_frozen():
    if not getattr(sys, "frozen", False):
        return
    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return
    tcl_dir = os.path.join(meipass, "_tcl_data")
    tk_dir = os.path.join(meipass, "_tk_data")
    os.environ["TCL_LIBRARY"] = tcl_dir
    os.environ["TK_LIBRARY"] = tk_dir
    os.environ["PATH"] = meipass + os.pathsep + os.environ.get("PATH", "")
    try:
        os.add_dll_directory(meipass)
    except Exception:
        pass

def _show_message_box(text, title="VitalityGuard"):
    try:
        ctypes.windll.user32.MessageBoxW(None, text, title, 0x40)
    except Exception:
        pass

def main():
    """
    程序入口
    """
    _configure_tk_for_frozen()

    # 1. Single Instance Check
    if not _acquire_single_instance_lock():
        _show_message_box("VitalityGuard 已在运行（可能在托盘或后台）。")
        sys.exit(0)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', handlers=[
        logging.FileHandler(_get_log_file_path(), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ])

    def _excepthook(exc_type, exc, tb):
        logging.exception("Unhandled exception", exc_info=(exc_type, exc, tb))
        _show_message_box(f"程序异常退出：{exc}\n\n日志：{_get_log_file_path()}", "VitalityGuard")

    sys.excepthook = _excepthook
    try:
        config = ConfigManager().config
        set_windows_startup(bool(config.get("auto_start", False)))
    except Exception as e:
        logging.warning(f"Failed to apply Windows startup setting: {e}")
    set_runtime_current_mode("default")

    parser = argparse.ArgumentParser(description="VitalityGuard - Prevent Sudden Death Assistant")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no actual shutdown)")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode (short intervals)")
    parser.add_argument("--mock-curfew", action="store_true", help="Simulate night rest time (trigger shutdown immediately)")
    
    args = parser.parse_args()

    print("Starting VitalityGuard (防猝死助手)...")
    if args.dry_run:
        print("WARNING: DRY RUN MODE ENABLED (Shutdown will be simulated)")
    if args.test_mode:
        print("WARNING: TEST MODE ENABLED (Intervals are very short)")
    if args.mock_curfew:
        print("WARNING: MOCK NIGHT REST ENABLED")

    from locker import ScreenLockerApp
    app = ScreenLockerApp(test_mode=args.test_mode, dry_run=args.dry_run, mock_curfew=args.mock_curfew)
    try:
        app.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
