@echo off
REM Windows System Security Monitor Uninstaller
REM Copyright (c) Microsoft Corporation

echo Uninstalling Windows System Security Monitor...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator privileges confirmed.
) else (
    echo This operation requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Stop the service
echo Stopping service...
sc stop "WindowsSecurityMonitor" >nul 2>&1

REM Delete the service
echo Removing service registration...
sc delete "WindowsSecurityMonitor" >nul 2>&1

REM Remove from startup
echo Removing startup entry...
reg delete "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" ^
    /v "WindowsSecurityMonitor" /f >nul 2>&1

REM Remove service files
echo Removing service files...
if exist "%ProgramFiles%\WindowsSecurityMonitor" (
    rmdir /S /Q "%ProgramFiles%\WindowsSecurityMonitor" >nul 2>&1
)

REM Remove temporary files
if exist "%TEMP%\sysmonitor.cache" (
    attrib -H -S "%TEMP%\sysmonitor.cache" >nul 2>&1
    del "%TEMP%\sysmonitor.cache" >nul 2>&1
)

if exist "%TEMP%\winsecurity.tmp" (
    del "%TEMP%\winsecurity.tmp" >nul 2>&1
)

echo.
echo Uninstallation completed successfully.
echo Windows System Security Monitor has been removed from the system.
echo.
pause
