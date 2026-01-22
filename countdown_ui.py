import tkinter as tk
from tkinter import ttk
import time
import threading
import winsound
from i18n import i18n

class CountdownWindow:
    def __init__(self, parent_root, duration, allow_cancel=True):
        self.duration = duration
        self.allow_cancel = allow_cancel
        self.cancelled = False
        self.root = None
        self.parent_root = parent_root # Not strictly needed if we use Toplevel correctly
        self.time_left = duration

    def show(self):
        if self.duration <= 0:
            return True

        # Always use Toplevel to avoid messing with main root
        # But we need a root to hang off.
        # If we are called from locker, we have self.root (hidden)
        try:
            self.root = tk.Toplevel()
        except RuntimeError:
            # Fallback if no root exists (testing)
            self.root = tk.Tk()
            
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        
        # Set localized title
        self.root.title(i18n.get("countdown_text").split('\n')[0])

        # Disable closing via X
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # Label
        text = i18n.get("countdown_text", time=self.time_left)
        self.label = tk.Label(self.root, text=text, font=("Microsoft YaHei", 100, "bold"), fg="white", bg="black")
        self.label.pack(expand=True)

        # Subtext
        subtext = i18n.get("countdown_subtext")
        if not self.allow_cancel:
            subtext += f"\n{i18n.get('countdown_noskip')}"
        
        self.sub_label = tk.Label(self.root, text=subtext, font=("Microsoft YaHei", 20), fg="#aaaaaa", bg="black")
        self.sub_label.pack(pady=20)

        # Cancel Button
        if self.allow_cancel:
            self.cancel_btn = tk.Button(self.root, text=i18n.get("countdown_skip"), font=("Microsoft YaHei", 16), command=self.cancel, bg="#333333", fg="white", padx=20, pady=10)
            self.cancel_btn.pack(side="bottom", pady=50)

        # Start timer
        self.update_timer()
        
        # Start sound thread
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
            
            # Thread-safe check for window existence
            # In Tkinter, winfo_exists() might not be strictly thread-safe but is usually okay for read
            # However, calling it after destroy can crash
            try:
                if not self.root.winfo_exists():
                    break
            except Exception:
                break

            try:
                winsound.Beep(1000, 200) # 1000Hz, 200ms
            except:
                pass
            time.sleep(0.8)

if __name__ == "__main__":
    # Test
    print("Testing countdown...")
    # Mock root
    root = tk.Tk()
    root.withdraw()
    result = CountdownWindow(root, 5, allow_cancel=True).show()
    print(f"Result: {result}")
    root.destroy()
