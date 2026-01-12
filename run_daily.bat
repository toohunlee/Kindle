@echo off
REM Daily News Delivery Runner Script for Windows
REM This script activates the virtual environment and runs the main script

echo ================================================
echo Starting Daily News Delivery - %date% %time%
echo ================================================

REM Change to the script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
)

REM Run the main script
python main.py

set EXIT_CODE=%ERRORLEVEL%

echo ================================================
echo Finished - %date% %time%
echo Exit Code: %EXIT_CODE%
echo ================================================

exit /b %EXIT_CODE%
