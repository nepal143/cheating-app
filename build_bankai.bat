
@echo off
REM build_bankai.bat - build a single-file executable named bankai.exe using PyInstaller
REM This script uses the Python launcher to run PyInstaller as a module so it works
REM even when the PyInstaller script isn't on PATH.

REM Ensure you have PyInstaller and required runtime packages installed:
REM py -3 -m pip install --user pyinstaller websocket-client requests

py -3 -m PyInstaller --onefile --name bankai bankai.py --collect-submodules=websocket --hidden-import=requests

if %ERRORLEVEL% NEQ 0 (
    echo Build failed. Ensure PyInstaller and dependencies are installed and try again.
    exit /b %ERRORLEVEL%
)

echo Build succeeded. Look for dist\bankai.exe
