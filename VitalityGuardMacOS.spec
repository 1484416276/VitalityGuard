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
    a.binaries,
    a.datas,
    [],
    name='VitalityGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)
