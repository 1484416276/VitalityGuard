import json
import os
import logging

def get_config_dir():
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "VitalityGuard")

def get_config_file_path():
    return os.path.join(get_config_dir(), "config.json")

_RUNTIME_CURRENT_MODE = None

DEFAULT_CONFIG = {
    "language": "zh_CN",
    "current_mode": "default",
    "auto_start": True,
    "auto_update": True,
    "modes": {
        "default": {
            "name": "默认模式",
            "work_duration_minutes": 60,
            "rest_duration_minutes": 5,
            "allow_black_screen_unlock": True,
            "night_sleep_enabled": False,
            "night_sleep_start": "22:30",
            "night_sleep_end": "07:00",
            "countdown_seconds": 10
        }
    }
}

def set_runtime_current_mode(mode_name):
    global _RUNTIME_CURRENT_MODE
    _RUNTIME_CURRENT_MODE = mode_name

def get_runtime_current_mode():
    return _RUNTIME_CURRENT_MODE

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        config_path = get_config_file_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
        except Exception:
            pass

        if not os.path.exists(config_path):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                changed = False
                for k, v in DEFAULT_CONFIG.items():
                    if k not in config:
                        config[k] = v
                        changed = True
                if not isinstance(config.get("modes"), dict):
                    config["modes"] = {}
                    changed = True
                else:
                    if set(config["modes"].keys()) != {"default"}:
                        changed = True
                default_mode = config["modes"].get("default", {})
                merged_default_mode = DEFAULT_CONFIG["modes"]["default"].copy()
                if isinstance(default_mode, dict):
                    merged_default_mode.update(default_mode)
                config["modes"] = {"default": merged_default_mode}
                if config.get("current_mode") != "default":
                    config["current_mode"] = "default"
                    changed = True
                if changed:
                    self.save_config(config)
                return config
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return DEFAULT_CONFIG

    def reload_config(self):
        self.config = self.load_config()
        return self.config

    def save_config(self, config=None):
        if config:
            self.config = config
        
        try:
            config_path = get_config_file_path()
            try:
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
            except Exception:
                pass
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get_current_mode_config(self):
        mode_name = _RUNTIME_CURRENT_MODE or self.config.get("current_mode", "default")
        return self.config["modes"].get(mode_name, DEFAULT_CONFIG["modes"]["default"])

    def set_current_mode(self, mode_name):
        self.config["current_mode"] = "default"
        self.save_config()
        return True

    def update_mode(self, mode_key, new_settings):
        if mode_key != "default":
            return False
        if "default" in self.config.get("modes", {}) and isinstance(new_settings, dict):
            self.config["modes"]["default"].update(new_settings)
            self.save_config()
            return True
        return False

    def add_mode(self, mode_key, settings):
        return False

    def delete_mode(self, mode_key):
        return False
