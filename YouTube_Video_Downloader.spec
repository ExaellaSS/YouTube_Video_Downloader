# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['GUI_YouTube.py'],
    pathex=[],
    binaries=[('ffmpeg/bin/ffmpeg.exe', '.')],
    datas=[('resources/icon.ico', 'resources'), ('resources/vk.png', 'resources'), ('resources/telegram.png', 'resources'), ('resources/github.png', 'resources')],
    hiddenimports=[],
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
    name='GUI_YouTube',
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
    icon=['resources\\icon.ico'],
)
