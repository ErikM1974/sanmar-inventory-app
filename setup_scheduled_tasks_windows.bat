@echo off
REM Setup scheduled task for daily SanMar inventory and pricing import
REM This script creates a Windows scheduled task to run the import script at 7 AM every day

echo Setting up scheduled task for daily SanMar inventory and pricing import...

REM Get the current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%daily_inventory_pricing_import.py

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in the PATH. Please install Python and try again.
    exit /b 1
)

REM Create the scheduled task
schtasks /create /tn "SanMar Daily Import" /tr "python %SCRIPT_PATH%" /sc daily /st 07:00 /ru SYSTEM /f

if %ERRORLEVEL% equ 0 (
    echo Scheduled task created successfully.
    echo The import script will run at 7 AM every day.
) else (
    echo Failed to create scheduled task. Please run this script as administrator.
)

echo.
echo You can view and modify the task in Task Scheduler.
echo.

pause