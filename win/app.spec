# -*- mode: python ; coding: utf-8 -*-
import os
import esptool

a = Analysis(
    ['../ivh/app.pyw'],
    pathex=["."],
    binaries=[],
    datas=[
        ('../ivh/resources', 'ivh/resources'),
        ('../ivh/layouts', 'ivh/layouts'),
        ('../ivh/firmware', 'ivh/firmware'),
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
        "sv_ttk",
        "esptool"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

esptool_path = os.path.dirname(esptool.__file__)
targets_path = os.path.join(esptool_path, 'targets')

b = Analysis(
    ['../ivh/flash.py'],
    pathex=["."],
    binaries=[],
    datas=[(targets_path, 'esptool/targets')],
    hiddenimports=[
        "esptool"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyza = PYZ(a.pure)
pyzb = PYZ(b.pure)

exea = EXE(
    pyza,
    a.scripts,
    [],
    name='Invisible Hand',
    icon='../ivh/resources/hand.ico',
    contents_directory='.',
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

exeb = EXE(
    pyzb,
    b.scripts,
    [],
    name='flash',
    contents_directory='.',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exea,
    a.binaries,
    a.datas,
    exeb,
    b.binaries,
    b.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Invisible Hand',
)
