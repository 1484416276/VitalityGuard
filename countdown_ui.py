import tkinter as tk
import time
import threading
import platform
import subprocess
from i18n import i18n

class CountdownWindow:
    def __init__(self, parent_root, duration, allow_cancel=True):
        self.duration = duration
        self.allow_cancel = allow_cancel
        self.cancelled = False
        self.root = None
        self.parent_root = parent_root
        self.time_left = duration

    def _play_beep(self):
        """跨平台蜂鸣声"""
        system = platform.system()
        
        if system == "Darwin":
            try:
                subprocess.run(
                    ["afplay", "/System/Library/Sounds/Ping.aiff"],
                    capture_output=True,
                    timeout=2
                )
            except Exception:
                pass
        elif system == "Windows":
            try:
                import winsound
                winsound.Beep(1000, 200)
            except Exception:
                pass
        else:
            try:
                print('\a', end='', flush=True)
            except Exception:
                pass

    def show(self):
        if self.duration <= 0:
            return True

        try:
            self.root = tk.Toplevel()
        except RuntimeError:
            self.root = tk.Tk()
            
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        
        self.root.title(i18n.get("countdown_text").split('\n')[0])

        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        text = i18n.get("countdown_text", time=self.time_left)
        self.label = tk.Label(self.root, text=text, font=("Helvetica", 100, "bold"), fg="white", bg="black")
        self.label.pack(expand=True)

        subtext = i18n.get("countdown_subtext")
        if not self.allow_cancel:
            subtext += f"\n{i18n.get('countdown_noskip')}"
        
        self.sub_label = tk.Label(self.root, text=subtext, font=("Helvetica", 20), fg="#aaaaaa", bg="black")
        self.sub_label.pack(pady=20)

        if self.allow_cancel:
            self.cancel_btn = tk.Button(self.root, text=i18n.get("countdown_skip"), font=("Helvetica", 16), command=self.cancel, bg="#333333", fg="white", padx=20, pady=10)
            self.cancel_btn.pack(side="bottom", pady=50)

        self.update_timer()
        
        threading.Thread(target=self.play_sound, daemon=True).start()

        if isinstance(self.root, tk.Toplevel):
            self.root.wait_window(self.root)
        else:
            self.root.mainloop()
        
        return not self.cancelled

    def update_timer(self):
        if self.time_left > 0:
            text = i18n.get("countdown_text", time=self.time_left)
            self.label.config(text=text)
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.root.destroy()

    def cancel(self):
        self.cancelled = True
        self.root.destroy()

    def play_sound(self):
        for _ in range(self.duration):
            if self.cancelled:
                break
            
            try:
                if not self.root.winfo_exists():
                    break
            except Exception:
                break

            self._play_beep()
            time.sleep(0.8)

if __name__ == "__main__":
    print("Testing countdown...")
    root = tk.Tk()
    root.withdraw()
    result = CountdownWindow(root, 5, allow_cancel=True).show()
    print(f"Result: {result}")
    root.destroy()
