# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import sys

hiddenimports = []
hiddenimports += collect_submodules('pystray')
hiddenimports += collect_submodules('pyautogui')
hiddenimports += collect_submodules('pyscreeze')
hiddenimports += collect_submodules('pygetwindow')
hiddenimports += collect_submodules('mouseinfo')

def _walk_data_files(src_dir, dest_prefix):
    out = []
    for root, _, files in os.walk(src_dir):
        for file_name in files:
            src_path = os.path.join(root, file_name)
            rel_dir = os.path.relpath(root, src_dir)
            dest_dir = os.path.join(dest_prefix, rel_dir) if rel_dir != "." else dest_prefix
            out.append((src_path, dest_dir))
    return out

datas = []
datas += collect_data_files('customtkinter')

base_prefix = sys.base_prefix
conda_tcl = os.path.join(base_prefix, "Library", "lib", "tcl8.6")
conda_tk = os.path.join(base_prefix, "Library", "lib", "tk8.6")
if os.path.isdir(conda_tcl):
    datas += _walk_data_files(conda_tcl, "_tcl_data")
if os.path.isdir(conda_tk):
    datas += _walk_data_files(conda_tk, "_tk_data")

binaries = []
for dll in ("tcl86t.dll", "tk86t.dll"):
    dll_path = os.path.join(base_prefix, "Library", "bin", dll)
    if os.path.isfile(dll_path):
        binaries.append((dll_path, "."))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
