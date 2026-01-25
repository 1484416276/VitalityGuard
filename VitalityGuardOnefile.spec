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

def _walk_data_files(src_dir, dest_prefix):
    """
    将目录下所有文件递归映射为 PyInstaller datas 列表项。

    返回格式：[(src_path, dest_dir), ...]
    """
    out = []
    for root, _, files in os.walk(src_dir):
        for file_name in files:
            src_path = os.path.join(root, file_name)
            rel_dir = os.path.relpath(root, src_dir)
            dest_dir = os.path.join(dest_prefix, rel_dir) if rel_dir != "." else dest_prefix
            out.append((src_path, dest_dir))
    return out

base_prefix = sys.base_prefix
conda_tcl = os.path.join(base_prefix, "Library", "lib", "tcl8.6")
conda_tk = os.path.join(base_prefix, "Library", "lib", "tk8.6")
has_forced_tcl = os.path.isdir(conda_tcl)
has_forced_tk = os.path.isdir(conda_tk)

forced_datas = []
forced_datas += collect_data_files('customtkinter')
if has_forced_tcl:
    forced_datas += _walk_data_files(conda_tcl, "_tcl_data")
if has_forced_tk:
    forced_datas += _walk_data_files(conda_tk, "_tk_data")

forced_binaries = []
for dll in ("tcl86t.dll", "tk86t.dll"):
    dll_path = os.path.join(base_prefix, "Library", "bin", dll)
    if os.path.isfile(dll_path):
        forced_binaries.append((dll_path, "."))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=forced_binaries,
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

_forced_bin_src = {os.path.normcase(os.path.normpath(src)) for (src, _) in forced_binaries}
_strip_binary_names = {"tcl86t.dll", "tk86t.dll"}
_filtered_bins = []
for dest_name, src_name, typecode in a.binaries:
    if os.path.basename(dest_name).lower() in _strip_binary_names:
        if forced_binaries and os.path.normcase(os.path.normpath(src_name)) not in _forced_bin_src:
            continue
    _filtered_bins.append((dest_name, src_name, typecode))
a.binaries = TOC(_filtered_bins)

_tcl_src_root = os.path.normcase(os.path.normpath(conda_tcl)) if has_forced_tcl else None
_tk_src_root = os.path.normcase(os.path.normpath(conda_tk)) if has_forced_tk else None
_filtered_datas = []
for dest_name, src_name, typecode in a.datas:
    dest_norm = str(dest_name).replace("\\", "/")
    src_norm = os.path.normcase(os.path.normpath(src_name))
    if dest_norm.startswith("_tcl_data/"):
        if _tcl_src_root and not src_norm.startswith(_tcl_src_root):
            continue
    if dest_norm.startswith("_tk_data/"):
        if _tk_src_root and not src_norm.startswith(_tk_src_root):
            continue
    _filtered_datas.append((dest_name, src_name, typecode))
a.datas = TOC(_filtered_datas)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VitalityGuard_v4',
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
