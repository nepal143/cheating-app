@echo off
echo ===============================
echo   Testing IgniteRemote EXE
echo ===============================
echo.

if not exist "IgniteRemote_Fixed.exe" (
    echo ERROR: IgniteRemote_Fixed.exe not found!
    echo Please run the build script first.
    pause
    exit /b 1
)

echo Testing EXE launch...
echo.
echo Starting IgniteRemote_Fixed.exe...
echo ^(The app should open in a few seconds^)
echo.
echo If the app opens successfully with the VS Code-style UI, 
echo the EXE is working correctly!
echo.
echo Press Ctrl+C to stop this test or close the app window.
echo.

start "" "IgniteRemote_Fixed.exe"

echo EXE launched! Check if the application window opened.
echo.
pause
