import os
import sys
import time
import json
import argparse
import subprocess

import customtkinter as ctk
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from settings_gui import SettingsGUI
from i18n import i18n


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _try_font(size):
    for name in ("C:\\Windows\\Fonts\\msyh.ttc", "C:\\Windows\\Fonts\\consola.ttf", "C:\\Windows\\Fonts\\arial.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _grab_window(root):
    from PIL import ImageGrab

    root.update_idletasks()
    root.update()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    if w <= 1 or h <= 1:
        root.update_idletasks()
        root.update()
        w = root.winfo_width()
        h = root.winfo_height()
    bbox = (x, y, x + w, y + h)
    return ImageGrab.grab(bbox=bbox)


def _save(img, path):
    img.save(path, format="PNG")


def _render_placeholder(path, title, lines):
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (18, 18, 18))
    draw = ImageDraw.Draw(img)
    title_font = _try_font(40)
    body_font = _try_font(24)
    draw.text((40, 40), title, fill=(240, 240, 240), font=title_font)
    y = 120
    for line in lines:
        draw.text((40, y), line, fill=(200, 200, 200), font=body_font)
        y += 38
    _save(img, path)


def _render_json_image(path, data):
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (18, 18, 18))
    draw = ImageDraw.Draw(img)
    font = _try_font(20)
    title_font = _try_font(36)
    draw.text((40, 30), "config.json 示例（截图占位）", fill=(240, 240, 240), font=title_font)
    s = json.dumps(data, ensure_ascii=False, indent=2)
    y = 90
    for line in s.splitlines():
        draw.text((40, y), line, fill=(210, 210, 210), font=font)
        y += 26
        if y > h - 30:
            break
    _save(img, path)


def _capture_settings_screens(out_dir, lang):
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    gui = SettingsGUI()
    if getattr(gui, "lang", None) != lang:
        try:
            gui.lang = lang
            i18n.set_lang(lang)
            gui.reload_gui()
        except Exception:
            pass

    root = gui.root
    root.deiconify()
    root.lift()
    root.attributes("-topmost", True)
    root.update()
    time.sleep(0.8)

    img = _grab_window(root)
    _save(img, os.path.join(out_dir, "01-settings-home.png"))

    root.update()
    time.sleep(0.6)
    img = _grab_window(root)
    _save(img, os.path.join(out_dir, "02-mode-and-durations.png"))

    try:
        gui.var_black_screen_unlock.set(True)
    except Exception:
        pass
    root.update()
    time.sleep(0.4)

    try:
        gui.var_night.set(True)
        gui.toggle_night_settings()
    except Exception:
        pass
    root.update()
    time.sleep(0.4)
    img = _grab_window(root)
    _save(img, os.path.join(out_dir, "05-night-rest.png"))

    return root


def _capture_black_screen(root, out_dir, lang):
    i18n.set_lang(lang)
    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-topmost", True)
    overlay.configure(bg="black")
    overlay.title(i18n.get("rest_screen_title"))
    overlay.protocol("WM_DELETE_WINDOW", lambda: None)

    hint = tk.Label(overlay, text=i18n.get("press_esc_hint"), font=("Microsoft YaHei", 12), fg="#808080", bg="black")
    hint.pack(side="bottom", pady=20)

    feedback = tk.Label(overlay, text="Unlock: 0/5", font=("Microsoft YaHei", 10), fg="#444444", bg="black")
    feedback.pack(side="bottom", pady=5)

    btn = tk.Button(overlay, text=i18n.get("emergency_unlock"), font=("Microsoft YaHei", 12))
    btn.pack(side="bottom", pady=20)

    label = tk.Label(overlay, text=i18n.get("rest_screen_text", time="04:59"), font=("Microsoft YaHei", 48), fg="white", bg="black")
    label.pack(expand=True)

    overlay.update()
    time.sleep(0.6)

    from PIL import ImageGrab
    img = ImageGrab.grab()
    _save(img, os.path.join(out_dir, "03-black-screen-unlock.png"))

    try:
        overlay.destroy()
    except Exception:
        pass


