import json
import os
import logging

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "language": "zh_CN",
    "current_mode": "default",
    "modes": {
        "default": {
            "name": "默认模式",
            "work_duration_minutes": 40,
            "rest_duration_minutes": 10,
            "allow_interruption": False,
            "night_sleep_enabled": True,
            "night_sleep_start": "22:30",
            "night_sleep_end": "07:00",
            "countdown_seconds": 5,
            "allow_esc_unlock": False
        },
        "meeting": {
            "name": "会议模式",
            "work_duration_minutes": 60,
            "rest_duration_minutes": 5,
            "allow_interruption": True,
            "night_sleep_enabled": False,
            "night_sleep_start": "23:00",
            "night_sleep_end": "06:00",
            "countdown_seconds": 10,
            "allow_esc_unlock": True
        },
        "movie": {
            "name": "观影模式",
            "work_duration_minutes": 120,
            "rest_duration_minutes": 15,
            "allow_interruption": True,
            "night_sleep_enabled": True,
            "night_sleep_start": "00:00",
            "night_sleep_end": "08:00",
            "countdown_seconds": 0,
            "allow_esc_unlock": True
        }
    }
}

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
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
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get_current_mode_config(self):
        mode_name = self.config.get("current_mode", "default")
        return self.config["modes"].get(mode_name, DEFAULT_CONFIG["modes"]["default"])

    def set_current_mode(self, mode_name):
        if mode_name in self.config["modes"]:
            self.config["current_mode"] = mode_name
            self.save_config()
            return True
        return False

    def update_mode(self, mode_key, new_settings):
        if mode_key in self.config["modes"]:
            self.config["modes"][mode_key].update(new_settings)
            self.save_config()
            return True
        return False

    def add_mode(self, mode_key, settings):
        if mode_key in self.config["modes"]:
            return False # Already exists
        
        self.config["modes"][mode_key] = settings
        self.save_config()
        return True

    def delete_mode(self, mode_key):
        if mode_key in self.config["modes"]:
            # Prevent deleting the last mode or default if possible, but let's just basic check
            if len(self.config["modes"]) <= 1:
                return False
            
            del self.config["modes"][mode_key]
            
            # If we deleted the current mode, switch to default or first available
            if self.config["current_mode"] == mode_key:
                self.config["current_mode"] = list(self.config["modes"].keys())[0]
                
            self.save_config()
            return True
        return False
