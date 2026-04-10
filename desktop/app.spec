# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.pyw'],
    pathex=["."],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('layouts', 'layouts'),
    ],
    hiddenimports=[
        "os",
        "serial",
        "pathlib",
        "re",
        "json",
        "sys",
        "threading",
        "tkinter",
        "tkinter.ttk",
        "collections",
        "platformdirs",
        "formation",
        "sv_ttk"
    ],
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
    name='Invisible Hand',
    icon='resources/hand.ico',
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
    version='version.txt',
)
