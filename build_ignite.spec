# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['d:\\ishand folder\\cheating app'],
    binaries=[],
    datas=[
        ('relay_client.py', '.'),
        ('crypto_utils.py', '.'),
        ('optimized_capture.py', '.'),
        ('stealth_manager.py', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'websocket',
        'requests',
        'cryptography',
        'pystray',
        'pyautogui',
        'psutil',
        'keyboard',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'threading',
        'json',
        'base64',
        'zlib',
        'io',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IgniteRemote',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
    version_info=None,
)
