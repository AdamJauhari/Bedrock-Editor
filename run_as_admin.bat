@echo off
title Bedrock NBT/DAT Editor - Administrator Mode
echo ========================================
echo Bedrock NBT/DAT Editor
echo Running as Administrator...
echo ========================================

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Pastikan Python sudah terinstall dan ada di PATH
    pause
    exit /b 1
)

:: Run the program as administrator
echo Starting Bedrock NBT/DAT Editor...
python main.py

:: If program exits with error, pause to show error message
if errorlevel 1 (
    echo.
    echo Program exited with error code: %errorlevel%
    pause
)

echo.
echo Program selesai.
pause
