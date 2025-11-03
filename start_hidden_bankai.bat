@echo off
echo 🔥 Starting Hidden BANKAI Host...
echo.

cd /d "C:\Users\ashut\Downloads\cheating-app-master\cheating-app-master\cheating app final repo\cheating-app\dist"
start "" WORKING_BANKAI_HOST.exe

echo ✅ Host started in background (no window)
echo.
echo 📋 Checking for session file...
timeout /t 3 /nobreak >nul

cd /d "C:\Users\ashut\Downloads\cheating-app-master\cheating-app-master\cheating app final repo\cheating-app"

if exist "working_session.txt" (
    set /p session_id=<working_session.txt
    echo ✅ SESSION ID: %session_id%
    echo 📱 Use this session ID in your IgniteRemote client
) else (
    echo ⏳ Session file not found yet, check working_session.txt in a moment
)

echo.
echo 🎯 Host is running silently in background
echo 📁 Session ID saved in: working_session.txt
pause