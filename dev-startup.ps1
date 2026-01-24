# Fantasy Football Analysis - Development Startup Script
# Automatically sets up Python venv, installs dependencies, and starts both servers

# Get the script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$venvPath = Join-Path $scriptDir ".venv"
$requirementsPath = Join-Path $scriptDir "requirements.txt"

Write-Host "=== Fantasy Football Analysis - Setup & Startup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking for Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking for Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Found: Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found! Please install Node.js 16+ from nodejs.org" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists, create if not
if (-Not (Test-Path $venvPath)) {
    Write-Host ""
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "  ✓ Virtual environment created at .venv" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# Upgrade pip, setuptools, and wheel
Write-Host ""
Write-Host "Upgrading pip, setuptools, and wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ pip, setuptools, and wheel upgraded" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to upgrade pip tools" -ForegroundColor Red
    exit 1
}

# Install/Update Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r $requirementsPath --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists in frontend
$frontendPath = Join-Path $scriptDir "frontend"
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-Not (Test-Path $nodeModulesPath)) {
    Write-Host ""
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $frontendPath
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install frontend dependencies" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
} else {
    Write-Host ""
    Write-Host "  ✓ Frontend dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Starting Development Servers ===" -ForegroundColor Cyan
Write-Host ""

# Start Backend in new terminal
Write-Host "Starting backend API server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; .\.venv\Scripts\Activate.ps1; python run_api.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 2

# Start Frontend in new terminal (using cmd.exe to avoid PowerShell execution policy)
Write-Host "Starting frontend dev server..." -ForegroundColor Green
Start-Process cmd.exe -ArgumentList "/k", "cd /d `"$frontendPath`" && npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "Both servers are starting:" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Frontend:    http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop: Press Ctrl+C in each terminal window" -ForegroundColor Gray