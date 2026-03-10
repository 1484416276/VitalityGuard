import pystray
from PIL import Image, ImageDraw
import threading
import sys
import platform
from i18n import i18n
import logging

class SystemTrayIcon:
    def __init__(self, app_name="VitalityGuard", on_quit=None, on_show=None):
        self.app_name = app_name
        self.on_quit = on_quit
        self.on_show = on_show
        self.icon = None
        self.thread = None
        self.last_error = None
        self._running = False

    def create_image(self):
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
        self._running = False
        if self.icon:
            try:
                self.icon.stop()
            except BaseException:
                pass
        if self.on_quit:
            try:
                self.on_quit()
            except BaseException:
                pass

    def run(self):
        try:
            image = self.create_image()
            self.icon = pystray.Icon(
                self.app_name,
                image,
                i18n.get("tray_tooltip"),
                menu=self.setup_menu()
            )
            self._running = True
            
            if platform.system() == "Darwin":
                self.icon.run_detached()
            else:
                self.icon.run()
        except Exception as e:
            self.last_error = str(e)
            logging.exception("System tray failed to start")

    def start_in_thread(self):
        if platform.system() == "Darwin":
            try:
                image = self.create_image()
                self.icon = pystray.Icon(
                    self.app_name,
                    image,
                    i18n.get("tray_tooltip"),
                    menu=self.setup_menu()
                )
                self._running = True
                self.icon.run_detached()
            except Exception as e:
                self.last_error = str(e)
                logging.exception("System tray failed to start")
        else:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()

    def stop(self):
        self._running = False
        if self.icon:
            try:
                self.icon.stop()
            except BaseException:
                pass

    def show_notification(self, title, message):
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                pass

if __name__ == "__main__":
    def quit_app():
        print("Quitting...")
        sys.exit()

    def show_app():
        print("Showing app...")

    tray = SystemTrayIcon(on_quit=quit_app, on_show=show_app)
    print("Starting tray...")
    tray.run()
