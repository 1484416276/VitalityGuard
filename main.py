import argparse
import sys
import logging
import ctypes
import os
from config_manager import ConfigManager, set_runtime_current_mode
from utils.system_ops import set_windows_startup

_SINGLE_INSTANCE_MUTEX = None

def _acquire_single_instance_lock():
    """
    尝试获取单实例互斥锁；获取失败表示已有实例在运行。
    """
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
    """
    获取日志文件路径（优先使用 APPDATA，其次回落到当前工作目录）。
    """
    base = os.getenv("APPDATA") or os.getcwd()
    log_dir = os.path.join(base, "VitalityGuard", "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = os.getcwd()
    return os.path.join(log_dir, "vitalityguard.log")

class _StreamToLogger:
    """
    将 stdout/stderr 写入 logging，避免打包后丢失 print 输出。
    """
    def __init__(self, logger, level):
        self._logger = logger
        self._level = level
        self._buffer = ""

    def write(self, message):
        if not message:
            return
        self._buffer += str(message)
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self._logger.log(self._level, line.rstrip())

    def flush(self):
        if self._buffer.strip():
            self._logger.log(self._level, self._buffer.rstrip())
        self._buffer = ""

def _configure_logging():
    """
    初始化日志：开发时输出到控制台，打包后仅落盘并接管 stdout/stderr。
    """
    is_frozen = bool(getattr(sys, "frozen", False))
    handlers = [logging.FileHandler(_get_log_file_path(), encoding="utf-8-sig")]
    if not is_frozen:
        handlers.append(logging.StreamHandler(sys.stdout))
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    if is_frozen:
        logger = logging.getLogger("VitalityGuard")
        sys.stdout = _StreamToLogger(logger, logging.INFO)
        sys.stderr = _StreamToLogger(logger, logging.ERROR)

def _find_first_existing_dir(base_dirs, relative_candidates):
    """
    在多个 base_dirs 下按候选相对路径查找第一个存在的目录。
    """
    for base in base_dirs:
        if not base:
            continue
        for rel in relative_candidates:
            path = os.path.join(base, rel)
            if os.path.isdir(path):
                return path
    return None

def _find_dir_containing_file(base_dirs, filename, max_depth=6):
    """
    在多个 base_dirs 下递归查找包含指定文件名的目录。
    """
    for base in base_dirs:
        if not base or not os.path.isdir(base):
            continue
        base = os.path.abspath(base)
        for root, dirnames, filenames in os.walk(base):
            depth = root[len(base):].count(os.sep)
            if depth > max_depth:
                dirnames[:] = []
                continue
            if filename in filenames:
                return root
    return None

def _configure_tk_for_frozen():
    """
    打包后为 Tcl/Tk 显式配置数据目录与 DLL 搜索路径，避免 init.tcl 冲突。
    """
    if not getattr(sys, "frozen", False):
        return
    meipass = getattr(sys, "_MEIPASS", None)
    if not meipass:
        return
    exe_dir = os.path.dirname(getattr(sys, "executable", "") or "") or None
    internal_dir = os.path.join(meipass, "_internal")
    base_dirs = [internal_dir, meipass, exe_dir]

    tcl_dir = _find_first_existing_dir(
        base_dirs,
        [
            "_tcl_data",
            os.path.join("tcl", "tcl8.6"),
            os.path.join("tcl8.6"),
        ],
    )
    tk_dir = _find_first_existing_dir(
        base_dirs,
        [
            "_tk_data",
            os.path.join("tcl", "tk8.6"),
            os.path.join("tk8.6"),
        ],
    )
    if not tcl_dir:
        tcl_dir = _find_dir_containing_file(base_dirs, "init.tcl")
    if not tk_dir:
        tk_dir = _find_dir_containing_file(base_dirs, "tk.tcl")

    if tcl_dir:
        os.environ["TCL_LIBRARY"] = tcl_dir
    if tk_dir:
        os.environ["TK_LIBRARY"] = tk_dir

    path_parts = [p for p in [internal_dir, meipass, exe_dir] if p]
    os.environ["PATH"] = os.pathsep.join(path_parts + [os.environ.get("PATH", "")])

    for d in path_parts:
        try:
            os.add_dll_directory(d)
        except Exception:
            pass

    for candidate_base in path_parts:
        tcl_dll = os.path.join(candidate_base, "tcl86t.dll")
        tk_dll = os.path.join(candidate_base, "tk86t.dll")
        try:
            if os.path.isfile(tcl_dll):
                ctypes.WinDLL(tcl_dll)
            if os.path.isfile(tk_dll):
                ctypes.WinDLL(tk_dll)
        except Exception:
            pass

def _show_message_box(text, title="VitalityGuard"):
    """
    在 Windows 上显示简单的 MessageBox（异常时忽略）。
    """
    try:
        ctypes.windll.user32.MessageBoxW(None, text, title, 0x40)
    except Exception:
        pass

def main():
    """
    程序入口
    """
    _configure_logging()
    logging.info("VitalityGuard starting...")
    logging.info("Log file: %s", _get_log_file_path())
    logging.info("Frozen: %s", bool(getattr(sys, "frozen", False)))
    logging.info("Python: %s", sys.version.replace("\n", " "))

    _configure_tk_for_frozen()

    # 1. Single Instance Check
    if not _acquire_single_instance_lock():
        _show_message_box("VitalityGuard 已在运行（可能在托盘或后台）。")
        sys.exit(0)
    
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
    parser.add_argument("--self-test", action="store_true", help="Run a short GUI self-test and exit")
    
    args = parser.parse_args()

    print("Starting VitalityGuard (防猝死助手)...")
    if args.dry_run:
        print("WARNING: DRY RUN MODE ENABLED (Shutdown will be simulated)")
    if args.test_mode:
        print("WARNING: TEST MODE ENABLED (Intervals are very short)")
    if args.mock_curfew:
        print("WARNING: MOCK NIGHT REST ENABLED")
    if args.self_test:
        print("WARNING: SELF TEST ENABLED (auto actions)")

    from locker import ScreenLockerApp
    app = ScreenLockerApp(test_mode=args.test_mode, dry_run=args.dry_run, mock_curfew=args.mock_curfew)
    try:
        if args.self_test:
            app.start_self_test()
        else:
            app.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
