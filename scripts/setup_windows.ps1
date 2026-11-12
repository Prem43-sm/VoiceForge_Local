# VoiceForge Local - Windows Setup Script
# Run in PowerShell as: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then: .\scripts\setup_windows.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " VoiceForge Local - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Verify Python version
Write-Host "`n[1/9] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  Found: $pythonVersion"

# 2. Create virtual environment
Write-Host "`n[2/9] Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "  Virtual environment already exists." -ForegroundColor Green
}

# 3. Install dependencies
Write-Host "`n[3/9] Installing dependencies..." -ForegroundColor Yellow
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements/core.txt
Write-Host "  Core dependencies installed." -ForegroundColor Green

# 4. Verify FFmpeg
Write-Host "`n[4/9] Checking FFmpeg..." -ForegroundColor Yellow
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpeg) {
    Write-Host "  FFmpeg found at: $($ffmpeg.Source)" -ForegroundColor Green
} else {
    Write-Host "  FFmpeg not found. Please install FFmpeg from https://ffmpeg.org/download.html" -ForegroundColor Red
    Write-Host "  Add ffmpeg.exe to your system PATH." -ForegroundColor Yellow
}

# 5. Verify PyTorch
Write-Host "`n[5/9] Checking PyTorch..." -ForegroundColor Yellow
.venv\Scripts\python -c "import torch; print('  PyTorch:', torch.__version__); print('  CUDA:', torch.cuda.is_available())"

# 6. Create directories
Write-Host "`n[6/9] Creating data directories..." -ForegroundColor Yellow
$dirs = @("data/models", "data/voice_packs", "data/outputs", "data/cache", "data/logs", "config")
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
        Write-Host "  Created: $d"
    }
}

# 7. Initialize database
Write-Host "`n[7/9] Initializing database..." -ForegroundColor Yellow
.venv\Scripts\python -c "
from app.database.connection import init_db
from app.config.settings import get_settings
s = get_settings()
init_db(s.db_path)
print('  Database initialized at:', s.db_path)
"

# 8. Create default config
Write-Host "`n[8/9] Creating default configuration..." -ForegroundColor Yellow
if (-not (Test-Path "config/config.toml")) {
    Copy-Item -Path "config/config.toml.example" -Destination "config/config.toml" -ErrorAction SilentlyContinue
    Write-Host "  Config created." -ForegroundColor Green
} else {
    Write-Host "  Config already exists." -ForegroundColor Green
}

# 9. Run doctor
Write-Host "`n[9/9] Running doctor diagnostics..." -ForegroundColor Yellow
.venv\Scripts\python -m app.cli.main doctor

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Activate venv: .venv\Scripts\Activate.ps1"
Write-Host "  2. Install a TTS model: voiceforge models"
Write-Host "  3. Start the API: voiceforge server"
Write-Host "  4. Launch GUI: python app/main.py"