def _capture_tray_menu(out_dir, delay_seconds):
    from PIL import ImageGrab
    try:
        import winsound
    except Exception:
        winsound = None

    path = os.path.join(out_dir, "04-tray-menu.png")

    print("")
    print("准备截取托盘右键菜单（04-tray-menu.png）")
    print("1) 先确认 VitalityGuard 正在运行，并且托盘图标可见（可能在 ^ 隐藏图标里）")
    print("2) 在倒计时结束前，右键托盘图标打开菜单，并保持菜单不要消失")
    print(f"3) 倒计时 {delay_seconds} 秒后自动截全屏并保存：{path}")
    print("")

    for remaining in range(delay_seconds, 0, -1):
        print(f"倒计时：{remaining}...", flush=True)
        time.sleep(1)

    if winsound:
        try:
            winsound.Beep(900, 180)
        except Exception:
            pass

    img = ImageGrab.grab()
    _save(img, path)
    print("已保存托盘菜单截图：", path)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-tray", action="store_true")
    parser.add_argument("--tray-delay", type=int, default=5)
    parser.add_argument("--only-tray", action="store_true")
    parser.add_argument("--lang", type=str, default="zh_CN")
    parser.add_argument("--all-langs", action="store_true")
    args = parser.parse_args(argv)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_langs = ["zh_CN", "en_US", "ja_JP", "ko_KR", "fr_FR", "de_DE", "es_ES", "ru_RU"]
    langs = all_langs if args.all_langs else [args.lang]

    if args.all_langs:
        for lang in all_langs:
            cmd = [sys.executable, os.path.abspath(__file__), "--lang", lang]
            if args.capture_tray:
                cmd.append("--capture-tray")
                cmd.extend(["--tray-delay", str(args.tray_delay)])
            if args.only_tray:
                cmd.append("--only-tray")
            subprocess.run(cmd, cwd=base, check=False)
        return

    for lang in langs:
        out_dir = os.path.join(base, "docs", "images", lang)
        _ensure_dir(out_dir)

        if args.only_tray:
            _capture_tray_menu(out_dir, max(1, int(args.tray_delay)))
            continue

        root = _capture_settings_screens(out_dir, lang)
        _capture_black_screen(root, out_dir, lang)

        _render_json_image(
            os.path.join(out_dir, "06-config-json.png"),
            {
                "language": lang,
                "current_mode": "default",
                "auto_start": False,
                "modes": {
                    "default": {
                        "name": "默认模式",
                        "work_duration_minutes": 45,
                        "rest_duration_minutes": 5,
                        "countdown_seconds": 5,
                        "allow_black_screen_unlock": True,
                        "night_sleep_enabled": True,
                        "night_sleep_start": "22:30",
                        "night_sleep_end": "07:00",
                    }
                },
            }
        )

        if args.capture_tray:
            _capture_tray_menu(out_dir, max(1, int(args.tray_delay)))
        else:
            title_by_lang = {
                "zh_CN": "托盘菜单截图（占位图）",
                "en_US": "Tray Menu Screenshot Placeholder",
                "ja_JP": "トレイメニュー（プレースホルダー）",
                "ko_KR": "트레이 메뉴(자리표시자)",
                "fr_FR": "Capture du menu de la zone de notification (espace réservé)",
                "de_DE": "Tray-Menü Screenshot (Platzhalter)",
                "es_ES": "Captura del menú de la bandeja (marcador de posición)",
                "ru_RU": "Скриншот меню трея (заглушка)",
            }
            hint_by_lang = {
                "zh_CN": "右键托盘图标并保持菜单不要消失",
                "en_US": "Right-click tray icon and keep menu open",
                "ja_JP": "トレイアイコンを右クリックしてメニューを表示したままにする",
                "ko_KR": "트레이 아이콘을 우클릭해 메뉴를 열어 둡니다",
                "fr_FR": "Clic droit sur l’icône et gardez le menu ouvert",
                "de_DE": "Tray-Symbol rechtsklicken und Menü offen lassen",
                "es_ES": "Clic derecho en el icono y mantén el menú abierto",
                "ru_RU": "Щёлкните правой кнопкой и удерживайте меню открытым",
            }
            _render_placeholder(
                os.path.join(out_dir, "04-tray-menu.png"),
                title_by_lang.get(lang, "Tray Menu Screenshot Placeholder"),
                [
                    "python tools/capture_screenshots.py --capture-tray --lang " + lang,
                    hint_by_lang.get(lang, "Right-click tray icon and keep menu open"),
                ],
            )

        print("Screenshots generated in:", out_dir)
        try:
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()
