@echo off
REM Quick session checker - shows current active session

cd /d "%~dp0"

if exist "bankai_session.txt" (
    echo.
    echo ===============================
    echo   ACTIVE SESSION FOUND
    echo ===============================
    set /p session_id=<bankai_session.txt
    echo.
    echo Session ID: %session_id%
    echo.
    echo Use this ID in your IgniteRemote client
    echo to connect to this host.
    echo.
    echo ===============================
) else (
    echo.
    echo No active session found.
    echo.
    echo Make sure the silent host is running:
    echo   .\dist\bankai_silent_host.exe
    echo.
)

pause