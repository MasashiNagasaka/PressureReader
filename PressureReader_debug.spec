# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('tkinter')


a = Analysis(
    ['C:\\nagasaka\\AI\\PressureReader\\Project01\\src\\PressureReader.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\nagasaka\\AI\\PressureReader\\Project01\\src\\pr_images', 'pr_images'), ('C:\\nagasaka\\AI\\PressureReader\\Project01\\src\\config', 'config'), ('C:\\nagasaka\\AI\\PressureReader\\Project01\\src\\poppler', 'poppler'), ('C:\\Users\\Z627956\\AppData\\Local\\Programs\\Python\\Python313\\tcl\\tcl8.6', '_tcl_data'), ('C:\\Users\\Z627956\\AppData\\Local\\Programs\\Python\\Python313\\tcl\\tk8.6', '_tk_data')],
    hiddenimports=hiddenimports,
    hookspath=['C:\\nagasaka\\AI\\PressureReader\\Project01\\build_hooks'],
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
    name='PressureReader_debug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir='.\\\\_pressure_tmp',
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\nagasaka\\AI\\PressureReader\\Project01\\src\\PR_logo_2.ico'],
)
