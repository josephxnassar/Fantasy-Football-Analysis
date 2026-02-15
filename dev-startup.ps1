# Fantasy Football Analysis - Development Startup Script
# Automatically sets up uv environment, installs dependencies, and starts both servers

# Get the script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host "=== Fantasy Football Analysis - Setup & Startup ===" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
Write-Host "Checking for uv..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version 2>&1
    Write-Host "  ✓ Found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ uv not found! Please install uv from https://docs.astral.sh/uv/" -ForegroundColor Red
    Write-Host "    Quick install: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
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

# Sync Python dependencies with uv (creates venv automatically)
Write-Host ""
Write-Host "Syncing Python dependencies with uv..." -ForegroundColor Yellow

# Check if venv exists and is valid
$venvValid = $false
if (Test-Path .venv) {
    # A valid venv has pyvenv.cfg
    if (Test-Path .venv/pyvenv.cfg) {
        $venvValid = $true
        Write-Host "  ✓ Existing virtual environment found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Virtual environment corrupted (missing pyvenv.cfg), rebuilding..." -ForegroundColor Yellow
    }
}

# Only recreate venv if it's corrupted or doesn't exist
if (-not $venvValid) {
    # Kill any lingering Python or Node processes that might hold file handles
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Wait for processes to fully terminate
    Start-Sleep -Milliseconds 500
    
    # Remove corrupted venv with multiple retry attempts
    if (Test-Path .venv) {
        $retries = 3
        $success = $false
        for ($i = 1; $i -le $retries; $i++) {
            try {
                Remove-Item -Recurse -Force .venv -ErrorAction Stop
                $success = $true
                break
            } catch {
                if ($i -lt $retries) {
                    Write-Host "    Retry $i/$retries..." -ForegroundColor Gray
                    Start-Sleep -Milliseconds 500
                }
            }
        }
        
        if (-not $success) {
            Write-Host "  ✗ Warning: Could not fully clean venv, proceeding anyway" -ForegroundColor Yellow
        }
    }
}

uv sync
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python dependencies synced" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to sync Python dependencies" -ForegroundColor Red
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

# Start Backend in new terminal (using uv run)
Write-Host "Starting backend API server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; uv run python -m backend.run_api" -WindowStyle Normal

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