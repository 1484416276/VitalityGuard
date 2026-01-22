import argparse
import sys
import logging
import socket
from locker import ScreenLockerApp
from config_manager import ConfigManager, set_runtime_current_mode
from utils.system_ops import set_windows_startup

def is_already_running():
    """
    检查是否已有实例在运行
    使用绑定本地端口的方法来实现单实例锁
    """
    try:
        # Create a socket and bind to a specific port
        # If binding fails, another instance is running
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 12345)) # Port 12345 for VitalityGuard lock
        return s # Keep socket open
    except socket.error:
        return None

def main():
    """
    程序入口
    """
    # 1. Single Instance Check
    lock_socket = is_already_running()
    if not lock_socket:
        print("VitalityGuard is already running! Exiting...")
        # Optional: Bring existing window to front? Hard without UI handle.
        # Just exit for now.
        sys.exit(0)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s',
        stream=sys.stdout
    )
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

    app = ScreenLockerApp(test_mode=args.test_mode, dry_run=args.dry_run, mock_curfew=args.mock_curfew)
    try:
        app.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
