import pystray
from PIL import Image, ImageDraw
import threading
import sys
import os
import tkinter as tk
from i18n import i18n

class SystemTrayIcon:
    def __init__(self, app_name="VitalityGuard", on_quit=None, on_show=None):
        self.app_name = app_name # This is just internal ID now
        self.on_quit = on_quit
        self.on_show = on_show
        self.icon = None
        self.thread = None

    def create_image(self):
        # Create a simple icon image programmatically
        # In a real app, load a .ico or .png file
        width = 64
        height = 64
        color1 = (0, 100, 255)
        color2 = (255, 255, 255)
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.ellipse((width//4, height//4, 3*width//4, 3*height//4), fill=color2)
        
        return image

    def setup_menu(self):
        menu = (
            pystray.MenuItem(i18n.get("tray_menu_settings"), self.action_show),
            pystray.MenuItem(i18n.get("tray_menu_quit"), self.action_quit)
        )
        return menu

    def action_show(self, icon, item):
        if self.on_show:
            self.on_show()

    def action_quit(self, icon, item):
        icon.stop()
        if self.on_quit:
            self.on_quit()

    def run(self):
        image = self.create_image()
        self.icon = pystray.Icon(
            "name",
            image,
            i18n.get("tray_tooltip"),
            menu=self.setup_menu()
        )
        self.icon.run()

    def start_in_thread(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()

    def show_notification(self, title, message):
        if self.icon:
            self.icon.notify(message, title)

if __name__ == "__main__":
    # Test
    def quit_app():
        print("Quitting...")
        sys.exit()

    def show_app():
        print("Showing app...")

    tray = SystemTrayIcon(on_quit=quit_app, on_show=show_app)
    print("Starting tray...")
    tray.run()
