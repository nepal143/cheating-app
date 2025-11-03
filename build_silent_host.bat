@echo off
REM Build silent host executable using PyInstaller

echo Building silent bankai host...

python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name bankai_silent_host ^
    --hidden-import=websocket ^
    --hidden-import=_websocket_mask_python ^
    --hidden-import=websocket._abnf ^
    --hidden-import=websocket._app ^
    --hidden-import=websocket._core ^
    --hidden-import=websocket._exceptions ^
    --hidden-import=websocket._handshake ^
    --hidden-import=websocket._http ^
    --hidden-import=websocket._logging ^
    --hidden-import=websocket._socket ^
    --hidden-import=websocket._ssl_compat ^
    --hidden-import=websocket._url ^
    --hidden-import=websocket._utils ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --collect-submodules=websocket ^
    --collect-submodules=requests ^
    bankai_silent_host.py

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Silent host built successfully as dist\bankai_silent_host.exe
echo This executable runs without showing any console window.
echo.
pause