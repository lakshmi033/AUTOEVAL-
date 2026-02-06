# AutoEval+ Quick Setup Script for Windows
# Run this script in PowerShell: .\setup.ps1

Write-Host "🚀 AutoEval+ Setup Script" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.11+ from python.org" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js from nodejs.org" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Setting up Backend..." -ForegroundColor Cyan
Write-Host ""

# Backend Setup
Set-Location "autoeval_backened"

# Remove old venv if exists
if (Test-Path "venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Create new venv
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install requirements
Write-Host "Installing Python dependencies (this may take 10-15 minutes)..." -ForegroundColor Yellow
Write-Host "Please wait..." -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ".."

Write-Host ""
Write-Host "📦 Setting up Frontend..." -ForegroundColor Cyan
Write-Host ""

# Frontend Setup
Set-Location "AUTOEVAL+"

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ".."

Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the project:" -ForegroundColor Cyan
Write-Host "1. Backend: cd autoeval_backened && .\venv\Scripts\Activate.ps1 && python -m uvicorn main:app --reload --port 8000" -ForegroundColor White
Write-Host "2. Frontend: cd AUTOEVAL+ && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Or use VS Code tasks: Ctrl+Shift+P -> Tasks: Run Task" -ForegroundColor Gray

