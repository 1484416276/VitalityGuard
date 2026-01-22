import customtkinter as ctk
from config_manager import ConfigManager
import tkinter.messagebox
from i18n import i18n

class SettingsGUI:
    def __init__(self, root_callback=None, quit_callback=None):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Init Language
        self.lang = self.config.get("language", "zh_CN")
        i18n.set_lang(self.lang)
        
        self.root_callback = root_callback # Callback to restart app or apply settings
        self.quit_callback = quit_callback

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title(i18n.get("app_title"))
        self.root.geometry("600x700")
        
        # Intercept close button
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()
    
    def on_closing(self):
        # User request: "点击关闭就是最小化到托盘，不需要再提醒"
        # Just withdraw (hide) the window
        self.root.withdraw()

    def create_widgets(self):
        # Language Selection
        self.lang_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.lang_frame.pack(pady=5, padx=20, fill="x", anchor="ne")
        
        self.label_lang = ctk.CTkLabel(self.lang_frame, text=i18n.get("language"))
        self.label_lang.pack(side="left", padx=10)
        
        self.lang_var = ctk.StringVar(value=self.lang)
        self.option_lang = ctk.CTkOptionMenu(self.lang_frame, values=["zh_CN", "en_US", "ja_JP"], variable=self.lang_var, command=self.change_language, width=100)
        self.option_lang.pack(side="left")

        # Title
        self.label_title = ctk.CTkLabel(self.root, text=i18n.get("settings_title"), font=("Roboto", 24))
        self.label_title.pack(pady=10)

        # Mode Selection
        self.mode_frame = ctk.CTkFrame(self.root)
        self.mode_frame.pack(pady=10, padx=20, fill="x")

        self.label_mode = ctk.CTkLabel(self.mode_frame, text=i18n.get("current_mode"))
        self.label_mode.pack(side="left", padx=10)

        self.mode_var = ctk.StringVar(value=self.config.get("current_mode", "default"))
        modes = list(self.config["modes"].keys())
        self.option_mode = ctk.CTkOptionMenu(self.mode_frame, values=modes, variable=self.mode_var, command=self.load_mode_settings)
        self.option_mode.pack(side="left", padx=10)

        # New/Delete Buttons
        self.btn_new_mode = ctk.CTkButton(self.mode_frame, text="+", width=30, command=self.create_new_mode)
        self.btn_new_mode.pack(side="left", padx=5)

        self.btn_del_mode = ctk.CTkButton(self.mode_frame, text="-", width=30, fg_color="red", command=self.delete_current_mode)
        self.btn_del_mode.pack(side="left", padx=5)

        # Settings Container
        self.settings_frame = ctk.CTkFrame(self.root)
        self.settings_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # We will populate settings_frame dynamically
        self.load_mode_settings(self.mode_var.get())

        # Save and Restart Button
        self.btn_start = ctk.CTkButton(self.root, text=i18n.get("save_restart"), command=self.start_app, fg_color="green", height=40, font=("Roboto", 16))
        self.btn_start.pack(pady=20, fill="x", padx=40)

    def change_language(self, lang):
        if lang != self.lang:
            self.lang = lang
            i18n.set_lang(lang)
            # Save immediately
            self.config["language"] = lang
            self.config_manager.save_config(self.config)
            # Reload GUI
            self.reload_gui()

    def reload_gui(self):
        # Destroy all widgets and recreate
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title(i18n.get("app_title"))
        self.create_widgets()

    def start_app(self):
        # Save settings first
        if not self.save_settings(show_message=False):
             return # Save failed

        # Trigger callback (which should restart service or update config)
        if self.root_callback:
            self.root.withdraw() # Hide window
            
            # Use root.after to run the callback logic slightly delayed to ensure UI is hidden first
            # and to allow main loop to process pending events
            self.root.after(100, self.root_callback)

    def refresh_mode_list(self):
        modes = list(self.config["modes"].keys())
        self.option_mode.configure(values=modes)
        self.mode_var.set(self.config.get("current_mode", "default"))
        self.load_mode_settings(self.mode_var.get())

    def create_new_mode(self):
        dialog = ctk.CTkInputDialog(text=i18n.get("new_mode_prompt"), title=i18n.get("new_mode_title"))
        new_mode_key = dialog.get_input()
        
        if not new_mode_key:
            return

        if new_mode_key in self.config["modes"]:
            tkinter.messagebox.showerror("Error", i18n.get("error_mode_exists"))
            return

        # Clone current settings as default for new mode
        current_mode = self.mode_var.get()
        new_settings = self.config["modes"][current_mode].copy()
        new_settings["name"] = new_mode_key
        
        if self.config_manager.add_mode(new_mode_key, new_settings):
            self.config["current_mode"] = new_mode_key
            self.config_manager.set_current_mode(new_mode_key)
            self.refresh_mode_list()
            tkinter.messagebox.showinfo("Success", f"Mode '{new_mode_key}' created")
        else:
            tkinter.messagebox.showerror("Error", i18n.get("error_create_failed"))

    def delete_current_mode(self):
        current_mode = self.mode_var.get()
        if len(self.config["modes"]) <= 1:
            tkinter.messagebox.showerror("Error", i18n.get("error_delete_last"))
            return

        if tkinter.messagebox.askyesno("Confirm", i18n.get("confirm_delete", mode=current_mode)):
            if self.config_manager.delete_mode(current_mode):
                self.config = self.config_manager.config # Reload config to get updated current_mode
                self.refresh_mode_list()
                tkinter.messagebox.showinfo("Success", "Mode deleted")
            else:
                tkinter.messagebox.showerror("Error", "Delete failed")

    def load_mode_settings(self, mode_name):
        # Clear existing widgets in settings_frame
        for widget in self.settings_frame.winfo_children():
            widget.destroy()

        mode_config = self.config["modes"][mode_name]

        # Work Duration
        self.add_entry(i18n.get("work_duration"), "work_duration_minutes", mode_config)
        
        # Rest Duration
        self.add_entry(i18n.get("rest_duration"), "rest_duration_minutes", mode_config)

        # Countdown
        self.add_entry(i18n.get("countdown"), "countdown_seconds", mode_config)

        # Allow Interruption
        self.var_interrupt = ctk.BooleanVar(value=mode_config.get("allow_interruption", False))
        self.chk_interrupt = ctk.CTkCheckBox(self.settings_frame, text=i18n.get("allow_interruption"), variable=self.var_interrupt)
        self.chk_interrupt.pack(pady=5, anchor="w", padx=20)

        # Allow ESC Unlock
        self.var_esc_unlock = ctk.BooleanVar(value=mode_config.get("allow_esc_unlock", False))
        self.chk_esc_unlock = ctk.CTkCheckBox(self.settings_frame, text=i18n.get("allow_esc_unlock"), variable=self.var_esc_unlock)
        self.chk_esc_unlock.pack(pady=5, anchor="w", padx=20)

        # Night Sleep
        self.var_night = ctk.BooleanVar(value=mode_config.get("night_sleep_enabled", True))
        self.chk_night = ctk.CTkCheckBox(self.settings_frame, text=i18n.get("night_sleep_enabled"), variable=self.var_night, command=self.toggle_night_settings)
        self.chk_night.pack(pady=10, anchor="w", padx=20)

        self.night_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.night_frame.pack(fill="x", padx=40)
        
        self.entry_night_start = self.add_entry_to_frame(self.night_frame, i18n.get("start_time"), "night_sleep_start", mode_config)
        self.entry_night_end = self.add_entry_to_frame(self.night_frame, i18n.get("end_time"), "night_sleep_end", mode_config)

        self.toggle_night_settings()

    def add_entry(self, label_text, key, config):
        frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        frame.pack(fill="x", pady=5, padx=20)
        
        label = ctk.CTkLabel(frame, text=label_text, width=150, anchor="w")
        label.pack(side="left")
        
        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(config.get(key, "")))
        entry.pack(side="right", expand=True, fill="x")
        
        # Store reference to retrieve value later
        setattr(self, f"entry_{key}", entry)

    def add_entry_to_frame(self, parent, label_text, key, config):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=2)
        
        label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w")
        label.pack(side="left")
        
        entry = ctk.CTkEntry(frame)
        entry.insert(0, str(config.get(key, "")))
        entry.pack(side="right", expand=True, fill="x")
        
        # Store reference
        setattr(self, f"entry_{key}", entry)
        return entry

    def toggle_night_settings(self):
        if self.var_night.get():
            self.entry_night_start.configure(state="normal")
            self.entry_night_end.configure(state="normal")
        else:
            self.entry_night_start.configure(state="disabled")
            self.entry_night_end.configure(state="disabled")

    def save_settings(self, show_message=True):
        mode_name = self.mode_var.get()
        current_config = self.config["modes"][mode_name]

        try:
            current_config["work_duration_minutes"] = int(self.entry_work_duration_minutes.get())
            current_config["rest_duration_minutes"] = int(self.entry_rest_duration_minutes.get())
            current_config["countdown_seconds"] = int(self.entry_countdown_seconds.get())
            current_config["allow_interruption"] = self.var_interrupt.get()
            current_config["allow_esc_unlock"] = self.var_esc_unlock.get()
            current_config["night_sleep_enabled"] = self.var_night.get()
            current_config["night_sleep_start"] = self.entry_night_start.get()
            current_config["night_sleep_end"] = self.entry_night_end.get()
        except ValueError:
            tkinter.messagebox.showerror("Error", "Invalid numeric input")
            return False

        # Update global config
        self.config["current_mode"] = mode_name
        self.config_manager.save_config(self.config)
        
        if show_message:
            tkinter.messagebox.showinfo("Success", "配置已保存")
        return True

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SettingsGUI()
    app.run()
