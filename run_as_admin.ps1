# Bedrock NBT/DAT Editor - Administrator Mode
# PowerShell Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bedrock NBT/DAT Editor" -ForegroundColor Yellow
Write-Host "Running as Administrator..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️ Script ini membutuhkan hak akses Administrator" -ForegroundColor Yellow
    Write-Host "🔄 Memulai ulang dengan hak akses Administrator..." -ForegroundColor Yellow
    
    # Restart script with admin privileges
    Start-Process PowerShell -ArgumentList "-File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python ditemukan: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python tidak ditemukan!" -ForegroundColor Red
    Write-Host "Pastikan Python sudah terinstall dan ada di PATH" -ForegroundColor Yellow
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}

# Check if main.py exists
if (-not (Test-Path "main.py")) {
    Write-Host "❌ ERROR: File main.py tidak ditemukan!" -ForegroundColor Red
    Write-Host "Pastikan script ini berada di folder yang sama dengan main.py" -ForegroundColor Yellow
    Read-Host "Tekan Enter untuk keluar"
    exit 1
}

# Run the program
Write-Host "🚀 Starting Bedrock NBT/DAT Editor..." -ForegroundColor Green
try {
    python main.py
    Write-Host "✅ Program selesai dengan sukses" -ForegroundColor Green
} catch {
    Write-Host "❌ Program exited with error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Tekan Enter untuk keluar"
