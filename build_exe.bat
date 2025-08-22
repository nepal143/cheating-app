@echo off
echo Building IgniteRemote Professional EXE...
echo.

:: Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: Build the EXE
echo Building with PyInstaller...
pyinstaller build_ignite.spec

if exist "dist\IgniteRemote.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo.
    echo EXE Location: dist\IgniteRemote.exe
    echo File size: 
    dir "dist\IgniteRemote.exe" | findstr "IgniteRemote.exe"
    echo.
    echo Ready to share! 🚀
    pause
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the output above for errors.
    pause
)
