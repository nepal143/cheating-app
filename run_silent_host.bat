@echo off
REM Run bankai silent host without showing console window
REM This uses pythonw.exe instead of python.exe to suppress the console

if exist "D:\ishand folder\cheating app\.venv\Scripts\pythonw.exe" (
    "D:\ishand folder\cheating app\.venv\Scripts\pythonw.exe" bankai_silent_host.py
) else (
    pythonw bankai_silent_host.py
)