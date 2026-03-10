# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from PyInstaller.building.datastruct import TOC
import os
import sys

hiddenimports = []
hiddenimports += collect_submodules('pystray')
hiddenimports += collect_submodules('pyautogui')
hiddenimports += collect_submodules('pyscreeze')
hiddenimports += collect_submodules('pygetwindow')
hiddenimports += collect_submodules('mouseinfo')
hiddenimports += collect_submodules('pyobjc')
hiddenimports += collect_submodules('pyobjc_core')
hiddenimports += collect_submodules('objc')

forced_datas = []
forced_datas += collect_data_files('customtkinter')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=forced_datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VitalityGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VitalityGuard',
)

app = BUNDLE(
    coll,
    name='VitalityGuard.app',
    icon=None,
    bundle_identifier='com.vitalityguard.app',
    version='1.0.3',
    info_plist={
        'CFBundleName': 'VitalityGuard',
        'CFBundleDisplayName': 'VitalityGuard',
        'CFBundleIdentifier': 'com.vitalityguard.app',
        'CFBundleVersion': '1.0.3',
        'CFBundleShortVersionString': '1.0.3',
        'CFBundleExecutable': 'VitalityGuard',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'NSPrincipalClass': 'NSApplication',
        'LSUIElement': True,
    },
)
