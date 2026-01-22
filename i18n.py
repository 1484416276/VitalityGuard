import json
import os
import locale

LANG_FILE = "lang.json"

DEFAULT_LANG = "zh_CN"

# Embedded translations to avoid missing file issues
TRANSLATIONS = {
    "zh_CN": {
        "app_title": "VitalityGuard - 防猝死助手",
        "settings_title": "VitalityGuard 配置",
        "current_mode": "当前模式:",
        "save_restart": "保存设置并重启助手",
        "work_duration": "工作时长 (分钟):",
        "rest_duration": "黑屏时长 (分钟):",
        "countdown": "倒计时 (秒, 0为关闭):",
        "allow_interruption": "黑屏期间允许打断",
        "allow_esc_unlock": "允许按 5 次 ESC 解锁",
        "auto_start": "开机自启动",
        "auto_start_failed": "设置开机自启动失败: {error}",
        "night_sleep_enabled": "启用夜间强制休眠（在此时间段无法开机）",
        "start_time": "开始时间 (HH:MM):",
        "end_time": "结束时间 (HH:MM):",
        "new_mode_title": "新建模式",
        "new_mode_prompt": "请输入新模式名称 (英文ID):",
        "error_mode_exists": "该模式名称已存在",
        "error_create_failed": "创建失败",
        "confirm_delete": "确定要删除模式 '{mode}' 吗?",
        "error_delete_last": "至少保留一个模式",
        "success_saved": "配置已保存，助手正在后台运行",
        "error_invalid_input": "输入无效，请输入数字",
        "tray_tooltip": "VitalityGuard (防猝死助手)",
        "tray_menu_settings": "打开设置",
        "tray_menu_quit": "退出",
        "notification_title": "VitalityGuard",
        "notification_started": "防猝死助手已启动，将在后台运行。",
        "countdown_text": "即将进入休息\n{time}",
        "countdown_subtext": "为了您的健康，请休息一下",
        "countdown_skip": "紧急跳过 (Skip)",
        "countdown_noskip": "(此模式下不可跳过)",
        "rest_screen_title": "休息时间",
        "rest_screen_text": "休息时间\n{time}",
        "emergency_unlock": "紧急解锁 (Emergency Unlock)",
        "curfew_text": "夜间休息\n好好休息",
        "curfew_shutdown_hint": "当前处于夜间休息时间，系统将被强制休眠。\n无法在此时间段使用电脑。\n休眠期间您的文件将保持原样，请勿担心。",
        "lock_cancelled": "用户取消了锁定。",
        "language": "语言 / Language:",
        "mode_default": "默认模式",
        "mode_meeting": "会议模式",
        "mode_movie": "观影模式",
        "press_esc_hint": "连按 5 次 ESC 解锁"
    },
    "en_US": {
        "app_title": "VitalityGuard - Anti-Overwork Assistant",
        "settings_title": "VitalityGuard Settings",
        "current_mode": "Current Mode:",
        "save_restart": "Save & Restart Assistant",
        "work_duration": "Work Duration (min):",
        "rest_duration": "Black Screen Duration (min):",
        "countdown": "Countdown (sec, 0=off):",
        "allow_interruption": "Allow Interruption",
        "allow_esc_unlock": "Allow ESC Unlock (5 times)",
        "auto_start": "Start with Windows",
        "auto_start_failed": "Failed to set startup: {error}",
        "night_sleep_enabled": "Enable Night Forced Hibernation (Cannot power on)",
        "start_time": "Start Time (HH:MM):",
        "end_time": "End Time (HH:MM):",
        "new_mode_title": "New Mode",
        "new_mode_prompt": "Enter new mode name (English ID):",
        "error_mode_exists": "Mode name already exists",
        "error_create_failed": "Creation failed",
        "confirm_delete": "Delete mode '{mode}'?",
        "error_delete_last": "Keep at least one mode",
        "success_saved": "Settings saved. Running in background.",
        "error_invalid_input": "Invalid input. Numbers only.",
        "tray_tooltip": "VitalityGuard",
        "tray_menu_settings": "Settings",
        "tray_menu_quit": "Quit",
        "notification_title": "VitalityGuard",
        "notification_started": "VitalityGuard started in background.",
        "countdown_text": "Rest Starting in\n{time}",
        "countdown_subtext": "Take a break for your health",
        "countdown_skip": "Skip",
        "countdown_noskip": "(Cannot skip in this mode)",
        "rest_screen_title": "Rest Time",
        "rest_screen_text": "Rest Time\n{time}",
        "emergency_unlock": "Emergency Unlock",
        "curfew_text": "Night Rest\nSleep Well",
        "curfew_shutdown_hint": "Night Rest active. System forcing hibernation.\nCannot use computer during this time.\nYour files will remain safe during hibernation.",
        "lock_cancelled": "Lock cancelled by user.",
        "language": "Language:",
        "mode_default": "Default",
        "mode_meeting": "Meeting",
        "mode_movie": "Movie",
        "press_esc_hint": "Press ESC 5 times to unlock"
    },
    "ja_JP": {
        "app_title": "VitalityGuard - 過労防止アシスタント",
        "settings_title": "VitalityGuard 設定",
        "current_mode": "現在のモード:",
        "save_restart": "設定を保存して再起動",
        "work_duration": "作業時間 (分):",
        "rest_duration": "休憩時間 (分):",
        "countdown": "カウントダウン (秒, 0=オフ):",
        "allow_interruption": "中断を許可する",
        "allow_esc_unlock": "ESCキー5回で解除を許可",
        "auto_start": "Windows 起動時に自動起動",
        "auto_start_failed": "自動起動の設定に失敗しました: {error}",
        "night_sleep_enabled": "夜間強制休止を有効化 (起動不可)",
        "start_time": "開始時間 (HH:MM):",
        "end_time": "終了時間 (HH:MM):",
        "new_mode_title": "新規モード",
        "new_mode_prompt": "新規モード名を入力 (英語ID):",
        "error_mode_exists": "そのモード名は既に存在します",
        "error_create_failed": "作成に失敗しました",
        "confirm_delete": "モード '{mode}' を削除しますか?",
        "error_delete_last": "少なくとも1つのモードを保持してください",
        "success_saved": "設定が保存されました。バックグラウンドで実行中。",
        "error_invalid_input": "無効な入力です。数字を入力してください。",
        "tray_tooltip": "VitalityGuard (過労防止アシスタント)",
        "tray_menu_settings": "設定を開く",
        "tray_menu_quit": "終了",
        "notification_title": "VitalityGuard",
        "notification_started": "VitalityGuardが起動しました。バックグラウンドで実行中です。",
        "countdown_text": "まもなく休憩です\n{time}",
        "countdown_subtext": "健康のために休憩しましょう",
        "countdown_skip": "スキップ (Skip)",
        "countdown_noskip": "(このモードではスキップできません)",
        "rest_screen_title": "休憩時間",
        "rest_screen_text": "休憩時間\n{time}",
        "emergency_unlock": "緊急解除 (Emergency Unlock)",
        "curfew_text": "夜間休憩\nおやすみなさい",
        "curfew_shutdown_hint": "夜間休憩時間です。システムを強制休止します。\nこの時間帯はPCを使用できません。\n休止中、ファイルはそのまま保持されますのでご安心ください。",
        "lock_cancelled": "ユーザーによってロックがキャンセルされました。",
        "language": "言語 / Language:",
        "mode_default": "デフォルト",
        "mode_meeting": "会議",
        "mode_movie": "映画",
        "press_esc_hint": "ESCキーを5回押して解除"
    }
}

class I18n:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18n, cls).__new__(cls)
            cls._instance.lang = DEFAULT_LANG
            cls._instance.load_lang()
        return cls._instance

    def load_lang(self):
        # Detect system language if not set? 
        # For now simple variable.
        pass

    def set_lang(self, lang_code):
        if lang_code in TRANSLATIONS:
            self.lang = lang_code
            return True
        return False

    def get(self, key, **kwargs):
        text = TRANSLATIONS.get(self.lang, TRANSLATIONS[DEFAULT_LANG]).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except:
                return text
        return text

i18n = I18n()
