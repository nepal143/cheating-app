@echo off
echo 🔥 Building BANKAI HOST EXE...
echo ===================================

cd /d "C:\Users\ashut\Downloads\cheating-app-master\cheating-app-master\cheating app final repo\cheating-app"

echo 📦 Installing PyInstaller...
py -3 -m pip install pyinstaller

echo 🚀 Building executable...
py -3 -m PyInstaller bankai_final_host.spec --clean

echo ✅ Build complete!
echo 📁 Executable location: dist\BANKAI_HOST.exe

echo.
echo 🎯 Ready to use:
echo    - Run dist\BANKAI_HOST.exe
echo    - Session ID will always be: BANKAI
echo    - Connect with IgniteRemote client using "BANKAI"

pause