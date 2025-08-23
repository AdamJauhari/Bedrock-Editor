@echo off
title Create Administrator Shortcut
echo ========================================
echo Creating Desktop Shortcut for Bedrock Editor
echo (Run as Administrator)
echo ========================================

:: Get current directory
set "CURRENT_DIR=%~dp0"
set "PYTHON_PATH=python.exe"
set "PROGRAM_PATH=%CURRENT_DIR%main.py"

:: Get desktop path
for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP=%%b"

if "%DESKTOP%"=="" (
    echo ERROR: Tidak dapat menemukan folder Desktop
    pause
    exit /b 1
)

:: Create VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\Bedrock NBT Editor (Admin).lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%PYTHON_PATH%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Arguments = "%PROGRAM_PATH%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Bedrock NBT/DAT Editor - Run as Administrator" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%CURRENT_DIR%icon.png,0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WindowStyle = 1 >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

:: Run VBS script
cscript //nologo "%TEMP%\CreateShortcut.vbs"

:: Set shortcut to run as administrator
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Bedrock NBT Editor (Admin).lnk'); $bytes = [System.IO.File]::ReadAllBytes($Shortcut.FullName); $bytes[0x15] = $bytes[0x15] -bor 0x20; [System.IO.File]::WriteAllBytes($Shortcut.FullName, $bytes)}"

:: Clean up
del "%TEMP%\CreateShortcut.vbs"

echo.
echo ✅ Shortcut berhasil dibuat di Desktop!
echo 📍 Lokasi: %DESKTOP%\Bedrock NBT Editor (Admin).lnk
echo.
echo 🎯 Cara menggunakan:
echo    1. Double-click shortcut di Desktop
echo    2. Klik "Yes" pada dialog UAC
echo    3. Program akan berjalan dengan hak akses Administrator
echo.
pause
