@echo off
echo =====================================
echo   IgniteRemote EXE Builder (Fixed)
echo =====================================
echo.

echo [1/5] Checking dependencies...
pip install pyinstaller pyautogui websocket-client requests cryptography pillow pystray keyboard psutil pywin32 --quiet --disable-pip-version-check

echo [2/5] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo [3/5] Creating optimized PyInstaller spec...
echo Creating IgniteRemote_Production.spec...

(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['main.py'],
echo     pathex=['%CD%'],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=[
echo         'relay_client',
echo         'websocket',
echo         'websocket._core',
echo         'websocket._handshake',
echo         'websocket._http',
echo         'websocket._logging',
echo         'websocket._socket',
echo         'websocket._ssl_compat',
echo         'websocket._url',
echo         'websocket._utils',
echo         'cryptography',
echo         'cryptography.fernet',
echo         'PIL',
echo         'PIL.Image',
echo         'PIL.ImageTk',
echo         'requests',
echo         'urllib3',
echo         'certifi',
echo         'charset_normalizer',
echo         'idna',
echo         'pyautogui',
echo         'pyscreeze',
echo         'pygetwindow',
echo         'pymsgbox',
echo         'pytweening',
echo         'mouseinfo',
echo         'pystray',
echo         'keyboard',
echo         'psutil',
echo         'win32gui',
echo         'win32con',
echo         'win32api',
echo         'win32clipboard',
echo         'pywintypes',
echo         'pythoncom'
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='IgniteRemote',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon=None
echo ^)
) > IgniteRemote_Production.spec

echo [4/5] Building EXE with all dependencies...
pyinstaller IgniteRemote_Production.spec --clean

if exist "dist\IgniteRemote.exe" (
    echo [5/5] EXE built successfully!
    copy "dist\IgniteRemote.exe" "IgniteRemote.exe" >nul
    echo.
    echo ===================================
    echo   BUILD COMPLETED SUCCESSFULLY!
    echo ===================================
    echo.
    echo Your EXE is ready:
    echo - IgniteRemote.exe ^(Main directory^)
    echo - dist\IgniteRemote.exe ^(Original location^)
    echo.
    echo File size: 
    dir /s IgniteRemote.exe | find "IgniteRemote.exe"
    echo.
    echo The EXE is completely portable and includes:
    echo ✓ All Python dependencies
    echo ✓ WebSocket client libraries  
    echo ✓ Cryptography and security modules
    echo ✓ GUI framework ^(tkinter^)
    echo ✓ Screen capture capabilities
    echo ✓ System tray integration
    echo ✓ Windows API bindings
    echo.
    echo Ready for distribution!
) else (
    echo [ERROR] Build failed! Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo Press any key to exit...
pause >nul
