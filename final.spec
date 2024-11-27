# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# Collect additional files for face_recognition (if needed)
datas = collect_data_files('face_recognition_models') + collect_data_files('dlib')

a = Analysis(
    ['final.py'],  # Path to your script
    pathex=[],  # Optional: Add custom paths if needed
    binaries=[],
    datas=datas,  # Include the collected data files
    hiddenimports=['face_recognition', 'dlib', 'cv2'],  # Add dependencies explicitly
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
    name='final',  # Name of the output executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
